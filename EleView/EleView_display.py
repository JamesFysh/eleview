from math import sqrt
from functools import partial

from PyQt4.QtCore import Qt, QPointF, QLineF, QObject, SIGNAL
from PyQt4.QtGui import (
    QPainterPath, QGraphicsScene, QPen, QBrush, QColor, QLinearGradient
)

from qgis.core import QgsMessageLog

from .ElevationReader import ElevationReader
from .EleView_dialogs import EleViewDialogDisp

ZOOM_IN_FACTOR = 1.25
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR


def fresnel_radius(distance_meters, frequency_mhz):
    radius_meters = 17.32 * sqrt(distance_meters / (4 * frequency_mhz))
    return radius_meters


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
        self.line = None
        self.path = None

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

    def configure_display(self):
        # Helper method to set up the elevation-view dialog
        if self.display is None:
            self.display = EleViewDialogDisp()
            self.display.wheelEvent = self.wheel_event
        for slider in (self.display.pt1Slider, self.display.pt2Slider):
            QObject.connect(
                slider,
                SIGNAL("valueChanged(int)"),
                partial(self.slider_moved, slider)
            )
        QObject.connect(
            self.display.enableFresnel,
            SIGNAL("stateChanged(int)"),
            self.display.frequency.setEnabled
        )

    def hide(self):
        # Hide the elevation-view dialog
        if self.display:
            self.display.hide()
        self.display = None

    def wheel_event(self, event):
        if self.display is None:
            return

        qgv = self.display.eleView

        # Save the scene pos
        old_pos = qgv.mapToScene(event.pos())

        # Zoom
        zoom_factor = ZOOM_IN_FACTOR if event.delta() > 0 else ZOOM_OUT_FACTOR
        qgv.scale(zoom_factor, zoom_factor)

        # Get the new position
        new_pos = qgv.mapToScene(event.pos())

        # Move scene to old position
        delta = new_pos - old_pos
        qgv.translate(delta.x(), delta.y())

    def slider_moved(self, slider, value):
        if self.display is None:
            return

        # Copy the current line
        line = QLineF(self.line.line())
        
        # Mutate it based on the value provided by the slider
        method, line_pt, orig_pt_y, lbl = {
            self.display.pt1Slider: (line.setP1, line.p1(), self.orig_pt1_y, self.display.lblPt1),
            self.display.pt2Slider: (line.setP2, line.p2(), self.orig_pt2_y, self.display.lblPt2),
        }[slider]
        method(QPointF(line_pt.x(), orig_pt_y + value))

        # Colour the line as appropriate
        self.line.setPen(QPen(
            Qt.red if self.line.collidesWithItem(self.path) else Qt.green, 1
        ))
        
        # And update the line geometry - this shall be reflected in the scene
        self.line.setLine(line)

        # Update the relevant label for the slider
        lbl.setText("+{} m".format(value))

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
        self.configure_display()

        self.log_points(points)

        # Set up the scene
        path = QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.lineTo(points[-1].x(), 0)
        path.lineTo(points[0].x(), 0)
        path.lineTo(points[0])

        height = path.boundingRect().height()

        scene = QGraphicsScene(self.display)
        gradient = QLinearGradient(QPointF(0., height), QPointF(0., 0.))
        gradient.setColorAt(0, QColor(0x00b300))
        gradient.setColorAt(1, QColor(0x331a00))
        self.path = scene.addPath(
            path,
            QPen(Qt.blue, 1),
            QBrush(gradient)
        )
        self.line = scene.addLine(
            QLineF(points[0], points[-1]),
            QPen(Qt.green, 1)
        )
        self.orig_pt1_y = points[0].y()
        self.orig_pt2_y = points[-1].y()

        if self.line.collidesWithItem(self.path):
            self.line.setPen(QPen(Qt.red, 1))

        # Set up the view
        view = self.display.eleView
        view.setScene(scene)
        view.ensureVisible(scene.sceneRect())
        view.scale(1., -1.)
        self.display.show()
