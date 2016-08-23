import unittest
from collections import namedtuple

from qgis.core import (
    QgsCoordinateReferenceSystem, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPoint, QgsField,
)
from PyQt4.QtCore import QVariant

from EleView.ElevationReader import ElevationReader

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()

START_PT, END_PT, ISECT_VECTORS, ELFN = (
    "start_pt", "end_pt", "vectors", "elevation function"
)

STATIC_COORD_DATA = {
    "aust": {
        START_PT: QgsPoint(144.9617, -37.81466),
        END_PT: QgsPoint(144.96126, -37.81369),
        ISECT_VECTORS: [
            QgsGeometry.fromWkt(v)
            for v in [
                'LINESTRING (144.961722 -37.81465, 144.961678 -37.81467)',
                'LINESTRING (144.961678 -37.814553, 144.961634 -37.814573)',
                'LINESTRING (144.961634 -37.814456, 144.96159 -37.814476)',
                'LINESTRING (144.96159 -37.814359, 144.961546 -37.814379)',
                'LINESTRING (144.961546 -37.814262, 144.961502 -37.814282)',
                'LINESTRING (144.961502 -37.814165, 144.961458 -37.814185)',
                'LINESTRING (144.961458 -37.814068, 144.961414 -37.814088)',
                'LINESTRING (144.961414 -37.813971, 144.96137 -37.813991)',
                'LINESTRING (144.96137 -37.813874, 144.961326 -37.813894)',
                'LINESTRING (144.961326 -37.813777, 144.961282 -37.813797)',
                'LINESTRING (144.961282 -37.81368, 144.961238 -37.8137)',
            ]
        ],
        ELFN: lambda i: 50 + i
    },
    "japan": {
        START_PT: QgsPoint(140., 46.),
        END_PT: QgsPoint(140.001, 45.999),
        ISECT_VECTORS: [
            QgsGeometry.fromWkt(v)
            for v in [
                'LINESTRING (140.000022 46.00001, 139.999978 45.99999)',
                'LINESTRING (140.000122 45.99991, 140.000078 45.99989)',
                'LINESTRING (140.000222 45.99981, 140.000178 45.99979)',
                'LINESTRING (140.000322 45.99971, 140.000278 45.99969)',
                'LINESTRING (140.000422 45.99961, 140.000378 45.99959)',
                'LINESTRING (140.000522 45.99951, 140.000478 45.99949)',
                'LINESTRING (140.000622 45.99941, 140.000578 45.99939)',
                'LINESTRING (140.000722 45.99931, 140.000678 45.99929)',
                'LINESTRING (140.000822 45.99921, 140.000778 45.99919)',
                'LINESTRING (140.000922 45.99911, 140.000878 45.99909)',
                'LINESTRING (140.001022 45.99901, 140.000978 45.99899)',
            ]
        ],
        ELFN: lambda i: 50 + i
    },
    "arctic": {
        START_PT: QgsPoint(-59.9999, 89.98),
        END_PT: QgsPoint(-59.99999, 89.99),
        ISECT_VECTORS: [
            QgsGeometry.fromWkt(v)
            for v in [
                'LINESTRING (-59.99968 89.9801, -60.00012 89.9799)',
                'LINESTRING (-59.99968 89.9811, -60.00012 89.9809)',
                'LINESTRING (-59.99968 89.9821, -60.00012 89.9819)',
                'LINESTRING (-59.99968 89.9831, -60.00012 89.9829)',
                'LINESTRING (-59.99968 89.9841, -60.00012 89.9839)',
                'LINESTRING (-59.99968 89.9851, -60.00012 89.9849)',
                'LINESTRING (-59.99968 89.9861, -60.00012 89.9859)',
                'LINESTRING (-59.99968 89.9871, -60.00012 89.9869)',
                'LINESTRING (-59.99968 89.9881, -60.00012 89.9879)',
                'LINESTRING (-59.99968 89.9891, -60.00012 89.9889)',
                'LINESTRING (-59.99968 89.9901, -60.00012 89.9899)',
            ]
        ],
        ELFN: lambda i: 50 + i
    },
    "antarctic": {
        START_PT: QgsPoint(39.999, -89.997),
        END_PT: QgsPoint(40.001, -89.998),
        ISECT_VECTORS: [
            QgsGeometry.fromWkt(v)
            for v in [
                'LINESTRING (39.99922 -89.9969, 39.99878 -89.9971)',
                'LINESTRING (39.99942 -89.997, 39.99898 -89.9972)',
                'LINESTRING (39.99962 -89.9971, 39.99918 -89.9973)',
                'LINESTRING (39.99982 -89.9972, 39.99938 -89.9974)',
                'LINESTRING (40.00002 -89.9973, 39.99958 -89.9975)',
                'LINESTRING (40.00022 -89.9974, 39.99978 -89.9976)',
                'LINESTRING (40.00042 -89.9975, 39.99998 -89.9977)',
                'LINESTRING (40.00062 -89.9976, 40.00018 -89.9978)',
                'LINESTRING (40.00082 -89.9977, 40.00038 -89.9979)',
                'LINESTRING (40.00102 -89.9978, 40.00058 -89.998)',
                'LINESTRING (40.00122 -89.9979, 40.00078 -89.9981)',
            ]
        ],
        ELFN: lambda i: 50 + i
    },
    "center": {
        START_PT: QgsPoint(-0.005, -0.005),
        END_PT: QgsPoint(0.005, 0.005),
        ISECT_VECTORS: [
            QgsGeometry.fromWkt(v)
            for v in [
                'LINESTRING (-0.00522 -0.0049, -0.00478 -0.0051)',
                'LINESTRING (-0.00422 -0.0039, -0.00378 -0.0041)',
                'LINESTRING (-0.00322 -0.0029, -0.00278 -0.0031)',
                'LINESTRING (-0.00222 -0.0019, -0.00178 -0.0021)',
                'LINESTRING (-0.00122 -0.0009, -0.00078 -0.0011)',
                'LINESTRING (-0.00022 0.0001, 0.00022 -0.0001)',
                'LINESTRING (0.00078 0.0011, 0.00122 0.0009)',
                'LINESTRING (0.00178 0.0021, 0.00222 0.0019)',
                'LINESTRING (0.00278 0.0031, 0.00322 0.0029)',
                'LINESTRING (0.00378 0.0041, 0.00422 0.0039)',
                'LINESTRING (0.00478 0.0051, 0.00522 0.0049)',
            ]
        ],
        ELFN: lambda i: 50 + i
    }
}

FeatureDescr = namedtuple('FeatureDescr', 'geom, elev')


class LayerMaker(object):
    def __init__(self, layer_name):
        self.layer = QgsVectorLayer("LineString", layer_name, 'memory')
        self.pr = self.layer.dataProvider()
        self.layer.startEditing()
        self.pr.addAttributes(
            [QgsField("elevation", QVariant.Double)]
        )
        self.layer.updateFields()

    def add_features(self, feature_descr_list):
        features = []
        for fd in feature_descr_list:
            feature = QgsFeature()
            feature.setGeometry(fd.geom)
            feature.setAttributes([fd.elev])
            features.append(feature)
        self.pr.addFeatures(features)
        self.layer.commitChanges()


class TestElevationReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layer_crs = QgsCoordinateReferenceSystem()
        cls.layer_crs.createFromSrid(4326)
        cls.measure_crs = QgsCoordinateReferenceSystem()
        cls.measure_crs.createFromSrid(4283)
        cls.test_layers = {}
        for layer_name, test_data in STATIC_COORD_DATA.items():
            lm = LayerMaker(layer_name)
            lm.add_features(
                [
                    FeatureDescr(vector, test_data[ELFN](idx))
                    for idx, vector in enumerate(test_data[ISECT_VECTORS])
                ]
            )
            cls.test_layers[layer_name] = lm.layer

    def extract_elevation_helper(self, p1, p2, features):
        lm = LayerMaker('test')
        lm.add_features(features)
        reader = ElevationReader(
            p1, p2, lm.layer, "elevation", self.layer_crs, self.measure_crs,
        )
        reader.extract_elevations()
        return reader.points

    def test_can_instantiate_reader(self):
        reader = ElevationReader(None, None, None, None, None, None)
        self.assertIsInstance(reader, ElevationReader)

    def test_can_read_elevations(self):
        for name, details in STATIC_COORD_DATA.items():
            reader = ElevationReader(
                details[START_PT],
                details[END_PT],
                self.test_layers[name],
                "elevation",
                self.layer_crs,
                self.measure_crs,
            )
            reader.extract_elevations()
            points = reader.points
            self.assertGreater(len(points), 9)
            p_x = [p.x() for p in points]
            self.assertListEqual(p_x, sorted(p_x))
            for point in points:
                self.assertTrue(10 < point.y())
                self.assertTrue(point.y() < 200)
                self.assertTrue(0 <= point.x())

    def test_no_intersect(self):
        # Define two points
        p1, p2 = QgsPoint(20., 10.), QgsPoint(20., 10.2)

        # Get the points generated by ElevationReader (should be an empty list)
        points = self.extract_elevation_helper(p1, p2, [])

        # Evaluate the results
        p_x = [p.x() for p in points]
        self.assertListEqual(p_x, sorted(p_x))
        self.assertEqual(len(points), 0)

    def test_multi_intersect(self):
        def zipline(p1, p2, increment):
            middle = p1.x()
            start = p1.y() + increment
            end = p2.y() - increment
            while start < end:
                yield QgsPoint(middle - increment, start)
                start += increment
                yield QgsPoint(middle + increment, start)

        # Define the two captured points
        p1, p2 = QgsPoint(20., 10.), QgsPoint(20., 10.2)

        # Define a "zig-zag" LineString geometry along the line between these
        # two points
        ls_points = list(zipline(p1, p2, 0.01))
        ls = QgsGeometry.fromPolyline(ls_points)

        # Get the points generated by ElevationReader
        points = self.extract_elevation_helper(
            p1,
            p2,
            [FeatureDescr(ls, 20)]
        )

        # Evaluate the results
        self.assertEqual(len(points), len(ls_points) - 1)
        p_x = [p.x() for p in points]
        self.assertListEqual(p_x, sorted(p_x))
        for point in points:
            self.assertEqual(point.y(), 20)

    def test_poly_intersect(self):
        # Define the two captured points

        p1 = QgsPoint(20.00871557427477, 10.00038053019082)
        p2 = QgsPoint(19.99128442572524, 10.19961946980917)
        centroid = QgsGeometry.fromPoint(QgsPoint(20., 10.1))

        # Get the points generated by ElevationReader
        points = self.extract_elevation_helper(
            p1,
            p2,
            [
                FeatureDescr(
                    centroid.buffer(radius, 8),
                    20 + ((.08 - radius) * 200)
                )
                for radius in (.01, .02, .03, .04, .05, .06, .07, .08)
            ]
        )

        # Evaluate the results
        self.assertEqual(len(points), 16)
        p_x = [p.x() for p in points]
        self.assertListEqual(p_x, sorted(p_x))
        for point in points:
            self.assertTrue(10 < point.y())
            self.assertTrue(point.y() < 200)
            self.assertTrue(0 < point.x())
