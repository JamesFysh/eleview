from functools import partial

from qgis.core import (
    QgsMessageLog, QgsRectangle, QgsFeatureRequest, QgsGeometry,
    QgsCoordinateTransform,
)
from qgis.gui import (
    QgsMapCanvas
)
from PyQt4.QtCore import (
    Qt, QPointF, QLineF, QObject, SIGNAL
)
from PyQt4.QtGui import (
    QPainterPath, QGraphicsScene, QPen, QBrush
)

from shapely.geometry import Point
from shapely import wkt

from EleView_dialog_display import EleViewDialogDisp


def flatten(pts):
    if not isinstance(pts, Point):
        return list(pts.geoms)
    return [pts]


class ElevationDisplay(object):
    def __init__(self, iface, ptsCaptured, elev_layer, elev_attr, measure_crs):
        self.iface = iface
        self.pt1, self.pt2 = ptsCaptured
        self.orig_pt1_y = None
        self.orig_pt2_y = None
        self.elev_layer = elev_layer
        self.elev_attr = elev_attr
        self.measure_crs = measure_crs
        self.display = None
        self.line = None
        self.path = None

    def show(self):
        self.extract_elevations()

    def hide(self):
        if self.display:
            self.display.hide()

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        qgv = self.display.eleView

        # Save the scene pos
        oldPos = qgv.mapToScene(event.pos())

        # Zoom
        if event.delta() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        qgv.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = qgv.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        qgv.translate(delta.x(), delta.y())

    def extract_elevations(self):
        rect = QgsRectangle(self.pt1, self.pt2)
        QgsMessageLog.logMessage(
            "Getting features in layer {}, intersecting rect {}".format(
                self.elev_layer.name(),
                rect.toString()
            ),
            level=QgsMessageLog.INFO
        )
        features = list(
            self.elev_layer.getFeatures(QgsFeatureRequest(rect))
        )
        QgsMessageLog.logMessage(
            "Got {} features".format(len(features)), 
            level=QgsMessageLog.INFO
        )
        xform = QgsCoordinateTransform(
            self.iface.mapCanvas().mapSettings().destinationCrs(),
            self.measure_crs
        )
        self.generate_points(
            wkt.loads(
                QgsGeometry.fromPolyline([self.pt1, self.pt2]).exportToWkt()
            ),
            wkt.loads(
                QgsGeometry.fromPolyline([
                    xform.transform(self.pt1),
                    xform.transform(self.pt2)
                ]).exportToWkt()
            ).length,
            {
                f: wkt.loads(f.geometry().exportToWkt())
                for f in features
            }
        )

    def generate_points(self, line, length, feature_map):
        points = []
        for feat, geom in feature_map.iteritems():
            isect_pts = [
                length * line.project(pt, True)
                for pt in flatten(line.intersection(geom))
            ]
            elevation = float(feat.attribute(self.elev_attr))
            for isect_pt in isect_pts:
                points.append(QPointF(isect_pt, elevation))
        self.show_elevation(sorted(points, key=lambda p: p.x()))

    def configure_display(self):
        if self.display is None:
            self.display = EleViewDialogDisp()
            self.display.wheelEvent = self.wheelEvent
        QObject.connect(
            self.display.pt1Slider,
            SIGNAL("valueChanged(int)"),
            partial(self.sliderMoved, self.display.pt1Slider)
        )
        QObject.connect(
            self.display.pt2Slider,
            SIGNAL("valueChanged(int)"),
            partial(self.sliderMoved, self.display.pt2Slider)
        )

    def sliderMoved(self, slider, value):
        QgsMessageLog.logMessage(
            "{} changed to {}".format(slider, value),
            level=QgsMessageLog.INFO
        )
        line = QLineF(self.line.line())
        if slider == self.display.pt1Slider:
            line.setP1(
                QPointF(
                    line.p1().x(),
                    self.orig_pt1_y + value

                )
            )
            self.display.lblPt1.setText("+{} m".format(value))
        else:
            line.setP2(
                QPointF(
                    line.p2().x(),
                    self.orig_pt2_y + value
                )
            )
            self.display.lblPt2.setText("+{} m".format(value))
        if self.line.collidesWithItem(self.path):
            self.line.setPen(QPen(Qt.red, 1))
        else:
            self.line.setPen(QPen(Qt.green, 1))
        self.line.setLine(line)

    def show_elevation(self, points):
        if not points:
            return
        self.configure_display()

        # Set up the scene
        scene = QGraphicsScene(self.display)
        path = QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.lineTo(points[-1].x(), 0)
        path.lineTo(points[0].x(), 0)
        path.lineTo(points[0].x(), points[0].y())
        self.path = scene.addPath(
            path,
            QPen(Qt.black, 1),
            QBrush(Qt.darkGreen, Qt.Dense4Pattern)
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
        #view.fitInView(scene.sceneRect())
        view.scale(1., -1.)
        self.display.show()
