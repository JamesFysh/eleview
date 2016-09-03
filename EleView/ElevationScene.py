from math import sqrt

from PyQt4.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt4.QtGui import (
    QPainterPath, QGraphicsScene, QPen, QBrush, QColor, QLinearGradient,
    QTransform
)

from .Constants import PT1, PT2, RPEN, GPEN, ZOOM_IN_FACTOR, ZOOM_OUT_FACTOR


def fresnel_radius(distance_meters, frequency_mhz):
    radius_meters = 17.32 * sqrt(distance_meters / (4 * frequency_mhz))
    return radius_meters


class ElevationScene(object):
    def __init__(self, dialog, view):
        self.dialog = dialog
        self.view = view
        self.scene = None
        self.line = None
        self.path = None
        self.zone = None
        self.pts = {}
        self.y_delta = {
            PT1: 0.,
            PT2: 0.
        }
        self.fresnel_visible = False
        self.frequency = 2400

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
        # Construct the line-geometry, we'll use this to construct the ellipsoid
        line = QLineF(pt1, pt2)

        # Determine the radius for the ellipsoid
        radius = fresnel_radius(line.length(), frequency)

        # Draw the ellipsoid
        zone = QPainterPath()
        zone.addEllipse(QPointF(0., 0.), line.length() / 2, radius)

        # Rotate the ellipsoid - same angle as the line
        transform = QTransform()
        transform.rotate(-line.angle())
        zone = transform.map(zone)

        # Center the zone over the line
        lc = QRectF(pt1, pt2).center()
        zc = zone.boundingRect().center()
        zone.translate(lc.x() - zc.x(), lc.y() - zc.y())

        return line, zone

    def initialize(self, points, show_fresnel, frequency):
        self.pts = {
            PT1: points[0],
            PT2: points[-1]
        }
        self.fresnel_visible = show_fresnel
        self.frequency = frequency

        # Construct static geometry to be included in the scene
        path = self.path_for(points)

        height = path.boundingRect().height()
        gradient = QLinearGradient(QPointF(0., height), QPointF(0., 0.))
        gradient.setColorAt(0, QColor(0x00b300))
        gradient.setColorAt(1, QColor(0x331a00))

        # Create the scene
        self.scene = QGraphicsScene(self.dialog)

        # Add geometries to the scene, keeping a reference to each
        self.path = self.scene.addPath(path, QPen(Qt.blue, 1), QBrush(gradient))

        # Update the scene; i.e. correct pen-colours etc.
        self.update_scene(add_geometries=True)

        # Set up the view with the constructed scene
        self.view.setScene(self.scene)
        self.view.ensureVisible(self.scene.sceneRect())
        self.view.scale(1., -1.)

    def update_scene(self, add_geometries=False):
        # Get new geometries
        line, zone = self.overlay_for(
            self.pts[PT1] + QPointF(0., self.y_delta[PT1]),
            self.pts[PT2] + QPointF(0., self.y_delta[PT2]),
            self.frequency
        )

        # And update the line geometry - this shall be reflected in the scene
        if add_geometries:
            self.line = self.scene.addLine(line)
            self.zone = self.scene.addPath(zone)
        else:
            self.line.setLine(line)
            self.zone.setPath(zone)

        # Colour the line & zone as appropriate
        for item in (self.line, self.zone):
            item.setPen(RPEN if item.collidesWithItem(self.path) else GPEN)

        # Show/hide the fresnel zone as requested
        self.zone.setVisible(self.fresnel_visible)

    def zoom_event(self, pos, delta):
        # Save the scene pos
        old_pos = self.view.mapToScene(pos)

        # Zoom
        zoom_factor = ZOOM_IN_FACTOR if delta > 0 else ZOOM_OUT_FACTOR
        self.view.scale(zoom_factor, zoom_factor)

        # Translate scene such that zoom appears to center on mouse pointer pos
        new_pos = self.view.mapToScene(pos)
        delta = new_pos - old_pos
        self.view.translate(delta.x(), delta.y())

    def slider_event(self, point, value):
        self.y_delta[point] = value
        self.update_scene()

    def fresnel_event(self, show_fresnel, value):
        self.fresnel_visible = show_fresnel
        self.frequency = value
        self.update_scene()
