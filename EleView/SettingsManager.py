from qgis.core import QgsProject

class PluginSettings(object):
    def __init__(self, layer_name, layer_attr, proj_wkt):
        self.layer_name = layer_name
        self.layer_attr = layer_attr
        self.proj_wkt = proj_wkt


class SettingsManager(object):
    def __init__(self):
        self.project_instance = QgsProject.instance()

    def read(self):
        layer_name = self.project_instance.readEntry(
            "eleview", "layername", ""
        )[0]
        layer_attr = self.project_instance.readEntry(
            "eleview", "layerattr", ""
        )[0]
        projection_wkt = self.project_instance.readEntry(
            "eleview", "projdefn", ""
        )[0]
        return PluginSettings(
            layer_name=layer_name,
            layer_attr=layer_attr,
            proj_wkt=projection_wkt
        )

    def write(self, settings):
        if not isinstance(settings, PluginSettings):
            raise TypeError(
                "SettingsManager.write must be called with a PluginSettings "
                "object"
            )
        self.project_instance.writeEntry(
            "eleview", "layername", settings.layer_name
        )
        self.project_instance.writeEntry(
            "eleview", "layerattr", settings.layer_attr
        )
        self.project_instance.writeEntry(
            "eleview", "projdefn", settings.proj_wkt
        )
