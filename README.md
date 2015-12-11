***************
mongo memorizer
***************

Functionality
=============

Mongo memorizer select geojsons from mongo database and make qgis memory layer
from this. There is possible use mongo query (it must be valid json).

There is possible to define host, password and authentication parameters, if it
is nescessary.

.. figure:: screenshots/mongo_memorizer.png
   :width: 30em
   :align: center

Data
====

Data must be valid geojson, with one exception, there is possible use more than
one subelement with geometry (but name of alternative geometry must be different
from geometry). Or geometry can have different name (for example if you need to
use bounding box for filtering etc).

If you want to use spatial index, geometry must be valid (sample data aren`t).

Geojson should be in this fashion:

.. code-block:: json

   {
           "_id" : NumberLong("31525565010"),
           "geometry" : {
                   "type" : "Polygon",
                   "coordinates" : [
                           [
                                   [
                                           12.639899812059387,
                                           50.18799746731742
                                   ],
                                   [
                                           12.63980863624595,
                                           50.188038896579606
                                   ],
                                   [
                                           12.63985711214033,
                                           50.18808683912924
                                   ],
                                   [
                                           12.639879484859948,
                                           50.18807632413388
                                   ],
                                   [
                                           12.639951960147378,
                                           50.18804378805749
                                   ],
                                   [
                                           12.639899812059387,
                                           50.18799746731742
                                   ]
                           ]
                   ]
           },
           "type" : "Feature",
           "properties" : {
                   "PododdeleniCisla" : 20,
                   "ZpusobyVyuzitiPozemku" : 23,
                   "KmenoveCislo" : 446,
                   "PlatiOd" : "2013-09-27T00:00:00",
                   "VymeraParcely" : 52,
                   "KatastralniUzemi" : {
                           "Kod" : 752223
                   },
                   "DruhCislovaniKod" : 2,
                   "IdTransakce" : 355913,
                   "DruhPozemkuKod" : 14,
                   "RizeniId" : NumberLong("27044904010"),
                   "Id" : NumberLong("31525565010")
           },
           "geometry_p" : {
                   "type" : "Point",
                   "coordinates" : [
                           12.639870657036909,
                           50.18803879095269
                   ]
           }
   }

Sample data can be imported like this (if you are on localhost and mongo runs
without authentization)

.. code-block:: bash

   mongoimport --db mongo_memorizer --collection Parcely --drop --file sample.json


Elements in one collection should have the same geometry type (if they have the
same name of geometry subdocument)

Connecting
==========

Default for connection is port 27017 on localhost. I you run mongo without
authentication, you could't change anything. But you can change port, host, set
user and password and select authentication method, SCRAM-SHA-1 is default.
You should set authentication database too (it is not the same as database with
your features).

.. figure:: screenshots/connection.png

If your user have not permission for *show databases* in mongo, plugin will not
be able to fill combo box with databases and you will be asked for set name of
database you want to use.

Selecting collection
====================

.. figure:: screenshots/collection_select.png

If you are connected, you can select database and collection with your data. You
must select database to enable combo box with collections. After you select
collection, run button will be enabled. 

You can use limit for obtain only few elements, and check box for filtering by
map canvas will be enabled, if your geometry is in lat/lon. But be careful on
project SRID.

Querying
========

.. figure:: screenshots/query.png

You can filter data by querry (but if you use geometry querry and filter by map
canvas, your querry will be overvriten). You can try, if your query is valid and
if is, count of features in result will be returned. Querry must be valid json.

Query examples
--------------

Features with geometry

.. code-block:: json

   {"geometry":{"$exists":1}}

Feature has _id with some value

.. code-block:: json

   {"_id":32097350010}

Value of *Id* in properties has some value.

.. code-block:: json

   {"properties.Id": 32097350010}
