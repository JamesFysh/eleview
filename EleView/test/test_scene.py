import unittest

from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QPainterPath

from EleView.ElevationScene import ElevationScene


class TestElevationScene(unittest.TestCase):
    def test_path_for_empty_list_raises(self):
        self.assertRaises(IndexError, ElevationScene.path_for, [])

    def test_path_for_two_points_returns_expected_rect(self):
        a_path = ElevationScene.path_for([QPointF(0., 10.), QPointF(10., 10.)])
        self.assertIsInstance(a_path, QPainterPath)

        rect = a_path.boundingRect()
