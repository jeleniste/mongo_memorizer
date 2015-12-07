# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mongolizer_layer
                                 A QGIS plugin
 create memory layer from geojsons stored in mongo
                             -------------------
        begin                : 2015-12-05
        copyright            : (C) 2015 by Jelen
        email                : godzilalalala@gmail.com
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
    """Load mongolizer_layer class from file mongolizer_layer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mongoloid import mongolizer_layer
    return mongolizer_layer(iface)
