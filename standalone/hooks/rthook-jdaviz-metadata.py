#!/usr/bin/env python3
"""
Runtime hook for frozen jdaviz app.

- Ensures packaged distribution metadata (copied via copy_metadata into the dist) is discoverable
  by importlib.metadata / pkg_resources by inserting the `_internal` metadata folder onto sys.path.
- Ensures Jupyter widget assets/nbextensions packaged under ./share/jupyter and ./etc/jupyter are
  visible at runtime by prepending them to JUPYTER_PATH / JUPYTER_CONFIG_DIR.
"""
import sys
import os


def _maybe_prepend_path(p):
    if p and os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)


def _prepend_env_var(name, value):
    if not value or not os.path.exists(value):
        return
    prev = os.environ.get(name, "")
    if prev:
        os.environ[name] = value + os.pathsep + prev
    else:
        os.environ[name] = value


def _candidate_dirs():
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(os.path.abspath(meipass))

    if getattr(sys, "frozen", False):
        exe_dir = os.path.abspath(os.path.dirname(sys.executable))
        candidates.append(exe_dir)

        resources_dir = os.path.abspath(os.path.join(exe_dir, os.pardir, "Resources"))
        if os.path.isdir(resources_dir):
            candidates.append(resources_dir)

    try:
        import jdaviz
        pkg_dir = os.path.abspath(os.path.dirname(jdaviz.__file__))
        candidates.append(pkg_dir)
        pkg_parent = os.path.abspath(os.path.dirname(pkg_dir))
        candidates.append(pkg_parent)
    except Exception:
        pass

    return [c for c in dict.fromkeys(candidates) if os.path.isdir(c)]


def main():
    for base in _candidate_dirs():
        _maybe_prepend_path(os.path.join(base, "_internal"))

    for base in _candidate_dirs():
        share = os.path.join(base, "share", "jupyter")
        etc = os.path.join(base, "etc", "jupyter")
        internal_share = os.path.join(base, "_internal", "share", "jupyter")
        internal_etc = os.path.join(base, "_internal", "etc", "jupyter")

        if os.path.isdir(share):
            _prepend_env_var("JUPYTER_PATH", share)
        if os.path.isdir(etc):
            _prepend_env_var("JUPYTER_CONFIG_DIR", etc)
        if os.path.isdir(internal_share):
            _prepend_env_var("JUPYTER_PATH", internal_share)
        if os.path.isdir(internal_etc):
            _prepend_env_var("JUPYTER_CONFIG_DIR", internal_etc)

    for base in _candidate_dirs():
        _maybe_prepend_path(base)


main()
