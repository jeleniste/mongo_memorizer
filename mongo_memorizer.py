# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mongolizer_layer
                                 A QGIS plugin
 create memory layer from geojsons stored in mongo
                              -------------------
        begin                : 2015-12-05
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Jelen
        email                : godzilalalala@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from mongo_memorizer_dockwidget import mongolizer_layerDockWidget
import os.path

##
from pymongo import MongoClient
from PyQt4.QtCore import QVariant
import simplejson as json
from osgeo import ogr
import re
import qgis.utils
from qgis.core import *
import bson
from types import NoneType
from pymongo import errors as mongoerr

##
##from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog

#from dateutil.parser import parse as dateparse


class mongolizer_layer:
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

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'mongolizer_layer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&mongo_memorizer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'mongolizer_layer')
        self.toolbar.setObjectName(u'mongolizer_layer')

        #print "** INITIALIZING mongolizer_layer"

        self.pluginIsActive = False
        self.dockwidget = None



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
        return QCoreApplication.translate('mongolizer_layer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

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
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/mongolizer_layer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'mongo_memorizer'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING mongolizer_layer"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD mongolizer_layer"

        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&mongo_memorizer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def populate_input_select_collection(self):
        """fill combobox with names from list of collections 
        from actual mongo database"""

        self.dockwidget.input_select_collection.clear()

        self.db = self.mongocli[
                self.dockwidget.input_database_name.currentText()]

        self.dockwidget.input_select_collection.addItems(
                self.db.collection_names())

    def select_collection(self):
        self.collection = self.db[
                self.dockwidget.input_select_collection.currentText()]

        self.dockwidget.load_layer.setEnabled(True)
        self.dockwidget.input_canvas_filter.setEnabled(False)

        self.enable_spat_filtr()



    def enable_spat_filtr(self):
        """try if is posible filter layer by geometry intersection"""

        geomcolname = self.dockwidget.input_geom_coll.text()
        try:
            #enable spat filter
            spatial_query = {"$geoIntersects":
                {"$geometry":
                    json.loads(ogr.CreateGeometryFromWkt(
                        self.iface.mapCanvas().extent().asWktPolygon()).ExportToJson())
                }
            }
            self.collection.find_one({geomcolname : spatial_query})
            self.dockwidget.input_canvas_filter.setEnabled(True)
        except: 
            self.dockwidget.input_canvas_filter.setEnabled(False)
            #QMessageBox.critical(QDialog()
            #        , "eee", "eeeeee")


    def mongo_memorize_execute(self):
        """run transfer of mongo collection, or query into
        memory layer and add it into the layer registry"""
        #option 1
        query = json.loads(self.dockwidget.input_query.toPlainText())

        self.dockwidget.progressBar.setRange(1
                , self.collection.find(query).count())

        self.mongo_memorize(
                collection =  self.collection
                , query = query
                )
        QgsMapLayerRegistry.instance().addMapLayer(self.vl)
    #--------------------------------------------------------------------------

    def try_query(self):
        """try query if is correct and show number of objects in
        result"""

        query = self.dockwidget.input_query.toPlainText()

        try:
            count = self.collection.find(json.loads(query)).count()
            QMessageBox.information(QDialog()
                    , "Query is Valid", "Current query returns %s features"%count)

        except:
            QMessageBox.critical(QDialog()
                    ,"Invalid Query","This querry is probably invalid")

    def mongo_connect(self):
        """create connection and authentize user"""
        self.user = self.dockwidget.input_user.text()
        self.password = self.dockwidget.input_password.text()
        self.auth_db = self.dockwidget.input_auth_db.text()
        self.host = self.dockwidget.input_host.text()
        self.port = self.dockwidget.input_port.text()
        self.pwd = self.dockwidget.input_password.text()
        self.auth_db = self.dockwidget.input_auth_db.text()
        self.auth_mechanism = self.dockwidget.input_auth_method.currentText()
        if self.auth_mechanism == u'':
            self.auth_mechanism = 'SCRAM-SHA-1'




        try:
            self.mongocli = MongoClient(self.host, int(self.port)) 

            #authenticate
            if self.host != "" and self.pwd != "" and self.auth_db != "":
                 self.mongocli[self.auth_db].authenticate(self.user
                         , self.pwd
                         , mechanism = self.auth_mechanism)

            QMessageBox.information(QDialog()
                    , "Connection", "You are succesfully connected into the db")

            try:
                self.dockwidget.input_database_name.clear()
                self.dockwidget.input_database_name.addItems(
                        self.mongocli.database_names())

            except mongoerr.OperationFailure:
                QMessageBox.critical(QDialog()
                        , "Permission error"
                        , "You user probably have not permission for list databases")
                
                self.dockwidget.input_database_name.clear()
                self.dockwidget.input_database_name.addItems(
                        [
                            QInputDialog.getText(QDialog(),"dbname"
                                , "insert database name")[0]
                            ]
                        )
                self.populate_input_select_collection()

                #Disable run button
                self.dockwidget.load_layer.setEnabled(False)


        except:
            QMessageBox.critical(QDialog()
                    ,"Invalid connection","db connection failed")




    def run(self):
        """Run method that loads and starts the plugin"""


        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING mongolizer_layer"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = mongolizer_layerDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

        #mongo connection
        #self.mongocli = MongoClient() #default, moznost zmenit

        #auth mechanisms
        self.dockwidget.input_auth_method.addItems(
                [
                    'SCRAM-SHA-1'
                    , 'MONGODB-CR'
                    , 'x.509'
                    , 'Kerberos'
                    , 'LDAP'
                ]
            )

        #database_names presunout do connect
        #self.dockwidget.input_database_name.addItems(
        #        self.mongocli.database_names())

        #form actions
        self.dockwidget.progressBar.reset()

        self.dockwidget.input_database_name.activated.connect(
                self.populate_input_select_collection)

        self.dockwidget.input_select_collection.activated.connect(
                self.select_collection)

        self.dockwidget.load_layer.clicked.connect(
                self.mongo_memorize_execute)

        #zlobi, widget i logika
        self.dockwidget.input_connect.clicked.connect(
                self.mongo_connect)

        #zlobi, widget i logika
        self.dockwidget.input_try_query.clicked.connect(
                self.try_query)



##------------------------------------
##class mongo_memorize(QgsVectorLayer):
    """make memory layer from geojsons stored in mongo
    """

    ##def __init__(self
    def mongo_memorize(self
            #, dbname = 'ruian'
            #, collectionname = 'KatastralniUzemi'
            , collection
            , query = {}
            , mustr_proprt = None
            , transform_proprt = None
            , geomcolname = 'geometry'
            , host = 'localhost'
            , port = 27017
            #, srid = 4326
            ):
        """Konstruktor
        Create memory layer from geojsons stored in mongo
        :param collection: mongodb collection MongoClient().dbname.collectionname
        :param query: dict with mongo querry loaded from geojson
        default is all features from layer
        :param geomcolname: name of sbdocument with geometry, default is geometry
        it is for case when one feature has more then one geometry
        :param host: default localhost
        :param port: default 27017
        :param srid: default 4326
        :return: populated QgsVectorLayer
        """


        self.vl = QgsVectorLayer()

        #geomcolname
        geomcolname = self.dockwidget.input_geom_coll.text()

        #extent
        #ogr.CreateGeometryFromWkt(iface.mapCanvas().extent().asWktPolygon()).ExportToJson()
        #db.Parcely.find({geometry:{$geoIntersects:{$geometry:j}}})

        if self.dockwidget.input_canvas_filter.checkState():
            spatial_query = {"$geoIntersects":
                {"$geometry":
                    json.loads(ogr.CreateGeometryFromWkt(
                        self.iface.mapCanvas().extent().asWktPolygon()).ExportToJson())
                }
            }
            query[geomcolname] = spatial_query

        #srid
        srid = self.dockwidget.input_srid.text()
        
        #load first object for create table structures
        mustr = collection.find_one({geomcolname:{'$exists':1}})

        #setting up provider
        try:
            self.vl.setDataSource(
                    '%s?crs=EPSG:%s' % (mustr[geomcolname]['type'], str(srid))
                    , collection.name
                    , 'memory')
        except TypeError:
                QMessageBox.critical(QDialog()
                        , "Missing geometry"
                        , "Any of objects in this collection has no geometry\
                                or geometry isn`t valid")
                return(None)



        #provider
        pr = self.vl.dataProvider()
         
        #ISO date template
        isisodate = re.compile('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

        #attrs deffinition
        pr.addAttributes(
            #ogc_fid    
            [QgsField('ogc_fid',QVariant.LongLong)] #LongLong have not proper length
            + [QgsField(k
                , 
                #mongolizer_layer.qgs_attrtypedef(v)
                (lambda i:
                    QVariant.Int if type(i) is int
                    else QVariant.LongLong if type(i) is bson.int64.Int64 
                    else QVariant.Double if type(i) is float
                    else QVariant.String if type(i) is dict #string into json
                    else QVariant.String if type(i) is list #string into json
                    else QVariant.Date if re.match(isisodate, i)
                    else QVariant.String
                    )(v)
                
                ) 
                for k,v in mustr['properties'].iteritems() if type(v) is not NoneType]
        )

        #update layer definition
        self.vl.updateFields() 

        #limit
        limit = self.dockwidget.input_limit.text()
        cur = (collection.find(query) if limit == '' else collection.find(query).limit(int(limit)))

        self.dockwidget.progressBar.setRange(1
                , self.collection.find(query).count())

        for i in cur:
            #create feature
            fet = QgsFeature()

            #test if feature has geometry
            if  geomcolname in i and type(i[geomcolname]) is not NoneType:
                #add geometry
                fet.setGeometry(
                        QgsGeometry.fromWkt(
                            ogr.CreateGeometryFromJson(
                                json.dumps(i[geomcolname])
                                ).ExportToWkt()
                            )
                        )

            #process attrs

            #missing colls
            missing_cols = {k:v for k,v in i['properties'].iteritems() 
                if k not in 
                [f.name() for f in self.vl.pendingFields()]}

            if missing_cols:
                #adding missing colls
                pr.addAttributes(
                    [QgsField(k
                        , 
                        #mongolizer_layer.qgs_attrtypedef(v)
                        (lambda i:
                            QVariant.Int if type(i) is int
                            else QVariant.Double if type(i) is float
                            else QVariant.String if type(i) is dict 
                            else QVariant.String if type(i) is list 
                            else QVariant.LongLong if type(i) is bson.int64.Int64
                            else QVariant.Date if re.match(isisodate, i)
                            else QVariant.String
                            )(v)
                        
                        ) 
                        for k,v in missing_cols.iteritems() if type(v) is not NoneType]
                )

                #update layer def.
                self.vl.updateFields() 

            #fill attributes
            fet.setAttributes(
                map(lambda a: 
                    json.dumps(a, ensure_ascii=False) if (type(a) is dict or type(a) is list)
                    else int(a) if type(a) is bson.int64.Int64
                    else a,
                    (
                        #[int(i['_id'])] #ogc_fid #because of object id, is not possible to transform it to int
                        [str(i['_id'])] #ogc_fid
                        #properties from mustr
                        + [i['properties'][field.name()] 
                            if field.name() in i['properties'] else None
                            for field in self.vl.pendingFields() 
                            if field.name() not in ['ogc_fid']]
                    )
                )
            )

            pr.addFeatures([fet])

            self.dockwidget.progressBar.setValue(
                    self.dockwidget.progressBar.value() + 1)
        

        self.vl.updateExtents()
