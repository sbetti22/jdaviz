from PyInstaller.utils.hooks import collect_data_files, copy_metadata, collect_submodules, collect_all

datas, binaries, hiddenimports = collect_all('solara')

datas += collect_data_files('solara')
datas += copy_metadata('solara')
datas += copy_metadata('solara-ui')

