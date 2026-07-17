from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata, collect_submodules


datas, binaries, hiddenimports = collect_all('specutils')
datas += copy_metadata('specutils')