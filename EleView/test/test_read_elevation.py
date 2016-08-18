import unittest

from qgis.core import (
    QgsCoordinateReferenceSystem, QgsVectorLayer, QgsFeature, QgsGeometry
)

from EleView.ElevationReader import ElevationReader

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()

START_PT, END_PT, ISECT_VECTORS = "start_pt", "end_pt", "vectors"

STATIC_COORD_DATA = {
    "aust": {
        START_PT: None,
        END_PT: None,
        ISECT_VECTORS: [],
    },
    "japan": {
        START_PT: None,
        END_PT: None,
        ISECT_VECTORS: [],
    },
    "arctic": {
        START_PT: None,
        END_PT: None,
        ISECT_VECTORS: [],
    },
    "antarctic": {
        START_PT: None,
        END_PT: None,
        ISECT_VECTORS: [],
    }
}


class TestElevationReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_layers = {}
        for layer_name, test_data in STATIC_COORD_DATA.items():
            layer = QgsVectorLayer(baseName=layer_name)
            cls.test_layers[layer_name] = layer
            for vector in test_data[ISECT_VECTORS]:
                feature = QgsFeature()
                layer.addFeature(feature)

    def test_can_instantiate_reader(self):
        reader = ElevationReader(None, None, None, None, None, None)
        self.assertIsInstance(reader, ElevationReader)

    def test_can_read_elevations(self):
        pass