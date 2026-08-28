import sys
# this avoids:
# ValueError: Key backend: 'module://matplotlib_inline.backend_inline' is not a valid value for backend; supported values are [...]
# Although not 100% why, it has two effects:
#  1. PyInstaller picks it up as a module to include
#  2. It registers the backend, maybe earlier than it would be otherwise
import matplotlib_inline
import matplotlib_inline.backend_inline

# We still see the above error on CI on jdaviz, and the PyInstaller
# output recommends the following:
import matplotlib
matplotlib.use("module://matplotlib_inline.backend_inline")
# since matplotlib 3.9 (see https://github.com/matplotlib/matplotlib/pull/27948),
# it seems that matplotlib_inline.backend_inline is an alias for inline
# so we make sure to communicate that to PyInstaller
matplotlib.use("inline")
from pathlib import Path
import os
from urllib.parse import unquote, urlparse

import jdaviz.cli
from datetime import datetime



def _normalize_macos_path(arg):
    if not arg:
        return None
    candidate = str(arg).strip()
    if candidate.startswith("file://"):
        parsed = urlparse(candidate)
        candidate = unquote(parsed.path)
    elif candidate.startswith("~/"):
        candidate = str(Path.home() / candidate[2:])
    elif candidate.startswith("-psn_"):
        return None
    elif candidate.startswith("-"):
        return None
    if candidate and os.path.exists(candidate):
        return candidate
    if candidate and candidate.startswith("/"):
        return candidate
    return None


def _save_open_files(filepaths):
    uniq = []
    seen = set()
    for filepath in filepaths:
        normalized = _normalize_macos_path(filepath)
        if normalized is None or normalized in seen:
            continue
        uniq.append(normalized)
        seen.add(normalized)
    if uniq:
        print(os.pathsep.join(uniq))
        os.environ['JDAVIZ_OPEN_FILES'] = os.pathsep.join(uniq)
    return uniq

def _install_macos_open_files_handler():
    """Register the real Finder open-file callback used by macOS .app bundles.

    Finder sends open-document events through AppKit, not argv, for free-standing macOS
    apps. Registering a Cocoa open-files handler ensures the actual file path reaches the
    Python process before multiprocessing spawns worker processes.
    """
    if sys.platform != "darwin" or not getattr(sys, "frozen", False):
        return

    try:
        import AppKit
    except Exception:
        return

    nsapp = AppKit.NSApplication.sharedApplication()

    def _open_files_handler(filenames):
        paths = _save_open_files(filenames)
        if paths:
            for path in paths:
                if path not in sys.argv:
                    sys.argv.append(path)
        return None

    try:
        nsapp.setOpenFilesHandler_(_open_files_handler)
    except Exception:
        try:
            from Foundation import NSObject

            class _FinderOpenFilesDelegate(NSObject):
                def applicationOpenFiles_(self, _sender, filenames):
                    paths = _save_open_files(filenames)
                    for path in paths:
                        if path not in sys.argv:
                            sys.argv.append(path)
                    return True

            delegate = _FinderOpenFilesDelegate.alloc().init()
            nsapp.setDelegate_(delegate)
        except Exception:
            pass


def _register_macos_finder_filepaths():
    """Store Finder-opened file paths for the CLI before multiprocessing boots."""
    if sys.platform != "darwin" or not getattr(sys, "frozen", False):
        return

    _install_macos_open_files_handler()

    candidates = list(sys.argv[1:])
    try:
        from Foundation import NSProcessInfo
    except Exception:
        NSProcessInfo = None
    if NSProcessInfo is not None:
        candidates.extend(str(arg) for arg in NSProcessInfo.processInfo().arguments()[1:])

    _save_open_files(candidates)


def detect_fileformat(filepath):

    try:
        from jdaviz.configs.deconfigged.helper import App as DeconfiggedHelper
        from jdaviz.core.loaders.resolvers.file.file import PresetFileResolver
        from jdaviz.core.registries import (loader_parser_registry, loader_importer_registry)
    except Exception:
        return []
   
    labels = []
    
    try:
        helper = DeconfiggedHelper()
        try:
            resolver = PresetFileResolver(filepath, app=helper._app)
        except Exception:
            try:
                resolver = PresetFileResolver.from_input(app=helper._app, inp=filepath)
            except Exception:
                resolver = None

        parser_input = None
        if resolver is not None:
            try:
                parser_input = resolver.parsed_input
            except Exception:
                parser_input = filepath
        else:
            parser_input = filepath

        for parser_name, Parser in loader_parser_registry.members.items():
            if parser_name == 'fits' or parser_name == 'asdf':
                try:
                    parser = Parser(helper._app, parser_input)
                except Exception:
                    continue
                if not parser.is_valid:
                    try:
                        parser._cleanup()
                    except Exception:
                        pass
                    continue

                try:
                    importer_input = parser.output
                except Exception:
                    try:
                        parser._cleanup()
                    except Exception:
                        pass
                    continue

                for importer_name, Importer in loader_importer_registry.members.items():
                    try:
                        importer = Importer(app=helper._app, resolver=resolver, parser=parser, input=importer_input)
                    except Exception:
                        continue
                    try:
                        if importer.is_valid:
                            labels.append(importer_name)
                    except Exception:
                        pass
                    finally:
                        if hasattr(importer, '_cleanup'):
                            try:
                                importer._cleanup()
                            except Exception:
                                pass

                if hasattr(parser, '_cleanup'):
                    try:
                        parser._cleanup()
                    except Exception:
                        pass

        if not labels:
            labels.append('Cannot read file')

    except Exception:
        # any top-level failure: return what we have (possibly empty)
        pass

    return labels[0]


if __name__ == "__main__":
    _register_macos_finder_filepaths()

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):

        # Define a safe user-writable path (e.g., user's home folder)
        user_home = Path.home()

        # create jdaviz_cache directory to save downloaded files
        jdaviz_cache = user_home / ".cache" / "jdaviz"
        jdaviz_cache.mkdir(exist_ok=True)
        os.environ['JDAVIZ_CACHE_DIR'] = str(jdaviz_cache)

        # create astropy_cache directory to save downloaded files 
        # (backup in case it had been deleted or astropy not installed)
        astropy_cache = user_home / ".cache" / "astropy"
        astropy_cache.mkdir(exist_ok=True)
        os.environ['ASTROPY_CACHE_DIR'] = str(astropy_cache)

        # Change Python's working directory to a writable directory
        # This prevents Jdaviz from defaulting download_uri_to_path to the read-only _MEIPASS path
        os.chdir(user_home)

    orig_args = sys.argv.copy()
    args = [sys.argv.copy()[0]]

    # fits_exts = {'.fits', '.fit', '.fts', '.fitz', '.ftz', '.fz', '.asdf'}
    # converted = []
    # for a in orig_args[1:]:
    #     try:
    #         p = Path(a)
    #     except Exception:
    #         continue
    #     if p.exists() and p.suffix.lower() in fits_exts:
    #         converted.append(str(Path(a).absolute()))

    # for f in converted:
    #     if not any((arg == '--filepath' and i + 1 < len(args) and args[i + 1] == f) for i, arg in enumerate(args)):
    #         args.append("--filepath")
    #         args.append(f)

    open_files = [p for p in os.environ.get('JDAVIZ_OPEN_FILES', '').split(os.pathsep) if p]
    if open_files and not any(arg in {"-fp", "--filepath"} for arg in args):
        for filepath in open_files:
            args.extend(["--filepath", filepath])



    # # Determine whether a layout argument was provided and whether it indicates 'flexible'
    has_layout = any((a == '--layout' or a.startswith('--layout=')) for a in orig_args)
    layout_is_flexible = False
    for i, a in enumerate(orig_args):
        if a == '--layout' and i + 1 < len(orig_args) and orig_args[i + 1].lower() == 'flexible':
            layout_is_flexible = True
            break
        if a.startswith('--layout=') and a.split('=', 1)[1].lower() == 'flexible':
            layout_is_flexible = True
            break

    # Detect whether the user provided file_format flags already
    has_file_format = any((a == '--file_format' or a.startswith('--file_format=') or a == '-ff') for a in orig_args)

    # If layout not provided, set default to flexible so double-click opens flexible layout
    if not has_layout:
        args.append('--layout')
        args.append('flexible')
        layout_is_flexible = True

    if layout_is_flexible and open_files and not has_file_format:
        for fpath in open_files:
            label = detect_fileformat(fpath)

            args.append('--file_format')
            args.append(label)

    # Change the browser to qt if not specified (preserve existing --browser=... form)
    if "--browser" not in args and not any(a.startswith('--browser=') for a in orig_args):
        args.append("--browser")
        args.append("qt")

    sys.argv = args

    log_path = os.path.expanduser("~/Desktop/app_arguments_log.txt")

    with open(log_path, "a") as f:
        f.write(f"--- Launch Time: {datetime.now()} ---\n")
        f.write(f"Number of arguments: {len(sys.argv)}\n")
        f.write(f"Original args: {str(orig_args)}\n\n")
        f.write(f"Full sys.argv: {str(sys.argv)}\n\n")
        f.write(f"os eviron: {str(os.environ.get('JDAVIZ_OPEN_FILES', ''))}\n\n")

    jdaviz.cli._main()