import unittest

from qgis.core import (
    QgsPoint, QgsCoordinateReferenceSystem
)

from EleView.EleView_display import ElevationDisplay


class TestElevationDisplayClass(unittest.TestCase):
    def setUp(self):
        crs = QgsCoordinateReferenceSystem().createFromSrid(3112)

        self.display = ElevationDisplay(
            QgsPoint(0., 0.),
            QgsPoint(0., 0.),
            None,
            None,
            crs,
            crs
        )

    def test_sliders_affect_scene(self):
        pass

    def test_fresnel_checkbox_affects_scene(self):
        pass

    def test_fresnel_spinbox_affects_scene(self):
        pass