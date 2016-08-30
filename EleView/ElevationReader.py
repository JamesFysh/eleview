from PyQt4.QtCore import QPointF
from qgis.core import (
    QgsMessageLog, QgsRectangle, QgsFeatureRequest, QgsGeometry,
    QgsCoordinateTransform, QgsPoint, QGis
)


def de_polygonize(geometry):
    if geometry.type() == QGis.Polygon:
        polygon = geometry.asPolygon()
        exterior = polygon[0]
        return [
            QgsGeometry.fromPolyline([p1, p2])
            for p1, p2 in zip(exterior[0::1], exterior[1::1])
        ]
    return [geometry]


def flatten(pts):
    if pts.type() == QGis.Point and pts.isMultipart():
        return list(pts.asMultiPoint())
    return [pts.asPoint()]


class ElevationReader(object):
    def __init__(self, pt1, pt2, layer, layer_attr, layer_crs, measure_crs):
        self.pt1 = pt1
        self.pt2 = pt2
        self.layer = layer
        self.layer_attr = layer_attr
        self.layer_crs = layer_crs
        self.measure_crs = measure_crs
        self.xform = QgsCoordinateTransform(self.layer_crs, self.measure_crs)
        self.points = None

    def _retrieve_features(self):
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
        return feat_geom_map

    def _transform_coordinates(self, some_geometries):
        # Construct a "reprojector" to map from the layer CRS to the CRS that
        # the user selected.
        for a_geometry in some_geometries:
            a_geometry.transform(self.xform)

    def _generate_points(self, line, feature_map):
        points = []
        for feat, geoms in feature_map.items():
            for geom in geoms:
                if not geom.intersects(line):
                    continue
                elevation = float(feat.attribute(self.layer_attr))
                for x_value in [
                    pt.x()
                    for pt in flatten(line.intersection(geom))
                ]:
                    points.append(QPointF(x_value, elevation))
        if points:
            min_px = min(p.x() for p in points)
            points = sorted(
                [QPointF(p.x() - min_px, p.y()) for p in points],
                key=lambda p: p.x()
            )
        self.points = points

    def extract_elevations(self):
        feat_geom_map = self._retrieve_features()
        self._transform_coordinates(feat_geom_map.values())
        xfpt1, xfpt2 = self.xform.transform(QgsPoint(self.pt1)), \
                       self.xform.transform(QgsPoint(self.pt2))
        self._generate_points(
            QgsGeometry.fromPolyline([xfpt1, xfpt2]),
            {
                f: de_polygonize(g)
                for f, g in feat_geom_map.items()
            }
        )
