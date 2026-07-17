# Runtime hook to force-import jdaviz configuration modules so parser registration
# decorators run in frozen PyInstaller bundles.
# This should be listed after the metadata-path prepending hook (rthook-jdaviz-metadata.py)
# so that importlib.metadata and pkg_resources can find package metadata.

import sys
import importlib

if getattr(sys, "frozen", False):
    try:
        # Import top-level package (ensures jdaviz.__init__ executed)
        import jdaviz  # noqa: F401
        # Import the configs package which imports individual config modules
        # that register parsers and loaders via decorators.
        importlib.import_module('jdaviz.configs')
        # Also import the loaders.parsers package to ensure parser classes
        # (e.g., FITSParser) are registered via their decorators when
        # running in a frozen PyInstaller bundle.
        importlib.import_module('jdaviz.core.loaders.parsers')
    except Exception:
        # Best-effort only; failures should not crash the frozen app startup
        pass
