from PyInstaller.utils.hooks import collect_submodules

# Ensure PyObjC framework module subpackages are collected so imports like
# `from AppKit import NSApplication` work when bundled.
hiddenimports = []
for pkg in ('objc', 'AppKit', 'Foundation', 'CoreFoundation', 'CoreServices', 'Quartz', 'Cocoa'):
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        # Be defensive: if a particular subpackage isn't installed in the
        # build environment, collect_submodules will raise — ignore.
        pass

