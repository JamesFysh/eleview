from math import sqrt
import unittest

from PyQt4.QtCore import QPointF, QRectF
from PyQt4.QtGui import QPainterPath

from EleView.EleView_dialogs import EleViewDialogDisp
from EleView.ElevationScene import fresnel_radius, ElevationScene, PT1


class TestElevationScene(unittest.TestCase):
    def test_path_for_empty_list_raises(self):
        self.assertRaises(IndexError, ElevationScene.path_for, [])

    def test_path_for_two_points_returns_expected_rect(self):
        a_path = ElevationScene.path_for([QPointF(0., 10.), QPointF(10., 10.)])
        self.assertIsInstance(a_path, QPainterPath)

        rect = a_path.boundingRect()
        self.assertEqual(rect.bottom(), 10.)
        self.assertEqual(rect.height(), 10.)
        self.assertEqual(rect.width(), 10.)
        self.assertEqual(rect.top(), 0.)

    def test_overlay_for_returns_expected_rect(self):
        line, zone = ElevationScene.overlay_for(
            QPointF(-100., -1.), QPointF(100., 1.), 2400
        )
        self.assertEqual(line.length(), sqrt(200.**2 + 2**2))
        zrect = zone.boundingRect()
        self.assertGreater(zrect.width(), 200.)
        self.assertGreater(zrect.height(), fresnel_radius(200., 2400)*2)

        lrect = QRectF(line.p1(), line.p2())
        expanded_zrect = zrect.adjusted(-1., -1., 1., 1.)
        self.assertTrue(
            expanded_zrect.contains(lrect),
            "{} not contained by {}".format(lrect, expanded_zrect)
        )

    def test_scene_has_expected_items(self):
        dialog = EleViewDialogDisp()
        scene = ElevationScene(dialog, dialog.eleView)
        scene.initialize([QPointF(0., 100.), QPointF(100., 100.)], True, 2400)
        self.assertIsNotNone(scene.line)
        self.assertIsNotNone(scene.path)
        self.assertIsNotNone(scene.zone)
        self.assertIsNotNone(scene.scene)
        self.assertEqual(
            {scene.line, scene.path, scene.zone},
            set(scene.scene.items())
        )

    def test_scene_geometries_make_sense(self):
        dialog = EleViewDialogDisp()
        scene = ElevationScene(dialog, dialog.eleView)
        scene.initialize([QPointF(0., 100.), QPointF(100., 100.)], True, 2400)
        self.assertGreater(
            scene.line.boundingRect().top(), scene.path.boundingRect().top(),
        )
        self.assertTrue(
            scene.zone.boundingRect().contains(scene.line.boundingRect())
        )

    def test_scene_geometries_mutate_on_slide(self):
        dialog = EleViewDialogDisp()
        scene = ElevationScene(dialog, dialog.eleView)
        scene.initialize([QPointF(0., 100.), QPointF(100., 100.)], True, 2400)

        line_before = scene.line.line()
        zone_before = scene.zone.path()
        scene.slider_event(PT1, 2)
        self.assertGreater(scene.line.line().y1(), line_before.y1())
        self.assertEqual(scene.line.line().x1(), line_before.x1())

        self.assertGreater(
            scene.zone.boundingRect().center().y(),
            zone_before.boundingRect().center().y()
        )

    def test_scene_geometries_mutate_on_fresnel(self):
        dialog = EleViewDialogDisp()
        scene = ElevationScene(dialog, dialog.eleView)
        scene.initialize([QPointF(0., 100.), QPointF(100., 100.)], True, 2400)

        zone_before = scene.zone.boundingRect()
        scene.fresnel_event(True, 2400)
        self.assertEqual(zone_before, scene.zone.boundingRect(),)

        scene.fresnel_event(True, 2300)
        self.assertNotEqual(zone_before, scene.zone.boundingRect())