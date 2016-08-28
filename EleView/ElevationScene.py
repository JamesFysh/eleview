from math import sqrt, atan2

from PyQt4.QtGui import (
    QPainterPath, QGraphicsScene, QPen, QBrush, QColor, QLinearGradient
)
from PyQt4.QtCore import Qt, QPointF, QLineF

ZOOM_IN_FACTOR = 1.25
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR
PT1, PT2 = "first point", "second point"


def fresnel_radius(distance_meters, frequency_mhz):
    radius_meters = 17.32 * sqrt(distance_meters / (4 * frequency_mhz))
    return radius_meters


class ElevationScene(object):
    def __init__(self, dialog, view):
        self.dialog = dialog
        self.view = view
        self.line = None
        self.path = None
        self.zone = None
        self.p_y = {}

    @staticmethod
    def path_for(points):
        path = QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.lineTo(points[-1].x(), 0)
        path.lineTo(points[0].x(), 0)
        path.lineTo(points[0])
        return path

    @staticmethod
    def overlay_for(pt1, pt2, frequency):
        line = QLineF(pt1, pt2)
        radius = fresnel_radius(line.length(), frequency)
        zone = None

        return line, zone

    def initialize(self, points, show_fresnel, frequency):
        self.p_y = {
            PT1: points[0].y(),
            PT2: points[-1].y()
        }

        # Construct geometries to be included in the scene
        path = self.path_for(points)
        line, zone = self.overlay_for(points[0], points[-1], frequency)

        height = path.boundingRect().height()
        gradient = QLinearGradient(QPointF(0., height), QPointF(0., 0.))
        gradient.setColorAt(0, QColor(0x00b300))
        gradient.setColorAt(1, QColor(0x331a00))

        # Create the scene
        scene = QGraphicsScene(self.dialog)

        # Add geometries to the scene, keeping a reference to each
        self.path = scene.addPath(path, QPen(Qt.blue, 1), QBrush(gradient))
        self.line = scene.addLine(line, QPen(Qt.green, 1))
        self.zone = scene.addEllipse(0., 0., 0., 0.)

        if self.line.collidesWithItem(self.path):
            self.line.setPen(QPen(Qt.red, 1))

        # Set up the view
        self.view.setScene(scene)
        self.view.ensureVisible(scene.sceneRect())
        self.view.scale(1., -1.)

    def slider_event(self, point, value):
        # Copy the current line
        line = QLineF(self.line.line())

        # Mutate it based on the value provided by the slider
        method, line_pt= {
            PT1: (line.setP1, line.p1()),
            PT2: (line.setP2, line.p2())
        }[point]
        method(QPointF(line_pt.x(), self.p_y[point] + value))

        # And update the line geometry - this shall be reflected in the scene
        self.line.setLine(line)

        # Colour the line as appropriate
        self.line.setPen(QPen(
            Qt.red if self.line.collidesWithItem(self.path) else Qt.green, 1
        ))

    def zoom_event(self, pos, delta):
        # Save the scene pos
        old_pos = self.view.mapToScene(pos)

        # Zoom
        zoom_factor = ZOOM_IN_FACTOR if delta > 0 else ZOOM_OUT_FACTOR
        self.view.scale(zoom_factor, zoom_factor)

        # Get the new position
        new_pos = self.view.mapToScene(pos)

        # Move scene to old position
        delta = new_pos - old_pos
        self.view.translate(delta.x(), delta.y())

    def fresnel_event(self, show_fresnel, value):
        if show_fresnel is False:
            self.zone.hide()
        else:
            pass
