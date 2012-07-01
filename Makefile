

OSMFILES="../../osm_files/"
OUTDIR="../../data/07_watershed/"
PLANET="/osm/planet-latest.osm"

WATERSHED_TEMP="/osm/waterway_temp/"


australia:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)australia.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)au_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)australia.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)au_waterwayrelations.osm

	cat $(OSMFILES)au_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)au/ $(OSMFILES)au_waterwayrelations.osm

	cat $(OSMFILES)au_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)au/waterwaylist.txt

austria:
	 ../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)austria.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)at_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)austria.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)at_waterwayrelations.osm

	cat $(OSMFILES)at_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)at/ $(OSMFILES)at_waterwayrelations.osm

	cat $(OSMFILES)at_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)at/waterwaylist.txt

france:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)france.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)fr_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)france.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)fr_waterwayrelations.osm

	cat $(OSMFILES)fr_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)fr/ $(OSMFILES)fr_waterwayrelations.osm

	cat $(OSMFILES)fr_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)fr/waterwaylist.txt

germany:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)germany.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)de_waterways.osm
	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)germany.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)de_waterwayrelations.osm

	cat $(OSMFILES)de_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)de/ $(OSMFILES)de_waterwayrelations.osm

	cat $(OSMFILES)de_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)de/waterwaylist.txt

italy:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)italy.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)it_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)italy.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)it_waterwayrelations.osm

	cat $(OSMFILES)it_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)it/ $(OSMFILES)it_waterwayrelations.osm

	cat $(OSMFILES)it_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)it/waterwaylist.txt

spain:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)spain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)es_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)spain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)es_waterwayrelations.osm

	cat $(OSMFILES)es_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)es/ $(OSMFILES)es_waterwayrelations.osm

	cat $(OSMFILES)es_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)es/waterwaylist.txt

switzerland:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)switzerland.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)ch_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)switzerland.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)ch_waterwayrelations.osm

	cat $(OSMFILES)ch_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)ch/ $(OSMFILES)ch_waterwayrelations.osm

	cat $(OSMFILES)ch_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR)ch/waterwaylist.txt


planet:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(PLANET) | \
	  ./src/watershed.py filter $(OSMFILES)planet_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(PLANET) | \
	  ./src/watershed.py filter $(OSMFILES)planet_waterwayrelations.osm

	cat $(OSMFILES)planet_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)planet/ $(OSMFILES)planet_waterwayrelations.osm
