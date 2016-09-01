# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EleView
                                 A QGIS plugin
 Allows easy extrapolation from a vector elevation layer to determine the
 elevation between two points
                             -------------------
        begin                : 2015-04-05
        copyright            : (C) 2015 by -
        email                : james.fysh@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load EleView class from file EleView.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .EleView import PluginManager
    return PluginManager(iface)
