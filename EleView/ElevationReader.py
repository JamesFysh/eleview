from PyQt4.QtCore import QPointF
from qgis.core import (
    QgsMessageLog, QgsRectangle, QgsFeatureRequest, QgsGeometry,
    QgsCoordinateTransform,
)

from shapely.geometry import MultiPoint
from shapely import wkt


def flatten(pts):
    if isinstance(pts, MultiPoint):
        return list(pts.geoms)
    return [pts]


class ElevationReader(object):
    def __init__(self, pt1, pt2, layer, layer_attr, layer_crs, measure_crs):
        self.pt1 = pt1
        self.pt2 = pt2
        self.layer = layer
        self.layer_attr = layer_attr
        self.layer_crs = layer_crs
        self.measure_crs = measure_crs
        self.points = None

    def extract_elevations(self):
        # Construct an MBR in which to look for vectors in the layer
        rect = QgsRectangle(self.pt1, self.pt2)
        QgsMessageLog.logMessage(
            "Getting features in layer {}, intersecting rect {}".format(
                self.layer.name(),
                rect.toString()
            ),
            level=QgsMessageLog.INFO
        )

        # Retrieve vectors from the layer that intersect the constructed MBR
        feat_geom_map = {
            f: f.geometry()
            for f in self.layer.getFeatures(QgsFeatureRequest(rect))
        }
        QgsMessageLog.logMessage(
            "Got {} features".format(len(feat_geom_map)),
            level=QgsMessageLog.INFO
        )

        # Construct a "reprojector" to map from the layer CRS to the CRS that
        # the user selected.
        xform = QgsCoordinateTransform(self.layer_crs, self.measure_crs)
        trcrs = xform.transform
        for g in feat_geom_map.values():
            g.transform(xform)

        # And generate
        self.generate_points(
            wkt.loads(
                QgsGeometry.fromPolyline([self.pt1, self.pt2]).exportToWkt()
            ),
            wkt.loads(
                QgsGeometry.fromPolyline([
                    trcrs(self.pt1), trcrs(self.pt2)
                ]).exportToWkt()
            ).length,
            {
                f: wkt.loads(g.exportToWkt())
                for f, g in feat_geom_map.items()
            }
        )

    def generate_points(self, line, length, feature_map):
        points = []
        for feat, geom in feature_map.items():
            isect_pts = [
                length * line.project(pt, True)
                for pt in flatten(line.intersection(geom))
            ]
            elevation = float(feat.attribute(self.layer_attr))
            for isect_pt in isect_pts:
                points.append(QPointF(isect_pt, elevation))
        self.points = sorted(points, key=lambda p: p.x())
