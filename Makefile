

OSMFILES="../../osm_files/"
OUTDIR="../../data/08_watershed2/"
PLANET="/osm/planet-latest.osm"

WATERSHED_TEMP=/osm/waterway_temp/


australia:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)australia.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)au_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)australia.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)au_waterwayrelations.osm

	cat $(OSMFILES)au_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)au/ $(OSMFILES)au_waterwayrelations.osm

spain:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)spain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)es_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)spain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)es_waterwayrelations.osm

	cat $(OSMFILES)es_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)es/ $(OSMFILES)es_waterwayrelations.osm

germany:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)germany.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)de_waterways.osm
	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)germany.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)de_waterwayrelations.osm

	cat $(OSMFILES)de_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)de/ $(OSMFILES)de_waterwayrelations.osm

planet:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(PLANET) | \
	  ./src/watershed.py filter $(OSMFILES)planet_waterways.osm
	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(PLANET) | \
	  ./src/watershed.py filter $(OSMFILES)planet_waterwayrelations.osm

	cat $(OSMFILES)planet_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR)planet/ $(OSMFILES)planet_waterwayrelations.osm
