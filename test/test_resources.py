# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import unittest
import os

from PyQt4.QtGui import QIcon


class EleViewDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/EleView/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

    def test_correct_customwidget_string(self):
        #
        filename = os.path.join(
            os.path.dirname(__file__),
            "..",
            "EleView",
            "main_dialog.ui"
        )
        count = 0
        with open(filename) as fp:
            for line in fp:
                self.assertFalse("qgsprojectionselectionwidget.h" in line)
                if "<header>qgis.gui</header>" in line:
                    count += 1
        self.assertEqual(count, 1)
