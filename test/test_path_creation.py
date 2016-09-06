import unittest

from PyQt4.QtCore import QPointF

from EleView.ElevationPath import ElevationPath


class TestPathGeneration(unittest.TestCase):
    def test_geometry(self):
        ep = ElevationPath([
            QPointF(0., 100.),
            QPointF(100., 150.),
            QPointF(200., 100.)
        ])
        path = ep.create_path()
        self.assertTrue(
            all(p.y() >= 0.0 for p in path)
        )
        self.assertTrue(
            all(p.x() >= 0.0 for p in path)
        )
