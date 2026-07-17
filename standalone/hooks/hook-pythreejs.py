"""PyInstaller hook for pythreejs.

pythreejs requires JSON data files at runtime for shader definitions.
This hook ensures those files are bundled with the application.
"""

from PyInstaller.utils.hooks import collect_data_files, copy_metadata, collect_submodules

# Collect all JSON files from pythreejs package
datas = collect_data_files('pythreejs', includes=['**/*.json'])
# datas = collect_data_files('pythreejs')
datas += copy_metadata('pythreejs')
hiddenimports = collect_submodules("pythreejs")