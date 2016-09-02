from PyQt4.QtCore import QObject, SIGNAL

from qgis.core import QgsMessageLog, QgsPoint
from qgis.gui import QgsMapToolEmitPoint

log = QgsMessageLog.instance()


class CanvasManager(object):
    def __init__(self, canvas, callback):
        self.canvas = canvas
        self.callback = callback

        # Canvas point-capture tool tracking
        if self.canvas:
            self.clickTool = QgsMapToolEmitPoint(self.canvas)
            self.previousTool = None
            self.current_pt = None
            self.pt1, self.pt2 = None, None

    def initialize(self):
        QObject.connect(
            self.clickTool,
            SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"),
            self.canvas_clicked
        ),

    def cleanup(self):
        if self.canvas.mapTool() == self.clickTool and self.previousTool:
            self.canvas.setMapTool(self.previousTool)

    def enable_capture(self, which_pt):
        self.current_pt = which_pt
        if self.canvas.mapTool() is not self.clickTool:
            self.previousTool = self.canvas.mapTool()
            self.canvas.setMapTool(self.clickTool)

    def canvas_clicked(self, pt, btn):
        log.logMessage(
            "Mouse-click: {}, {}".format(pt, btn),
            level=QgsMessageLog.INFO
        )
        self.callback(self.current_pt, QgsPoint(pt))

    def get_canvas_crs(self):
        return self.canvas.mapSettings().destinationCrs()
