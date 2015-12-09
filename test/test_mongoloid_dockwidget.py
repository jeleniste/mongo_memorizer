# coding=utf-8
"""DockWidget test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'godzilalalala@gmail.com'
__date__ = '2015-12-05'
__copyright__ = 'Copyright 2015, Jelen'

import unittest

from PyQt4.QtGui import QDockWidget

from mongo_memorizer_dockwidget import mongolizer_layerDockWidget

from utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class mongolizer_layerDockWidgetTest(unittest.TestCase):
    """Test dockwidget works."""

    def setUp(self):
        """Runs before each test."""
        self.dockwidget = mongolizer_layerDockWidget(None)

    def tearDown(self):
        """Runs after each test."""
        self.dockwidget = None

    def test_dockwidget_ok(self):
        """Test we can click OK."""
        pass

if __name__ == "__main__":
    suite = unittest.makeSuite(mongolizer_layerDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

