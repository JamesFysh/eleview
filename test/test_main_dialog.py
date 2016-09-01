import unittest

from EleView.EleView import EleView

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class DummyInterface(object):
    def mapCanvas(self):
        return None


class TestMainDialog(unittest.TestCase):
    def setUp(self):
        self.iface = DummyInterface()
        self.dialog = EleView(self.iface)

    def test_basic_construction(self):
        self.assertIsNotNone(self.dialog)
