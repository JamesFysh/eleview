import unittest

from qgis.core import (
    QgsCoordinateReferenceSystem, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPoint, QgsField
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
    # "japan": {
    #     START_PT: QgsPoint(140., 46.1),
    #     END_PT: QgsPoint(140.001, 45.999),
    #     ISECT_VECTORS: [
    #         QgsGeometry.fromWkt(v)
    #         for v in [
    #             'LINESTRING (140.000022 46.00001, 139.999978 45.99999)',
    #             'LINESTRING (140.000122 44.99991, 140.000078 44.99989)',
    #             'LINESTRING (140.000222 43.99981, 140.000178 43.99979)',
    #             'LINESTRING (140.000322 42.99971, 140.000278 42.99969)',
    #             'LINESTRING (140.000422 41.99961, 140.000378 41.99959)',
    #             'LINESTRING (140.000522 40.99951, 140.000478 40.99949)',
    #             'LINESTRING (140.000622 39.99941, 140.000578 39.99939)',
    #             'LINESTRING (140.000722 38.99931, 140.000678 38.99929)',
    #             'LINESTRING (140.000822 37.99921, 140.000778 37.99919)',
    #             'LINESTRING (140.000922 36.99911, 140.000878 36.99909)',
    #             'LINESTRING (140.001022 35.99901, 140.000978 35.99899)',
    #         ]
    #     ],
    #     ELFN: lambda i: 50 + i
    # },
    # "arctic": {
    #     START_PT: QgsPoint(-59.9999, 89.997),
    #     END_PT: QgsPoint(-59.99999, 89.9999),
    #     ISECT_VECTORS: [
    #         QgsGeometry.fromWkt(v)
    #         for v in [
    #             'LINESTRING (-59.999878 89.99801, -59.999922 89.99799)',
    #             'LINESTRING (-59.999878 89.998209, -59.999922 89.998189)',
    #             'LINESTRING (-59.999878 89.998408, -59.999922 89.998388)',
    #             'LINESTRING (-59.999878 89.998607, -59.999922 89.998587)',
    #             'LINESTRING (-59.999878 89.998806, -59.999922 89.998786)',
    #             'LINESTRING (-59.999878 89.999005, -59.999922 89.998985)',
    #             'LINESTRING (-59.999878 89.999204, -59.999922 89.999184)',
    #             'LINESTRING (-59.999878 89.999403, -59.999922 89.999383)',
    #             'LINESTRING (-59.999878 89.999602, -59.999922 89.999582)',
    #             'LINESTRING (-59.999878 89.999801, -59.999922 89.999781)',
    #             'LINESTRING (-59.999878 90, -59.999922 89.9998)',
    #         ]
    #     ],
    #     ELFN: lambda i: 50 + i
    # },
    "antarctic": {
        START_PT: QgsPoint(39.998, -89.997),
        END_PT: QgsPoint(40.002, -89.99999),
        ISECT_VECTORS: [
            QgsGeometry.fromWkt(v)
            for v in [
                'LINESTRING (39.999022 -89.99799, 39.998978 -89.99801)',
                'LINESTRING (39.999222 -89.998189, 39.999178 -89.998209)',
                'LINESTRING (39.999422 -89.998388, 39.999378 -89.998408)',
                'LINESTRING (39.999622 -89.998587, 39.999578 -89.998607)',
                'LINESTRING (39.999822 -89.998786, 39.999778 -89.998806)',
                'LINESTRING (40.000022 -89.998985, 39.999978 -89.999005)',
                'LINESTRING (40.000222 -89.999184, 40.000178 -89.999204)',
                'LINESTRING (40.000422 -89.999383, 40.000378 -89.999403)',
                'LINESTRING (40.000622 -89.999582, 40.000578 -89.999602)',
                'LINESTRING (40.000822 -89.999781, 40.000778 -89.999801)',
                'LINESTRING (40.001022 -89.99998, 40.000978 -90)',
            ]
        ],
        ELFN: lambda i: 50 + i
    }
}


class TestElevationReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_layers = {}
        for layer_name, test_data in STATIC_COORD_DATA.items():
            layer = QgsVectorLayer("LineString", layer_name, 'memory')
            layer.startEditing()
            cls.test_layers[layer_name] = layer
            pr = layer.dataProvider()
            pr.addAttributes(
                [QgsField("elevation", QVariant.Double)]
            )
            layer.updateFields()

            features = []
            for idx, vector in enumerate(test_data[ISECT_VECTORS]):
                feature = QgsFeature()
                feature.setGeometry(vector)
                elevation = test_data[ELFN](idx)
                feature.setAttributes([elevation])
                features.append(feature)
            pr.addFeatures(features)
            layer.commitChanges()
            layer.updateExtents()

    def test_can_instantiate_reader(self):
        reader = ElevationReader(None, None, None, None, None, None)
        self.assertIsInstance(reader, ElevationReader)

    def test_can_read_elevations(self):
        for name, details in STATIC_COORD_DATA.items():
            layer_crs = QgsCoordinateReferenceSystem()
            layer_crs.createFromSrid(4326)
            measure_crs = QgsCoordinateReferenceSystem()
            measure_crs.createFromSrid(3112)
            reader = ElevationReader(
                details[START_PT],
                details[END_PT],
                self.test_layers[name],
                "elevation",
                layer_crs,
                measure_crs,
            )
            reader.extract_elevations()
            self.assertEqual(len(reader.points), 11)
            for point in reader.points:
                self.assertTrue(10 < point.y())
                self.assertTrue(point.y() < 200)
