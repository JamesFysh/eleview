# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EleView
                                 A QGIS plugin
 Allows easy extrapolation from a vector elevation layer to determine the
 elevation between two points
                              -------------------
        begin                : 2015-04-05
        git sha              : $Format:%H$
        copyright            : (C) 2015 by -
        email                : james.fysh@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
from functools import partial

from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon

from qgis.core import QgsMessageLog, QgsCoordinateReferenceSystem

# Initialize Qt resources from file resources.py
from . import resources_rc

from .CanvasManager import CanvasManager
from .Constants import PT1, PT2
from .LayerManager import LayerManager
from .SettingsManager import SettingsManager, PluginSettings
from .PluginDialogs import EleViewMainDialog
from .ElevationDisplay import ElevationDisplay

log = QgsMessageLog.instance()


class PluginManager(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.points = {PT1: None, PT2: None}

        self.canvas_mgr = CanvasManager(iface.mapCanvas(), self.set_pt)
        self.layer_mgr = LayerManager()
        self.settings = SettingsManager()

        # Create the dialog (after translation) and keep reference
        self.dlg = EleViewMainDialog()
        self.display = None

        # Declare instance attributes
        self.actions = []
        self.menu = u'&Elevation Viewer'

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=False,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.iface.addToolBarIcon(action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/EleView/icon.png'
        # Add menu item
        self.add_action(
            icon_path,
            text=u'EleView',
            callback=self.run,
            parent=self.iface.mainWindow())

        self.canvas_mgr.initialize()

        for widget, signal, method in (
            (
                self.dlg.capturePoint1,
                "clicked()",
                partial(self.canvas_mgr.enable_capture, PT1)
            ),
            (
                self.dlg.capturePoint2,
                "clicked()",
                partial(self.canvas_mgr.enable_capture, PT2)
            ),
            (
                self.dlg.cboxElevLayer,
                "currentIndexChanged(const QString&)",
                self.layer_selection_changed
            ),
            (
                self.dlg.btnShowElevation,
                "clicked()",
                self.show_elevation_dialog
            ),
        ):
            QObject.connect(
                widget,
                SIGNAL(signal),
                method
            )

    def cleanup(self):
        if self.display:
            self.display.hide()
            self.display = None
        self.canvas_mgr.cleanup()

        self.settings.write(
            PluginSettings(
                layer_name=self.dlg.cboxElevLayer.currentText(),
                layer_attr=self.dlg.cboxElevAttr.currentText(),
                proj_wkt=self.dlg.cboxElevProj.crs().toWkt()
            )
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(u'&Elevation Viewer', action)
            self.iface.removeToolBarIcon(action)
        self.cleanup()

    def run(self):
        """Run method that performs all the real work"""
        self.layer_mgr.initialize()

        # Populate layer map, dialog 'cboxElevLayer' with layer list
        self.dlg.cboxElevLayer.addItems(self.layer_mgr.get_layer_names())

        # Attempt to load settings
        plugin_settings = self.settings.read()
        layer_idx = self.dlg.cboxElevLayer.findText(plugin_settings.layer_name)
        if layer_idx != -1:
            self.dlg.cboxElevLayer.setCurrentIndex(layer_idx)
        attr_idx = self.dlg.cboxElevAttr.findText(plugin_settings.layer_attr)
        if attr_idx != -1:
            self.dlg.cboxElevAttr.setCurrentIndex(attr_idx)
        if plugin_settings.proj_wkt:
            self.dlg.cboxElevProj.setCrs(
                QgsCoordinateReferenceSystem(plugin_settings.proj_wkt)
            )

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.exec_()

        # Clean up, after the tool closes
        self.cleanup()

    def layer_selection_changed(self, layer_name):
        log.logMessage(
            "Selected layer changed to {}".format(layer_name),
            level=QgsMessageLog.INFO
        )

        # Update layer-attribute list
        self.dlg.cboxElevAttr.clear()
        self.dlg.cboxElevAttr.addItems(
            self.layer_mgr.get_attrs_for_layer(layer_name)
        )

    def set_pt(self, point, value):
        self.points[point] = value
        {
            PT1: self.dlg.point1,
            PT2: self.dlg.point2,
        }.get(point).setText(str(value))
        self.dlg.raise_()

        if all(x is not None for x in self.points.values()):
            self.dlg.btnShowElevation.setEnabled(True)

    def show_elevation_dialog(self):
        current_layer = self.layer_mgr.get_layer_by_name(
            self.dlg.cboxElevLayer.currentText()
        )
        self.display = ElevationDisplay(
            self.points[PT1],
            self.points[PT2],
            current_layer,
            self.dlg.cboxElevAttr.currentText(),
            self.canvas_mgr.get_canvas_crs(),
            self.dlg.cboxElevProj.crs()
        )
        self.display.show()
        self.dlg.btnShowElevation.setEnabled(False)
