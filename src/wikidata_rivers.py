# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 09:21:51 2014

@author: werner
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json

#################### CONST
OUTDIR = '../data/08_wiki_icons/'

#################### CLASS
class River(object):
    def __init__(self,wikidata_id):
        self.wd_id = wikidata_id
        self.mouth = -1
        self.sidestreams = []
        self.mainstem = False
        self.osm_relid = ''
        self.coords = ('','')
        self.countries = []
        self.continents = []
        
    def write(self, level, visited):
        visited.discard(self.wd_id)
        print '\t'.join(['.'*(level-1)+str(level), str(self.wd_id), self.osm_relid,
                         str(self.mainstem), str(self.mouth),
                         self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                         ' '.join([str(i) for i in self.continents]),
                         ' '.join([str(i) for i in self.countries])
                         ])
        for ss in self.sidestreams:
            ss.write(level+1, visited)
            
    def __cmp__(self, other):
        assert isinstance(other, River)
        return cmp(self.mouth, other.mouth)


#################### FUNCTIONS
def readjson(filename):
    rivers = {}  # id --> River
    jdata = json.load(open(filename))
    unknown_mouth = []
    for wd_id in jdata['items']:
        rivers[wd_id] = River(wd_id)
    for wd_id, type_, relid in jdata['props']['402']:
        rivers[wd_id].osm_relid = relid
    for wd_id, type_, wd_id2 in jdata['props']['403']:
        if wd_id2 in rivers:
            rivers[wd_id2].sidestreams.append(rivers[wd_id])
            #print '.'
        else:
            unknown_mouth.append(rivers[wd_id])
            #print 'mouth %s does not exist' % wd_id2
        rivers[wd_id].mouth = wd_id2
    for wd_id, type_, instance in jdata['props']['31']:
        if instance == 573344:
            rivers[wd_id].mainstem=True
    for wd_id, type_, coord in jdata['props']['625']:
        rivers[wd_id].coords = coord.split('|')[:2]
    for wd_id, type_, country in jdata['props']['17']:
        rivers[wd_id].countries.append(country)
    for wd_id, type_, continent in jdata['props']['30']:
        rivers[wd_id].continents.append(continent)
    return rivers, unknown_mouth

#################### MAIN

rivers, unknown_mouth = readjson(sys.argv[1])

visited = set(rivers.keys())

for river in sorted(unknown_mouth):
    river.write(1, visited)
    
for river in rivers.values():
    if river.mouth == -1:
        river.write(1,visited)
        
