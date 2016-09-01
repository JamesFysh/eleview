import unittest

from PyQt4.QtCore import Qt, QPointF
from qgis.core import (
    QgsPoint, QgsCoordinateReferenceSystem
)

from EleView.ElevationDisplay import ElevationDisplay


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
        self.display._configure_dialog()
        self.display._configure_scene([
            QPointF(0., 100.), QPointF(100., 100.)
        ])


class TestElevationDisplaySliders(TestElevationDisplayClass):

    def test_slider_callback_affect_scene(self):
        display = self.display
        dialog = display.dialog
        scene = display.scene

        # Check that slider callback with slider "1" has an affect
        line_rect_before = scene.line.boundingRect()
        display.slider_moved(dialog.pt1Slider, 10)
        line_rect_after = scene.line.boundingRect()
        self.assertNotEqual(
            line_rect_before, line_rect_after
        )

        # And slider "2", also.
        line_rect_before = scene.line.boundingRect()
        display.slider_moved(dialog.pt2Slider, 20)
        line_rect_after = scene.line.boundingRect()
        self.assertNotEqual(
            line_rect_before, line_rect_after
        )

    def test_slider_signal_triggers_callback(self):
        display = self.display
        dialog = display.dialog
        scene = display.scene

        # Check that slider change-of-value with slider "1" has an affect
        # Callback triggered via signal
        line_rect_before = scene.line.boundingRect()
        dialog.pt1Slider.setValue(10)
        line_rect_after = scene.line.boundingRect()
        self.assertNotEqual(
            line_rect_before, line_rect_after
        )

        # And slider "2", also.
        # Callback triggered via signal
        line_rect_before = scene.line.boundingRect()
        dialog.pt2Slider.setValue(20)
        line_rect_after = scene.line.boundingRect()
        self.assertNotEqual(
            line_rect_before, line_rect_after
        )


class TestElevationDisplayFresnelCheckbox(TestElevationDisplayClass):
    def test_fresnel_callback_affects_scene(self):
        display = self.display
        scene = display.scene

        # Calling the fresnel callback with 'Unchecked' hides the zone path
        zone_visible_before = scene.zone.isVisible()
        display.fresnel_event(Qt.Unchecked)
        zone_visible_after = scene.zone.isVisible()
        self.assertNotEqual(
            zone_visible_before, zone_visible_after
        )
        self.assertFalse(zone_visible_after)

        # And with 'checked', it shows the zone path
        zone_visible_before = scene.zone.isVisible()
        display.fresnel_event(Qt.Checked)
        zone_visible_after = scene.zone.isVisible()
        self.assertNotEqual(
            zone_visible_before, zone_visible_after
        )
        self.assertTrue(zone_visible_after)

    def test_fresnel_signal_triggers_callback(self):
        display = self.display
        dialog = display.dialog
        scene = display.scene

        # Calling the fresnel callback with 'Unchecked' hides the zone path
        # Callback triggered via signal
        zone_visible_before = scene.zone.isVisible()
        dialog.enableFresnel.setCheckState(Qt.Unchecked)
        zone_visible_after = scene.zone.isVisible()
        self.assertNotEqual(
            zone_visible_before, zone_visible_after
        )
        self.assertFalse(zone_visible_after)

        # And with 'checked', it shows the zone path
        # Callback triggered via signal
        zone_visible_before = scene.zone.isVisible()
        dialog.enableFresnel.setCheckState(Qt.Checked)
        zone_visible_after = scene.zone.isVisible()
        self.assertNotEqual(
            zone_visible_before, zone_visible_after
        )
        self.assertTrue(zone_visible_after)

    def test_fresnel_callback_affects_frequency_spinbox(self):
        display = self.display
        dialog = display.dialog

        # Calling the fresnel callback with 'Unchecked' disables the frequency
        # spinbox control
        frequency_enabled_before = dialog.frequency.isEnabled()
        display.fresnel_event(Qt.Unchecked)
        frequency_enabled_after = dialog.frequency.isEnabled()
        self.assertNotEqual(
            frequency_enabled_before, frequency_enabled_after
        )
        self.assertFalse(frequency_enabled_after)

        # And with 'checked', it enables the frequency spinbox control
        frequency_enabled_before = dialog.frequency.isEnabled()
        display.fresnel_event(Qt.Checked)
        frequency_enabled_after = dialog.frequency.isEnabled()
        self.assertNotEqual(
            frequency_enabled_before, frequency_enabled_after
        )
        self.assertTrue(frequency_enabled_after)


class TestElevationDisplayFrequencySpin(TestElevationDisplayClass):
    def test_frequency_callback_affects_scene(self):
        display = self.display
        scene = display.scene

        # Check that frequency callback has an affect on the fresnel zone path
        for a_frequency in (100, 1000, 2400):
            zone_rect_before = scene.zone.boundingRect()
            display.freq_event(a_frequency)
            zone_rect_after = scene.zone.boundingRect()
            self.assertNotEqual(
                zone_rect_before, zone_rect_after
            )

    def test_frequency_signal_triggers_callback(self):
        display = self.display
        dialog = display.dialog
        scene = display.scene

        # Check that frequency callback has an affect on the fresnel zone path
        # Callback triggered via signal
        for a_frequency in (100, 1000, 2400):
            zone_rect_before = scene.zone.boundingRect()
            dialog.frequency.setValue(a_frequency)
            zone_rect_after = scene.zone.boundingRect()
            self.assertNotEqual(
                zone_rect_before, zone_rect_after
            )
