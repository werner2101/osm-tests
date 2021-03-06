#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import io
import os, time
import string
import json
import urllib
if sys.version_info < (3,0):
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer

import river_data
import countries
    
#################### CONST
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
BASEDIR = os.path.join(SCRIPTDIR, '../')
TEMPLATEDIR = os.path.join(BASEDIR, 'templates')
OUTDIR = os.path.join(SCRIPTDIR, '../../../data/07.1_watershed_data/')
COUNTRYFILE = os.path.join(BASEDIR, 'countries/TM_WORLD_BORDERS-0.3.shp')

TOOLSERVER='https://wdq.wmflabs.org/api'

WATERWAYS = [('573344', 'mainstem'),
             ('4022', 'river'),
             ('1140845','subterranean river'),
             ('3529419','small river'),
             ('47521', 'stream'),
             ('1437299', 'torrent'),
             ('2048319','ditch'),
             ('27250','tidal creek'),
             ('187971','wadi'),
             ('12284', 'canal'),
             ('8261440','canal for transporting water'),
             ('5031071','canal tunnel'),
             ('1009249', 'bundeswasserstrasse'),
             ('523166','gracht'),
             ('708457','wetering'),
#             ('34038','waterfall'),
             ('355304','watercourse'),
             ('166620','drainage basin'),
             ('285451','drainage system'),
             ('43197','river delta'),
             ('591942','distributary')]
             
WATERAREAS = [('9430','ocean'),
              ('165','sea'),
              ('986177','mediteranean sea'),
              ('1973404','inland sea'),
              ('204894','marginal sea'),
              ('37901','strait'),
              ('1322134','gulf'),
              ('39594','bay'),
              ('812585','bayou'),
              ('283202','harbor'),
              ('1172599','inlet'),
              ('2923911',' empoldered inlet'),
              ('554394','ria'),
              ('491713','sound'),
              ('31615','cove'),
              ('558116','firth'),
              ('45776','fjord'),
              ('319714','fjard'),
              ('47053','estuary'),
              ('170321','wetland'),
              ('5926864','group of lakes'),
              ('23397','lake'),
              ('3215290','artificial lake'),
              ('211302','glacial lake'),
              ('188025','salt lake'),
              ('11349558','soda lake'),
              ('935277','salt pan'),
              ('14253637','dry lake'),
              ('6341928','rift lake'),
              ('204324','crater lake'),
              ('9019918','endoheic lake'),
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
        self.name = ''
        self.mouth_waterway = -1
        self.mouth_area = -1
        self.sidestreams = []
        self.lakes_onriver = []
        self.part_of = []
        self.has_part = []
        self._type = _type
        self.osm_relid = ''
        self.coords = ('','')
        self.adminarea = []
        self.countries = []
        self.country2 = ''    # ISO code from geo coder
        self.continents = []
        self.osmriver =  None
        
    def traverse(self, level, visited, objlist):
        if self in visited:
            visited.discard(self)
            objlist.append((self,level))
        else:
            return

        if self.osmriver:
            self.osmriver.traverse(level, visited, objlist)
        for ss in self.sidestreams:
            if level < 20:
                ss.traverse(level+1, visited, objlist)
        for hp in self.has_part:
            if level < 20:
                hp.traverse(level+1, visited, objlist)
        for lor in self.lakes_onriver:
            if level < 20 and lor:
                lor.traverse(level+1, visited, objlist)

    def write(self, level):
        if self.mouth_waterway > 0:
            mouth = self.mouth_waterway
        else:
            mouth = self.mouth_area
        return u'\t'.join(['.'*(level-1)+str(level), str(self.wd_id), self.name, self.osm_relid,
                         str(self._type), str(mouth),
                         self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                         ' '.join([str(i) for i in self.continents]),
                         ' '.join([str(i) for i in self.countries]) + ' ' + self.country2,
                         ' '.join([str(i) for i in self.adminarea])
                         ])

    def write_html(self,level,parent_rivers=[]):
        if self.mouth_waterway > 0:
            mouth = self.mouth_waterway
        else:
            mouth = self.mouth_area
        if level == 1:
            color = ' bgcolor="#FF8888"'
        elif len(parent_rivers) == 0:
            color = ' bgcolor="#77FF77"'
        else:
            color = ''

        cells = ['.'*(level-1)+str(level), str(self.osm_relid),
                 str(self.wd_id), self.name, 
                 str(self._type), str(mouth),
                 self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                 '', 
                 '', # misc
                 self.country2,
                 ]
        return '<tr' + color + '><td>' + '</td><td>'.join(cells) + '</td></tr>'
            
    def __cmp__(self, other):
        assert isinstance(other, River)
        return cmp((self.mouth_waterway, self.wd_id), (other.mouth_waterway, other.wd_id))

class OsmRiver(object):
    def __init__(self, osmid):
        self.osm_relid = osmid
        self.version = ''
        self.type_ = ''
        self.name = ''
        self.wd_id = ''
        self.wikipedia = []
        self.destination = ''
        self.sidestreams = set([])
        self.coords = ('','')
        self.distance = 0
        self.countries = []
        self.country2 = ''    # ISO code from geo coder
        self.ref = ''

    def traverse(self, level, visited, objlist):
        if self in visited:
            visited.discard(self)
            objlist.append((self,level))
        else:
            return
            
        for ss in self.sidestreams:
            if not ss.wd_id:
                ss.traverse(level+1, visited, objlist)

    def write(self, level):
        if self.wd_id:
            wd_id = self.wd_id[1:]
        else:
            wd_id = ''
        return u'\t'.join(['.'*(level-1)+str(level), wd_id, self.name, str(self.osm_relid),
                           str(self.type_), self.destination,
                           self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                           '',
                           ' '.join([str(i) for i in self.countries]) + ' ' + self.country2,
                           '', # adminarea
                         ])

    def write_html(self,level,parent_rivers=[]):
        if self.wd_id:
            wd_id = self.wd_id[1:]
        else:
            wd_id = ''

        if level == 1:
            color = ' bgcolor="#FF7777"'
        elif len(parent_rivers) == 0:
            color = ' bgcolor="#77FF77"'
        else:
            color = ''
        
        cells = ['.'*(level-1)+str(level), str(self.osm_relid),
                 wd_id, self.name, 
                 str(self.type_), self.destination,
                 self.coords[0], # lat
                 self.coords[1], # lon
                 self.wikipedia, 
                 '%.2f' % (self.distance/1000), # river distance
                 self.country2,
                 ]
        return '<tr'+color+'><td>' + '</td><td>'.join(cells) + '</td></tr>'
        
    def __cmp__(self, other):
        assert isinstance(other, OsmRiver)
        return cmp((self.osm_relid, self.wd_id), (other.osm_relid, other.wd_id))
        

class Waterarea(object):
    def __init__(self, wikidata_id, _type):
        self.wd_id = wikidata_id
        self.osm_relid = ''   # not used
        self._type = _type
        self.name = ''
        self.part_of = -1
        self.inflows = []
        self.outflow = -1
        self.subparts = []
        self.osm_relid = ''
        self.coords = ('','')
        self.adminarea = []
        self.countries = []
        self.country2 = ''    # ISO code from geo coder
        self.continents = []

    def traverse(self, level, visited, objlist):
        if self in visited:
            visited.discard(self)
            objlist.append((self, level))
        else:
            return

        for sp in self.subparts:
            if level < 20:
                sp.traverse(level+1, visited, objlist)
        for river in self.inflows:
            if level < 20:
                river.traverse(level+1, visited, objlist)

    def write(self, level):
        return u'\t'.join(['.'*(level-1)+str(level), str(self.wd_id), self.name, self.osm_relid,
                         str(self._type), str(self.part_of),
                         self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                         ' '.join([str(i) for i in self.continents]),
                         ' '.join([str(i) for i in self.countries]),
                         ' '.join([str(i) for i in self.adminarea])
                         ])

    def write_html(self,level,**kwargs):
        cells = ['.'*(level-1)+str(level), str(self.osm_relid),
                 str(self.wd_id), self.name, 
                 str(self._type), str(self.part_of),
                 self.coords[0].replace('.',','), self.coords[1].replace('.',','),
                 '', 
                 '', # misc
                 self.country2,
                 ]
        if self._type in ['ocean', 'sea']:
            color = ' bgcolor="#3333FF"'
        else:
            color = ' bgcolor="#7777FF"'
            
        return '<tr' + color + '><td>' + '</td><td>'.join(cells) + '</td></tr>'
            
    def __cmp__(self, other):
        assert isinstance(other, Waterarea)
        return cmp((self.wd_id), (other.wd_id))


class WD_Analyser(object):
    def __init__(self, osmrivers={}):
        self.osmrivers = osmrivers
        self.objlist = []
        
        self.river_geometry()
        self.read()
        self.analyse()
    
    def read(self):
        """
        read river and waterarea data and analyse it
        """
        self.waterareas = readjson_waterareas()
        self.rivers = readjson_waterways()
    
    def river_geometry(self):
        if not self.osmrivers:
            return
        rdb = river_data.OsmRiverDB()
        counter = 0
        for rid, river in self.osmrivers.iteritems():
            geoprop = rdb.get_riverprop(rid,river.version)
            river.coords = geoprop.get('coords',('',''))
            river.distance = geoprop.get('distance', 0)
            river.country2 = geoprop.get('country','')
            counter += 1
            if counter % 100 == 0:
                rdb.write_file()
            
        rdb.write_file()
        
    def analyse(self):
        ## preprocessing of river items
        no_mouth = []
        unknown_mouth = []    
        for w_id, ww in self.rivers.items():
            if ww.mouth_waterway in self.rivers:
                self.rivers[ww.mouth_waterway].sidestreams.append(ww)
            elif ww.mouth_waterway in self.waterareas:
                self.waterareas[ww.mouth_waterway].inflows.append(ww)          
            elif ww.mouth_waterway > 0:
                unknown_mouth.append(ww)
            else:
                no_mouth.append(ww)
            for n, po in enumerate(ww.part_of):
                if po in self.rivers:
                    self.rivers[po].has_part.append(ww)
                else:
                    print "river part_of not found", ww.wd_id, po
            for n, lor in enumerate(ww.lakes_onriver):
                if lor in self.waterareas:
                    ww.lakes_onriver[n] = self.waterareas[lor]
                else:
                    ww.lakes_onriver[n] = None
    
        ## preprocessing of waterarea items    
        no_part = []
        for w_id, wa, in self.waterareas.items():
            if wa.part_of in self.waterareas:
                self.waterareas[wa.part_of].subparts.append(wa)
            elif wa.part_of in self.rivers:
                self.rivers[wa.part_of].has_part.append(wa)
            elif wa.outflow in self.rivers:
                self.rivers[wa.outflow].lakes_onriver.append(wa)
            else:
                no_part.append(wa)
    
        ## preporcessing of osmriver items
        for osmid, osmriver in self.osmrivers.iteritems():
            for i, sidestream in enumerate(osmriver.sidestreams):
                osmriver.sidestreams[i] = self.osmrivers[sidestream]
            if osmriver.wd_id:
                wdid = int(osmriver.wd_id[1:])
                if wdid in self.rivers:
                    self.rivers[wdid].osmriver = osmriver
                    osmriver.countries = self.rivers[wdid].countries
                    osmriver.country2 = self.rivers[wdid].country2
                    #osmriver.coords = self.rivers[wdid].coords
        
        ## need a list for the result and a set of all wikidata objects that will be visited
        visited = set(self.rivers.values()) | set(self.waterareas.values()) | set(self.osmrivers.values())
    
        ## start traversing with waterareas that are not part of other areas    
        for wa in sorted(no_part):
            if not (len(wa.subparts) + len(wa.inflows)):
                continue
            if wa in visited:
                wa.traverse(1,visited,self.objlist)
            
        ## collect all rivers with present, but unknown destination
        for river in sorted(unknown_mouth):
            if river in visited:
                river.traverse(1, visited, self.objlist)
        
        ## collect all the rest of the watercourses    
        for river in sorted(no_mouth):
            if river.mouth_waterway == -1:
                river.traverse(1,visited, self.objlist)
    
        ## collect all rivers only present in osm
        osmrivers_unvisited = set(self.osmrivers.values()) & visited
        print 'unvisited osmrivers:', len(osmrivers_unvisited)
        for osmriver in list(osmrivers_unvisited):
            osmrivers_unvisited -= set(osmriver.sidestreams)
        print 'unvisited osmrivers without sidestreams:', len(osmrivers_unvisited)
        for osmriver in osmrivers_unvisited:
            osmriver.traverse(1,visited, self.objlist)
        osmrivers_unvisited = set(self.osmrivers.values()) & visited
        print 'unvisited osmrivers with recursion:', len(osmrivers_unvisited)
        for osmriver in osmrivers_unvisited:
            osmriver.traverse(1,visited, self.objlist)

    def write(self):
        ## write the whole object list into a text file
        fid = io.open(os.path.join(OUTDIR, 'wikidata_tree.txt'), 'wt', encoding='utf-8')
        fid.write(u'\t'.join(['Level','wd_id','name','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
        for obj, level in self.objlist:
            fid.write(obj.write(level) + '\n')
   
    def write_countries(self, prefix=''):
        ## create lists for eatch country
        # collect all countries in a set first    
        countries = set()  # of wikidata ids
        for i, r in self.rivers.iteritems():
            countries |= set(r.countries)
        country_rows = []    
        known_country = set()
        for country in sorted(countries):
            levelstack = [-1]*100
            countrystack = [-1]*100
            selection = set()
            for i, objl in enumerate(self.objlist):
                obj, level = objl
                levelstack[level] = i
                countrystack[level] = -1
                if obj.countries:
                    if country in obj.countries:
                        countrystack[level] = country
                else:
                    if countrystack[level-1] == country:
                        countrystack[level] = country
                        
                if country == countrystack[level]:
                    selection |= set(levelstack[:level+1])
                
            known_country |= selection
    
            ## write a txt file for each country
            fid = io.open(os.path.join(OUTDIR, 'countries', '%s%i.txt' %(prefix,country)), 'wt', encoding='utf-8')
            fid.write(u'\t'.join(['Level','wd_id','name','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
            destlevel = 0
            for i, objl in enumerate(self.objlist):
                obj, level = objl
                if i in selection:
                    fid.write(obj.write(level) + '\n')
                    if level == 1 and type(obj) == River:
                        destlevel += 1
            fid.close()
            
            ## write a html file for each country
            wd_country = river_data.Wikidata(country)
            osm_link = ''
            if wd_country.iso:
                osm_link = '<a href="../07_watershed/planet/wikidata_osm_%s.html">html</a>' %(wd_country.iso)
            country_row = [wd_country.wdid_link,
                           wd_country.name,
                           '<a href="countries/%i.txt">txt</a>' %(country),
                           '%i/%i, %.1f%%' %(len(selection)-1, destlevel, 100-100*(float(destlevel)/(len(selection)-1))),
                           '<a href="countries/%s%i.txt">txt</a>' %(prefix,country),
                           osm_link
                           ]
            country_rows.append('<tr><td>' + '</td><td>'.join(country_row) + '</td></tr>')

        ## no country found
        fid = io.open(os.path.join(OUTDIR, 'countries', '%sunknown.txt' % prefix), 'wt', encoding='utf-8')
        fid.write(u'\t'.join(['Level','wd_id','name','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
        for i, objl in enumerate(self.objlist):
            obj, level = objl
            if i not in known_country:
                fid.write(obj.write(level) + '\n')
        fid.close()
        unknown_row = ['--',
                       'unknown',
                       '<a href="countries/unknown.txt">txt</a>',
                       '%i' % (len(self.objlist) - len(known_country)),
                       '<a href="countries/wikidata_osm_unknown.txt">txt</a>',
                       '']

        country_rows.append('<tr><td>' + '</td><td>'.join(unknown_row) + '</td></tr>')
    
        ## index for all countries
        template = string.Template(open(os.path.join(TEMPLATEDIR,'wikidata_countries.html')).read())
        subst = {'ROWS': '\n'.join(country_rows).encode('ascii','xmlcharrefreplace'),
                 'DATE': time.strftime("%Y-%m-%d")}
        filename = os.path.join(OUTDIR, 'index.html')
        open(filename,'wt').write(template.safe_substitute(subst))
        
    def write_osm(self, outfile, outdir=None):
        """
        write all elementes to a file, which have a osm_id
        """
        levelstack = [-1]*100
        selection = set()
        for i, objl in enumerate(self.objlist):
            obj, level = objl
            levelstack[level] = i
            if obj.osm_relid and type(obj) == OsmRiver:
                selection |= set(levelstack[:level+1])
                
        ## write selection to a txt file
        fid = io.open(outfile, 'wt', encoding='utf-8')
        fid.write(u'\t'.join(['Level','wd_id','name','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
        for i, objl in enumerate(self.objlist):
            obj, level = objl
            if i in selection:
                if type(obj) == Waterarea:
                    wd_area = river_data.Wikidata(obj.wd_id)
                    obj.name = wd_area.name
                fid.write(obj.write(level) + '\n')
        fid.close()
        
        ## create html output file
        if not outdir:
            return

        river_rows = []
        obj_stack = [None]*100
        for i, obj in enumerate(self.objlist):
            obj, level = obj
            obj_stack[level-1] = obj
            if i in selection:
                if type(obj) == Waterarea:
                    wd_area = river_data.Wikidata(obj.wd_id)
                    obj.name = wd_area.name
                parent_rivers = [ r for r in obj_stack[:level-1] if type(r) in (OsmRiver,River)]
                river_rows.append(obj.write_html(level,parent_rivers=parent_rivers))
            
        template = string.Template(open(os.path.join(TEMPLATEDIR,'watershed_wikidata.html')).read())
        subst = {'ROWS': '\n'.join(river_rows).encode('ascii','xmlcharrefreplace'),
                 'DATE': time.strftime("%Y-%m-%d")}
        filename = os.path.join(outdir + 'wikidata_osm.html')
        open(filename,'wt').write(template.safe_substitute(subst))
        
        osm_sel = selection
        
        ## create html output file for each country
        # collect all countries in a set first    
        countries = set()  # of wikidata ids
        for obj, level in self.objlist:
            if type(obj) == OsmRiver:
                countries.add(obj.country2)
        countries.remove('')  # empty countries are unknown
        known_country = set()
        for country in sorted(countries):
            levelstack = [-1]*100
            countrystack = [-1]*100
            selection = set()
            for i, objl in enumerate(self.objlist):
                obj, level = objl
                levelstack[level] = i
                countrystack[level] = -1
                if type(obj) == OsmRiver:
                    if country == obj.country2:
                        countrystack[level] = country
                else:
                    if countrystack[level-1] == country:
                        countrystack[level] = country
                        
                if country == countrystack[level]:
                    selection |= set(levelstack[:level+1])
                
            known_country |= selection
            
            # write into text file
            fid = io.open(os.path.join(outdir, 'wikidata_osm_'+country+'.txt'), 'wt', encoding='utf-8')
            fid.write(u'\t'.join(['Level','wd_id','name','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
            for i, objl in enumerate(self.objlist):
                obj, level = objl
                if i in selection and i in osm_sel:
                    if type(obj) == Waterarea:
                        wd_area = river_data.Wikidata(obj.wd_id)
                        obj.name = wd_area.name
                    fid.write(obj.write(level) + '\n')
            fid.close()
            # write into html file
            river_rows = []
            for i, objl in enumerate(self.objlist):
                obj, level = objl
                obj_stack[level-1] = obj
                if i in selection and i in osm_sel:
                    if type(obj) == Waterarea:
                        wd_area = river_data.Wikidata(obj.wd_id)
                        obj.name = wd_area.name
                    parent_rivers = [ r for r in obj_stack[:level-1] if type(r) in (OsmRiver,River)]
                    river_rows.append(obj.write_html(level,parent_rivers=parent_rivers))
            template = string.Template(open(os.path.join(TEMPLATEDIR,'watershed_wikidata_country.html')).read())
            subst = {'ROWS': '\n'.join(river_rows).encode('ascii','xmlcharrefreplace'),
                     'DATE': time.strftime("%Y-%m-%d"), 'COUNTRY': country.upper()}
            filename = os.path.join(outdir + 'wikidata_osm_'+country+'.html')
            open(filename,'wt').write(template.safe_substitute(subst))

        ## no country found
        fid = io.open(os.path.join(outdir, 'wikidata_osm_unknown.txt'), 'wt', encoding='utf-8')
        fid.write(u'\t'.join(['Level','wd_id','name','osm_id','type','mouth','lat','lon','continent','country','admin'])+'\n')
        for i, objl in enumerate(self.objlist):
            obj, level = objl
            if i not in known_country and i in osm_sel:
                fid.write(obj.write(level) + '\n')
        fid.close()

        
#################### FUNCTIONS
def readjson_waterways():
    """
    reads watercource json data retrieved from wikidata.
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
        for wd_id, type_, country in jdata['props'].get('205',[]):
            rivers[wd_id].countries.append(country)
        for wd_id, type_, continent in jdata['props'].get('30',[]):
            rivers[wd_id].continents.append(continent)
        for wd_id, type_, part_of in jdata['props'].get('361',[]):
            rivers[wd_id].part_of.append(part_of)
        for wd_id, type_, adminarea in jdata['props'].get('131',[]):
            rivers[wd_id].adminarea.append(adminarea)
        for wd_id, type_, lakes_river in jdata['props'].get('469',[]):
             rivers[wd_id].lakes_onriver.append(lakes_river)
        for wd_id, type_, wref in jdata['props'].get('1183',[]):
             rivers[wd_id].ref = wref
    
    countrycheck = countries.CountryChecker(COUNTRYFILE)
    for wd_id, r in rivers.iteritems():
        lat, lon = r.coords
        if lat and lon:
            p = countries.Point(float(lat),float(lon))
            c = countrycheck.getCountry(p)
            if c:
                r.country2 = c.iso

    return rivers

def readjson_waterareas():
    """
    reads waterarea json data retrieved from wikidata.
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
        for wd_id, type_, country in jdata['props'].get('205',[]):
            waterareas[wd_id].countries.append(country)
        for wd_id, type_, continent in jdata['props'].get('30',[]):
            waterareas[wd_id].continents.append(continent)
        for wd_id, type_, adminarea in jdata['props'].get('131',[]):
            waterareas[wd_id].adminarea.append(adminarea)
        for wd_id, type_, outflow in jdata['props'].get('201',[]):
            waterareas[wd_id].outflow = outflow

    return waterareas

def retrieve_wikidata():
    """
    get wikidata watercourse and waterarea data and store the result in json 
    data files
    """
    for i_id, r_type in WATERWAYS:
        print i_id, r_type
        url = TOOLSERVER + '?q=claim[31:%s]&props=402,403,31,625,17,30,131,469,361,205,1183' %i_id
        answ = urllib.urlopen(url)
        data = answ.read()
        open(os.path.join(OUTDIR, r_type + '.json'), 'wt').write(data)
    
    for i_id, r_type in WATERAREAS:
        print i_id, r_type
        url = TOOLSERVER + '?q=claim[31:%s]&props=402,31,625,17,30,131,361,201,205' %i_id
        answ = urllib.urlopen(url)
        data = answ.read()
        open(os.path.join(OUTDIR, r_type + '.json'), 'wt').write(data)


#################### MAIN
if __name__ == '__main__':
    retrieve_wikidata()
    analyser = WD_Analyser({})
    analyser.write()
    analyser.write_countries()
