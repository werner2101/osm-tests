

OSMFILES="../../osm_files/"
OUTDIR2="../../data/02_Relationstypen/"
OUTDIR7="../../data/07_watershed/"
PLANET="/osm/planet-latest.osm"

WATERSHED_TEMP="/osm/waterway_temp/"


#################### planet
planet:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(PLANET) | \
	  ./src/watershed.py filter $(OSMFILES)planet_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(PLANET) | \
	  ./src/watershed.py filter $(OSMFILES)planet_waterwayrelations.osm

	cat $(OSMFILES)planet_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)planet/ $(OSMFILES)planet_waterwayrelations.osm

	cat $(OSMFILES)planet_waterwayrelations.osm | ./src/relationroles.py $(OUTDIR2)planet/relationroles.txt

riverbank:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)russia-european-part.osm.bz2 | \
	  ./src/riverbank.py filter au

	  ./src/riverbank.py analyse au au

#################### continents
africa:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)africa.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)africa_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)africa.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)africa_waterwayrelations.osm

	cat $(OSMFILES)africa_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)africa/ $(OSMFILES)africa_waterwayrelations.osm

	cat $(OSMFILES)africa_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)africa/waterwaylist.txt

	bzcat $(OSMFILES)africa_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)africa/relationroles.txt

australia:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)australia.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)au_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)australia.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)au_waterwayrelations.osm

	cat $(OSMFILES)au_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)au/ $(OSMFILES)au_waterwayrelations.osm

	cat $(OSMFILES)au_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)au/waterwaylist.txt

	bzcat $(OSMFILES)au_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)au/relationroles.txt

south-america:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)south-america.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)south-america_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)south-america.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)south-america_waterwayrelations.osm

	cat $(OSMFILES)south-america_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)south-america/ $(OSMFILES)south-america_waterwayrelations.osm

	cat $(OSMFILES)south-america_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)south-america/waterwaylist.txt

	bzcat $(OSMFILES)south-america_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)south-america/relationroles.txt


#################### countries

austria:
	 ../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)austria.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)at_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)austria.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)at_waterwayrelations.osm

	cat $(OSMFILES)at_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)at/ $(OSMFILES)at_waterwayrelations.osm

	cat $(OSMFILES)at_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)at/waterwaylist.txt

	bzcat $(OSMFILES)at_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)at/relationroles.txt

france:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)france.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)fr_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)france.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)fr_waterwayrelations.osm

	cat $(OSMFILES)fr_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)fr/ $(OSMFILES)fr_waterwayrelations.osm

	cat $(OSMFILES)fr_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)fr/waterwaylist.txt

	bzcat $(OSMFILES)fr_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)fr/relationroles.txt

germany:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)germany.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)de_waterways.osm
	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)germany.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)de_waterwayrelations.osm

	cat $(OSMFILES)de_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)de/ $(OSMFILES)de_waterwayrelations.osm

	cat $(OSMFILES)de_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)de/waterwaylist.txt

	bzcat $(OSMFILES)de_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)de/relationroles.txt

great_britain:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)great_britain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)uk_waterways.osm
	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)great_britain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)uk_waterwayrelations.osm

	cat $(OSMFILES)uk_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)uk/ $(OSMFILES)uk_waterwayrelations.osm

	cat $(OSMFILES)uk_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)uk/waterwaylist.txt

	bzcat $(OSMFILES)uk_relations.osm.bz2 | ./src/relationroles.py  $(OUTDIR2)uk/relationroles.txt

italy:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)italy.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)it_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)italy.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)it_waterwayrelations.osm

	cat $(OSMFILES)it_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)it/ $(OSMFILES)it_waterwayrelations.osm

	cat $(OSMFILES)it_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)it/waterwaylist.txt

	bzcat $(OSMFILES)it_relations.osm.bz2 | ./src/relationroles.py  $(OUTDIR2)it/relationroles.txt

spain:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)spain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)es_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)spain.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)es_waterwayrelations.osm

	cat $(OSMFILES)es_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)es/ $(OSMFILES)es_waterwayrelations.osm

	cat $(OSMFILES)es_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)es/waterwaylist.txt

	bzcat $(OSMFILES)es_relations.osm.bz2 | ./src/relationroles.py  $(OUTDIR2)es/relationroles.txt

switzerland:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)switzerland.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)ch_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)switzerland.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)ch_waterwayrelations.osm

	cat $(OSMFILES)ch_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)ch/ $(OSMFILES)ch_waterwayrelations.osm

	cat $(OSMFILES)ch_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)ch/waterwaylist.txt

	bzcat $(OSMFILES)ch_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)ch/relationroles.txt

portugal:
	../python-osm/src/osm/osmdb.py \
	  --ways_relations=/dev/stdout $(OSMFILES)portugal.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)pt_waterways.osm

	../python-osm/src/osm/osmdb.py \
	  --relations=/dev/stdout $(OSMFILES)portugal.osm.bz2 | \
	  ./src/watershed.py filter $(OSMFILES)pt_waterwayrelations.osm

	cat $(OSMFILES)pt_waterways.osm |./src/watershed.py createtables $(WATERSHED_TEMP)

	./src/watershed.py analyse $(WATERSHED_TEMP) $(OUTDIR7)pt/ $(OSMFILES)pt_waterwayrelations.osm

	cat $(OSMFILES)pt_waterways.osm | ./src/watershed.py waterwaylist $(WATERSHED_TEMP)relation_way $(OUTDIR7)pt/waterwaylist.txt

	bzcat $(OSMFILES)pt_relations.osm.bz2 | ./src/relationroles.py $(OUTDIR2)pt/relationroles.txt


