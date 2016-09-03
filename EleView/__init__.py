def classFactory(qgis_interface):
    from .EleView import PluginManager
    return PluginManager(qgis_interface)
