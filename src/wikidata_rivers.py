# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 09:21:51 2014

@author: werner
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
import urllib
if sys.version_info < (3,0):
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    
#################### CONST
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
OUTDIR = os.path.join(SCRIPTDIR, '../../../data/07.1_watershed_data/')

TOOLSERVER='https://wdq.wmflabs.org/api'

WATERWAYS = [('573344', 'mainstem'),
             ('4022', 'river'),
             ('47521', 'stream'),
             ('27250','tidal creek'),
             ('12284', 'canal'),
             ('523166','gracht'),
             ('34038','waterfall'),
             ('355304','watercourse')]
             
WATERAREAS = [('9430','ocean'),
              ('165','sea'),
              ('986177','mediteranean sea'),
              ('1973404','inland sea'),
              ('204894','marginal sea'),
              ('37901','strait'),
              ('1322134','gulf'),
              ('39594','bay'),
              ('283202','harbor'),
              ('1172599','inlet'),
              ('491713','sound'),
              ('31615','cove'),
              ('558116','firth'),
              ('45776','fjord'),
              ('319714','fjard'),
              ('47053','estuary'),
              ('170321','wetland'),
              ('5926864','group of lakes'),
              ('23397','lake'),
              ('211302','glacial lake'),
              ('188025','salt lake'),
              ('935277','salt pan'),
              ('6341928','rift lake'),
              ('204324','crater lake'),
              ('12779976','endoheic lake'),
              ('7205721','pluvial lake'),
              ('2915867','rift valley lake'),
              ('1165822','meromictic lake'),
              ('4862338','monomictic lake'),
              ('131681','reservoir'),
              ('2623499','ribbon lake'),
              ('3253281','pond'),
              ('187223','lagoon'),
              ('3705882', 'albufera')  # something like a lagoon
              ]
             

#################### CLASS
class River(object):
    def __init__(self,wikidata_id, _type):
        self.wd_id = wikidata_id
        self.mouth_waterway = -1
        self.mouth_area = -1
        self.sidestreams = []
        self._type = _type
        self.osm_relid = ''
        self.coords = ('','')
        self.adminarea = []
        self.countries = []
        self.continents = []
        
    def traverse(self, level, visited, objlist):
        visited.discard(self.wd_id)
        objlist.append((self,level))

        for ss in self.sidestreams:
            if level < 20:
                ss.traverse(level+1, visited, objlist)

    def write(self, level):
        if self.mouth_waterway > 0:
            mouth = self.mouth_waterway
        else:
            mouth = self.mouth_area
        return '\t'.join(['.'*(level-1)+str(level), str(self.wd_id), self.osm_relid,
                         str(self._type), str(mouth),
                         self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                         ' '.join([str(i) for i in self.continents]),
                         ' '.join([str(i) for i in self.countries]),
                         ' '.join([str(i) for i in self.adminarea])
                         ])
            
    def __cmp__(self, other):
        assert isinstance(other, River)
        return cmp((self.mouth_waterway, self.wd_id), (other.mouth_waterway, other.wd_id))

class Waterarea(object):
    def __init__(self, wikidata_id, _type):
        self.wd_id = wikidata_id
        self._type = _type
        self.part_of = -1
        self.inflows = []
        self.subparts = []
        self.osm_relid = ''
        self.coords = ('','')
        self.adminarea = []
        self.countries = []
        self.continents = []

    def traverse(self, level, visited, objlist):
        visited.discard(self.wd_id)
        objlist.append((self, level))

        for sp in self.subparts:
            if level < 20:
                sp.traverse(level+1, visited, objlist)
        for river in self.inflows:
            if level < 20:
                river.traverse(level+1, visited, objlist)

    def write(self, level):
        return '\t'.join(['.'*(level-1)+str(level), str(self.wd_id), self.osm_relid,
                         str(self._type), str(self.part_of),
                         self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                         ' '.join([str(i) for i in self.continents]),
                         ' '.join([str(i) for i in self.countries]),
                         ' '.join([str(i) for i in self.adminarea])
                         ])
            
    def __cmp__(self, other):
        assert isinstance(other, Waterarea)
        return cmp((self.wd_id), (other.wd_id))
        
#################### FUNCTIONS
def readjson_waterways():
    """
    reads a data request from wikidata. The following request is used to 
    retrieve attributes of rivers:
    
    https://wdq.wmflabs.org/api?q=claim[31:4022]&props=402,403,31,625,17,30,131
    """
    rivers = {}  # id --> River
    for i_id, r_type in WATERWAYS:
        filename = os.path.join(OUTDIR, r_type + '.json')
        print filename
        data = open(filename).read().replace('[],','')  ## fixes wdq bug
        data = data.replace(',[]','')                  ## fix for same bug
        jdata = json.loads(data)
        for wd_id in jdata['items']:
            if wd_id not in rivers:
                rivers[wd_id] = River(wd_id,r_type)
        for wd_id, type_, relid in jdata['props'].get('402',[]):
            rivers[wd_id].osm_relid = relid
        for wd_id, type_, wd_id2 in jdata['props'].get('403',[]):
            rivers[wd_id].mouth_waterway = wd_id2
        for wd_id, type_, coord in jdata['props'].get('625',[]):
            rivers[wd_id].coords = coord.split('|')[:2]
        for wd_id, type_, country in jdata['props'].get('17',[]):
            rivers[wd_id].countries.append(country)
        for wd_id, type_, continent in jdata['props'].get('30',[]):
            rivers[wd_id].continents.append(continent)
        for wd_id, type_, adminarea in jdata['props'].get('131',[]):
            rivers[wd_id].adminarea.append(adminarea)

    return rivers

def readjson_waterareas():
    """
    reads a json file of the data request about informations of waterarea data
    to retrive informations about water areas, where a river can flow to.
    """
    waterareas = {}
    for i_id, r_type in WATERAREAS:
        filename = os.path.join(OUTDIR, r_type + '.json')
        print filename
        data = open(filename).read().replace('[],','')  ## fixes wdq bug
        data = data.replace(',[]','')                  ## fix for same bug
        jdata = json.loads(data)
        for wd_id in jdata['items']:
            if wd_id not in waterareas:
                waterareas[wd_id] = Waterarea(wd_id,r_type)
        for wd_id, type_, relid in jdata['props'].get('402',[]):
            waterareas[wd_id].osm_relid = relid
        for wd_id, type_, wd_id2 in jdata['props'].get('361',[]):
            waterareas[wd_id].part_of = wd_id2
        for wd_id, type_, coord in jdata['props'].get('625',[]):
            waterareas[wd_id].coords = coord.split('|')[:2]
        for wd_id, type_, country in jdata['props'].get('17',[]):
            waterareas[wd_id].countries.append(country)
        for wd_id, type_, continent in jdata['props'].get('30',[]):
            waterareas[wd_id].continents.append(continent)
        for wd_id, type_, adminarea in jdata['props'].get('131',[]):
            waterareas[wd_id].adminarea.append(adminarea)

    return waterareas

def retrieve_wikidata():
    for i_id, r_type in WATERWAYS:
        print i_id, r_type
        url = TOOLSERVER + '?q=claim[31:%s]&props=402,403,31,625,17,30,131' %i_id
        answ = urllib.urlopen(url)
        data = answ.read()
        open(os.path.join(OUTDIR, r_type + '.json'), 'wt').write(data)
    
    for i_id, r_type in WATERAREAS:
        print i_id, r_type
        url = TOOLSERVER + '?q=claim[31:%s]&props=402,31,625,17,30,131,361' %i_id
        answ = urllib.urlopen(url)
        data = answ.read()
        open(os.path.join(OUTDIR, r_type + '.json'), 'wt').write(data)
      
def analyse_wikidata():
    rivers = readjson_waterways()
    waterareas = readjson_waterareas()
    
    no_mouth = []
    unknown_mouth = []    
    for w_id, ww in rivers.items():
        if ww.mouth_waterway in rivers:
            rivers[ww.mouth_waterway].sidestreams.append(ww)
        elif ww.mouth_waterway in waterareas:
            waterareas[ww.mouth_waterway].inflows.append(ww)          
        elif ww.mouth_waterway > 0:
            unknown_mouth.append(ww)
        else:
            no_mouth.append(ww)

    no_part = []
    for w_id, wa, in waterareas.items():
        if wa.part_of in waterareas:
            waterareas[wa.part_of].subparts.append(wa)
        else:
            no_part.append(wa)
    
    visited = set(rivers.keys()) | set(waterareas.keys())
    objlist = []

    for wa in sorted(no_part):
        if not (len(wa.subparts) + len(wa.inflows)):
            continue
        wa.traverse(1,visited,objlist)
        
    for river in sorted(unknown_mouth):
        river.traverse(1, visited, objlist)
    
    for river in sorted(no_mouth):
        if river.mouth_waterway == -1:
            river.traverse(1,visited, objlist)
    
    fid = open(os.path.join(OUTDIR, 'wikidata_tree.txt'), 'wt')
    fid.write('\t'.join(['Level','wd_id','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
    for obj, level in objlist:
        fid.write(obj.write(level) + '\n')
        
    countries = set()
    for i, r in rivers.iteritems():
        countries |= set(r.countries)
    
    for country in countries:
        levelstack = [-1]*100
        countrystack = [-1]*100
        selection = set()
        for i, objl in enumerate(objlist):
            obj, level = objl
            levelstack[level] = i
            if not obj.countries:
                if countrystack[level-1] == country:
                    countrystack[level] = country
            if country in obj.countries:
                selection |= set(levelstack[:level+1])
                countrystack[level] = country
            else:
                countrystack[level] = -1
        fid = open(os.path.join(OUTDIR, 'country_%i.txt' %country), 'wt')
        fid.write('\t'.join(['Level','wd_id','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
        for i, objl in enumerate(objlist):
            obj, level = objl
            if i in selection:
                fid.write(obj.write(level) + '\n')
        fid.close()
                
    

#################### MAIN
#retrieve_wikidata()
analyse_wikidata()

        
