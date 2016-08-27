# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EleView
                                 A QGIS plugin
 Allows easy extrapolation from a vector elevation layer to determine the elevation between two points
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

from qgis.core import (
    QgsMessageLog, QgsPoint, QgsProject, QgsCoordinateReferenceSystem,
)
from qgis.gui import (
    QgsMapToolEmitPoint
)
from PyQt4.QtCore import (
    QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL,
)
from PyQt4.QtGui import (
    QAction, QIcon
)

# Layers
from processing import getVectorLayers
from processing.core.parameters import ParameterVector

# Initialize Qt resources from file resources.py
from . import resources_rc

# Import the code for the dialog
from .EleView_dialogs import EleViewMainDialog
from .EleView_display import ElevationDisplay


class EleView:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # Get a reference to the mapCanvas
        self.canvas = self.iface.mapCanvas()
        # And create an object to capture canvas clicks
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.previousTool = None
        self.ptCapturing = None
        self.ptsCaptured = {}
        # Layer handling
        self.curr_layer = None
        self.layer_map = {}
        self.layer_attr_map = {}
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'EleView_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = EleViewMainDialog()
        self.display = None

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Elevation Viewer')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('EleView', message)

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
            text=self.tr(u'EleView'),
            callback=self.run,
            parent=self.iface.mainWindow())

        for widget, signal, method in (
            (
                self.clickTool,
                "canvasClicked(const QgsPoint &, Qt::MouseButton)",
                self.handleCanvasClick
            ),
            (
                self.dlg.capturePoint1,
                "clicked()",
                partial(self.enableCapture, self.dlg.point1)
            ),
            (
                self.dlg.capturePoint2,
                "clicked()",
                partial(self.enableCapture, self.dlg.point2)
            ),
            (
                self.dlg.cboxElevLayer,
                "currentIndexChanged(const QString&)",
                self.handleLayerChange
            ),
            (
                self.dlg.btnShowElevation,
                "clicked()",
                self.showElevClicked
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
        if self.canvas.mapTool() == self.clickTool:
            self.canvas.setMapTool(self.previousTool)

        proj = QgsProject.instance()
        proj.writeEntry(
            "eleview",
            "layername",
            self.dlg.cboxElevLayer.currentText()
        )
        proj.writeEntry(
            "eleview",
            "layerattr",
            self.dlg.cboxElevAttr.currentText()
        )
        proj.writeEntry(
            "eleview",
            "projdefn",
            self.dlg.cboxElevProj.crs().toWkt()
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Elevation Viewer'),
                action)
            self.iface.removeToolBarIcon(action)
        self.cleanup()

    def run(self):
        """Run method that performs all the real work"""
        # Populate layer map, dialog 'cboxElevLayer' with layer list
        self.layer_map = {
            str(layer.name()): layer
            for layer in getVectorLayers([ParameterVector.VECTOR_TYPE_LINE])
        }
        self.dlg.cboxElevLayer.addItems(sorted(self.layer_map.keys()))

        # Attempt to load settings
        proj = QgsProject.instance()
        lname = proj.readEntry("eleview", "layername", "???")[0]
        layer_idx = self.dlg.cboxElevLayer.findText(lname)
        if layer_idx != -1:
            self.dlg.cboxElevLayer.setCurrentIndex(layer_idx)
        lattr = proj.readEntry("eleview", "layerattr", "???")[0]
        attr_idx = self.dlg.cboxElevAttr.findText(lattr)
        if attr_idx != -1:
            self.dlg.cboxElevAttr.setCurrentIndex(attr_idx)
        pname = proj.readEntry("eleview", "projdefn", "???")[0]
        if pname != "???":
            self.dlg.cboxElevProj.setCrs(
                QgsCoordinateReferenceSystem(pname)
            )

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.exec_()

        # Clean up, after the tool closes
        self.cleanup()

    def enableCapture(self, ptCapturing):
        self.ptCapturing = ptCapturing
        if self.canvas.mapTool() is not self.clickTool:
            self.previousTool = self.canvas.mapTool()
            self.canvas.setMapTool(self.clickTool)

    def handleLayerChange(self, layerName):
        QgsMessageLog.logMessage(
            "Layer Name changing to {}".format(layerName),
            level=QgsMessageLog.INFO
        )
        # Build layer-attribute list
        self.curr_layer = self.layer_map[layerName]
        field_list = self.curr_layer.pendingFields()
        self.layer_attr_map = {
            str(field.name()): field
            for field in field_list
        }
        # Update layer-attribute list
        self.dlg.cboxElevAttr.clear()
        self.dlg.cboxElevAttr.addItems(sorted(self.layer_attr_map.keys()))

    def handleCanvasClick(self, pt, btn):
        QgsMessageLog.logMessage(
            "Mouse-click: {}, {}".format(pt, btn), 
            level=QgsMessageLog.INFO
        )
        self.ptsCaptured[self.ptCapturing] = QgsPoint(pt)
        self.ptCapturing.setText(str(pt))
        self.dlg.raise_()
        
        if len(self.ptsCaptured) == 2:
            self.dlg.btnShowElevation.setEnabled(True)

    def showElevClicked(self):
        self.display = ElevationDisplay(
            self.iface,
            self.ptsCaptured.values(),
            self.curr_layer,
            self.dlg.cboxElevAttr.currentText(),
            self.dlg.cboxElevProj.crs()
        )
        self.display.show()
        self.dlg.btnShowElevation.setEnabled(False)
