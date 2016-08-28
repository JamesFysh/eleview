from functools import partial

from PyQt4.QtCore import Qt, QPointF, QLineF, QObject, SIGNAL

from qgis.core import QgsMessageLog

from .ElevationReader import ElevationReader
from .ElevationScene import ElevationScene, PT1, PT2
from .EleView_dialogs import EleViewDialogDisp


class ElevationDisplay(object):
    """
    This class is responsible for drawing the "Elevation View" display, where 
    the user can see a line representing line-of-sight between the two points
    selected on the map, overlaid on a simulated side-view of the terrain (
    based on interpolation over the elevation of each vector encountered along
    the path between the start & end point).
    """
    def __init__(self, iface, ptsCaptured, elev_layer, elev_attr, measure_crs):
        self.orig_pt1_y = None
        self.orig_pt2_y = None
        self.display = None
        self.scene = None

        pt1, pt2 = ptsCaptured
        self.reader = ElevationReader(
            pt1,
            pt2,
            elev_layer,
            elev_attr,
            iface.mapCanvas().mapSettings().destinationCrs(),
            measure_crs
        )

    def show(self):
        # Extract elevation details from the vector layer
        self.reader.extract_elevations()

        # And display
        self.show_elevation(self.reader.points)

    def configure_dialog(self):
        # Helper method to set up the elevation-view dialog
        if self.display is None:
            self.display = EleViewDialogDisp()
            self.display.wheelEvent = self.wheel_event
            self.scene = ElevationScene(self.display, self.display.eleView)
        for slider in (self.display.pt1Slider, self.display.pt2Slider):
            QObject.connect(
                slider,
                SIGNAL("valueChanged(int)"),
                partial(self.slider_moved, slider)
            )
        QObject.connect(
            self.display.enableFresnel,
            SIGNAL("stateChanged(int)"),
            self.fresnel_event
        )
        QObject.connect(
            self.display.frequency,
            SIGNAL("valueChanged(int"),
            self.freq_event
        )

    def hide(self):
        # Hide the elevation-view dialog
        if self.display:
            self.display.hide()
        self.scene = None
        self.display = None

    def wheel_event(self, event):
        if self.scene is None:
            return

        self.scene.zoom_event(event.pos(), event.delta())

    def slider_moved(self, slider, value):
        if self.scene is None:
            return
        pt = {self.display.pt1Slider: PT1, self.display.pt2Slider: PT2}[slider]

        # Update the relevant label for the slider
        lbl = self.display.lblPt1 if pt == PT1 else self.display.lblPt2
        lbl.setText("+{} m".format(value))

        # And update the geometry in the scene
        self.scene.slider_event(pt, value)

    def freq_event(self, value):
        if self.scene is None:
            return
        self.scene.fresnel_event(self.display.frequency.isEnabled(), value)

    def fresnel_event(self, state):
        enabled = True if state else False
        frequency = self.display.frequency
        frequency.setEnabled(enabled)
        if self.scene:
            self.scene.fresnel_event(enabled, frequency.value())

    @staticmethod
    def log_points(the_points):
        x, y = [p.x() for p in the_points], [p.y() for p in the_points]
        QgsMessageLog.logMessage(
            "Elevations span over {} units horizontally, with a maximum "
            "elevation of {} and minimum of {}, comprised of {} distinct "
            "points".format(
                max(x) - min(x), max(y), min(y), len(the_points)
            ),
            level=QgsMessageLog.INFO
        )

    def show_elevation(self, points):
        if not points:
            return
        self.log_points(points)
        self.configure_dialog()
        frequency = self.display.frequency
        self.scene.initialize(points, frequency.isEnabled(), frequency.value())
        self.display.show()
