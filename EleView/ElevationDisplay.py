from functools import partial

from PyQt4.QtCore import Qt, QObject, SIGNAL

from qgis.core import QgsMessageLog

from .ElevationReader import ElevationReader
from .ElevationScene import ElevationScene, PT1, PT2
from .PluginDialogs import EleViewDialogDisp


log = QgsMessageLog.instance()


def log_points(the_points):
    x, y = [p.x() for p in the_points], [p.y() for p in the_points]
    log.logMessage(
        "Elevations span over {} units horizontally, with a maximum "
        "elevation of {} and minimum of {}, comprised of {} distinct "
        "points".format(
            max(x) - min(x), max(y), min(y), len(the_points)
        ),
        level=QgsMessageLog.INFO
    )


class ElevationDisplay(object):
    """
    This class is responsible for drawing the "Elevation View" display, where 
    the user can see a line representing line-of-sight between the two points
    selected on the map, overlaid on a simulated side-view of the terrain (
    based on interpolation over the elevation of each vector encountered along
    the path between the start & end point).
    """
    def __init__(self, pt1, pt2, elev_layer, elev_attr, layer_crs, measure_crs):
        self.dialog = None
        self.scene = None

        self.reader = ElevationReader(
            pt1,
            pt2,
            elev_layer,
            elev_attr,
            layer_crs,
            measure_crs
        )

    def show(self):
        """
        Helper function that pulls all the pieces together in order to present
        the user with a dialog that shows the elevation profile between the two
        selected points.
        """
        # Extract elevation details from the vector layer
        self.reader.extract_elevations()

        # Configure the dialog
        self._configure_dialog()

        # Configure the elevation scene
        self._configure_scene(self.reader.points)

        # Display the dialog
        self.dialog.show()

    def hide(self):
        """
        Hides the dialog
        """
        if self.dialog:
            self.dialog.hide()
        self.scene = None
        self.dialog = None

    def _configure_dialog(self):
        """
        Set up the dialog, including connecting all signals and slots as
        required.
        """
        if self.dialog is None:
            self.dialog = EleViewDialogDisp()
            self.dialog.wheelEvent = self.wheel_event
            self.scene = ElevationScene(self.dialog, self.dialog.eleView)
        for slider in (self.dialog.pt1Slider, self.dialog.pt2Slider):
            QObject.connect(
                slider,
                SIGNAL("valueChanged(int)"),
                partial(self.slider_moved, slider)
            )
        QObject.connect(
            self.dialog.enableFresnel,
            SIGNAL("stateChanged(int)"),
            self.fresnel_event
        )
        QObject.connect(
            self.dialog.frequency,
            SIGNAL("valueChanged(int)"),
            self.freq_event
        )

    def _configure_scene(self, points):
        """
        Given a collection of QPointF points, set up a QGraphicsScene, turning
        those points into a QGraphicsPath representing the elevation profile.
        Also overlay a line representing line-of-sight and a fresnel zone
        (useful for making decisions about antenna-height for long-range WiFi
        installations).

        :param points: A list of QPointF objects
        """
        if not points:
            return
        log_points(points)

        frequency = self.dialog.frequency
        self.scene.initialize(points, frequency.isEnabled(), frequency.value())

    def wheel_event(self, event):
        """
        Callback slot for mouse-wheel scrolling events
        :param event: The mouse-wheel event that occurred
        """
        if self.scene is None:
            return

        self.scene.zoom_event(event.pos(), event.delta())

    def slider_moved(self, slider, value):
        """
        Handles valueChanged signals from the sliders either side of the view.

        :param slider: Which slider widget was changed
        :param value: The value currently represented by the slider
        """
        if self.scene is None:
            return
        pt = {self.dialog.pt1Slider: PT1, self.dialog.pt2Slider: PT2}[slider]

        # Update the relevant label for the slider
        lbl = self.dialog.lblPt1 if pt == PT1 else self.dialog.lblPt2
        lbl.setText("+{} m".format(value))

        # And update the geometry in the scene
        self.scene.slider_event(pt, value)

    def freq_event(self, value):
        """
        Handles valueChanged signals from the frequency-selection QSpinBox

        :param value: The current value of the QSpinBox.
        """
        if self.scene is None:
            return
        self.scene.fresnel_event(self.dialog.frequency.isEnabled(), value)

    def fresnel_event(self, state):
        """
        Handles stateChanged signals from the "enable fresnel zone" tickbox.

        :param state: The current state - ticked or un-ticked
        """
        enabled = False if state == Qt.Unchecked else True
        frequency = self.dialog.frequency
        frequency.setEnabled(enabled)
        if self.scene:
            self.scene.fresnel_event(enabled, frequency.value())
