from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata, collect_submodules


hiddenimports = collect_submodules("jdaviz") + collect_submodules("specutils")
datas = collect_data_files('jdaviz')
datas += copy_metadata('jdaviz')
# Include metadata for external packages that are required for specutils/ASDF reader discovery
# and Glue astronomy integration in the frozen app.
datas += copy_metadata('specutils')
datas += copy_metadata('asdf')
datas += copy_metadata('ndcube')
datas += copy_metadata('gwcs')
datas += copy_metadata('astropy')
datas += copy_metadata('glue_astronomy')
datas += copy_metadata('matplotlib_inline')

# Include widget frameworks and nbextension assets so the frozen bundle can find widget models
# and registration information at runtime.
datas += collect_data_files('ipywidgets')
datas += copy_metadata('ipywidgets')
datas += collect_data_files('widgetsnbextension')
datas += copy_metadata('widgetsnbextension')
datas += collect_data_files('jupyterlab_widgets')
datas += copy_metadata('jupyterlab_widgets')
datas += collect_data_files('ipyvuetify')
datas += copy_metadata('ipyvuetify')
datas += collect_data_files('ipyvue')
datas += copy_metadata('ipyvue')
datas += collect_data_files('reacton')
datas += copy_metadata('reacton')
datas += collect_data_files('solara')
datas += copy_metadata('solara')