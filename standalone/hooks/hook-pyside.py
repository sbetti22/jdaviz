from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('PySide6')

# Attempt to include Qt plugins and QtWebEngineProcess/resources used by PySide6.
# Be conservative: only add files that exist in the build environment.

datas = []
binaries = []

try:
    import PySide6
    pyside_dir = Path(PySide6.__file__).resolve().parent
    qt_root = pyside_dir / 'Qt'

    # Include the plugins directory (platforms, etc.)
    plugins_dir = qt_root / 'plugins'
    if plugins_dir.exists():
        # add the whole plugins tree as data so it's available at runtime
        for p in plugins_dir.rglob('*'):
            if p.is_file():
                rel = p.relative_to(qt_root)
                dest = str(Path('PySide6') / 'Qt' / rel.parent)
                datas.append((str(p), dest))

    # Include libqcocoa and other dylibs are usually handled by PyInstaller's
    # binaries collection, but include libexec/QtWebEngineProcess explicitly.
    libexec_dir = qt_root / 'libexec'
    if libexec_dir.exists():
        for exe in libexec_dir.iterdir():
            if exe.is_file() and exe.name.startswith('QtWebEngineProcess'):
                binaries.append((str(exe), str(Path('PySide6') / 'Qt' / 'libexec')))

    # Also try common alternate locations for QtWebEngineProcess and resources
    # Search for qtwebengine_resources.pak and include its parent folder
    for p in qt_root.rglob('qtwebengine_resources.pak'):
        parent = p.parent
        for f in parent.rglob('*'):
            if f.is_file():
                rel = f.relative_to(qt_root)
                dest = str(Path('PySide6') / 'Qt' / rel.parent)
                datas.append((str(f), dest))

except Exception:
    # Be defensive: hook should not crash the build if PySide6 not present
    pass
