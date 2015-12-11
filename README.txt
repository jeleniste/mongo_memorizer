qgis plugin for create memory layer from geojsons stored in mongodb
Geojson should like in this fashion

import of sample data:
   mongoimport --db mongo_memorizer --collection Parcely --drop --file sample.json

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

In this version dont work:
