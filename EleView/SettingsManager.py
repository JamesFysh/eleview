from qgis.core import QgsProject, QgsMessageLog

log = QgsMessageLog.instance()


class PluginSettings(object):
    def __init__(self, layer_name, layer_attr, proj_wkt):
        self.layer_name = layer_name
        self.layer_attr = layer_attr
        self.proj_wkt = proj_wkt

    def __repr__(self):
        return "layer_name={}, layer_attr={}, proj_wkt={}".format(
            self.layer_name, self.layer_attr, self.proj_wkt
        )


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
        settings = PluginSettings(
            layer_name=layer_name,
            layer_attr=layer_attr,
            proj_wkt=projection_wkt
        )
        log.logMessage(
            "Loaded project settings: {}".format(settings),
            level=QgsMessageLog.INFO
        )
        return settings

    def write(self, settings):
        if not isinstance(settings, PluginSettings):
            raise TypeError(
                "SettingsManager.write must be called with a PluginSettings "
                "object"
            )
        log.logMessage(
            "Storing project settings: {}".format(settings),
            level=QgsMessageLog.INFO
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
