#! /usr/bin/python
import os,sys
import urllib
import hashlib
import json
if sys.version_info < (3,0):
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer

import mwparserfromhell as mwp

sys.path.append('../python-osm/src/')
from osm import pyosm, osmdb
import countries

##################### CONSTANTS
VERSION = '0.0.1'

BASE_TMP = '/home/werner/osm/data/07.1_watershed_data'
OSM_TMP = os.path.join(BASE_TMP,'osm')
WIKIDATA_TMP = os.path.join(BASE_TMP,'wikidata')
WIKIPEDIA_TMP = os.path.join(BASE_TMP,'wikipedia')

OSM_LOCAL_SERVER='http://localhost:8888/'
WIKIDATA_SERVER='https://www.wikidata.org/w/api.php'
WIKIPEDIA_SERVER={'en':'http://en.wikipedia.org/w/api.php',
                  'de':'http://de.wikipedia.org/w/api.php',
                  'es':'http://es.wikipedia.org/w/api.php',
                  'fr':'http://fr.wikipedia.org/w/api.php'}

PLANET = '/store/osm/planet-latest.osm'
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
BASEDIR = os.path.join(SCRIPTDIR, '../')
COUNTRYFILE = os.path.join(BASEDIR, 'countries/TM_WORLD_BORDERS-0.3.shp')

##################### CLASSES

class OsmRiverDB(object):
    def __init__(self, filename='osmriverdb.txt'):
        self.filename = filename
        self.rivers = {}  ## dict of dictionaries (key is str(relid)
        
        if filename:
            self.read_file()
        
        self.odb = osmdb.OsmDb(PLANET)
        self.countrycheck = countries.CountryChecker(COUNTRYFILE)
        
    def read_file(self):
        if not os.path.exists(self.filename):
            return
        for line in open(self.filename).readlines()[1:]:
            toks = line.strip().split('\t')
            if len(toks) < 6:
                continue
            prop = {'rid': toks[0],
                    'version':toks[1],
                    'coords': (toks[2], toks[3]),  # lat, lon
                    'distance': float(toks[4]),
                    'country': toks[5]}
            self.rivers[toks[0]] = prop
    
    def write_file(self):
        fid = open(self.filename,'w')
        fid.write('HEADLINE\n')
        for rid, prop in self.rivers.iteritems():
            col = [prop['rid'],
                   prop['version'],
                   prop['coords'][0],
                   prop['coords'][1],
                   str(prop['distance']),
                   prop['country']]
            fid.write('\t'.join(col))
            fid.write('\n')
        fid.close()
    
    def get_riverprop(self,rid,version):
        rid = str(rid)
        rprop = self.rivers.get(rid,{})
        if rprop.get('version','') == str(version):
            return rprop
        else:
            print 'riverprop not found: ', rid, version, rprop
        
        data = self.odb.get_objects_recursive('relation', [int(rid)], recursive=True)
        osmfile = pyosm.OSMXMLFile(content = osmdb.OSMHEAD + data + osmdb.OSMTAIL)
        if int(rid) not in osmfile.relations:
            return {}
        
        rel = osmfile.relations[int(rid)]
        bb = rel.bbox(recursive=False)
        if not bb:
            return {}

        rprop = {}        
        rprop['coords'] = (str((bb[0] + bb[1]) / 2), str((bb[2] + bb[3]) / 2))
        rprop['distance'] = rel.distance(roles=['main_stream',''], recursive=False)
        rprop['version'] = str(rel.version)
        rprop['rid'] = rid
        
        lat, lon = rprop['coords']
        if lat and lon:
            p = countries.Point(float(lat),float(lon))
            c = self.countrycheck.getCountry(p)
            if c:
                rprop['country'] = c.iso
            else:
                rprop['country'] = ''
        self.rivers[rid] = rprop
        print '  new:', rid, self.rivers[rid]
        return rprop

class OsmRiver(object):
    def __init__(self, relid):
        self.relid = str(relid)
        self.data = ''
        self.wikipedia = ''
        self.wikidata = ''
        self.name = ''
        self.version = ''
        
        self.get_data()
        self.read_data()
        
    def get_data(self):
        tmppath = os.path.join(OSM_TMP, self.relid + '.xml')
        if os.path.exists(tmppath):
            self.data = open(tmppath).read()
        else:
            url=OSM_LOCAL_SERVER + 'relations?relations=%s&mode=full' %self.relid
            reldata = urllib.urlopen(url)
            self.data = reldata.read()
            open(tmppath, 'wt').write(self.data)
            
    def read_data(self):
        self.osm = pyosm.OSMXMLFile(content=self.data)
        rel = self.osm.relations[int(self.relid)]
        self.bbox = rel.bbox
        self.name = rel.tags.get('name','')
        self.wikidata = rel.tags.get('wikidata','')
        self.wikipedia = rel.tags.get('wikipedia','')

    def html(self):
        htmlstr = self.page
        return htmlstr
        
    def __str__(self):
        return  '%s\t%s\t%s\t%s\t%s' %(self.relid, self.bbox, self.name, self.wikipedia, self.wikidata)
            
            
class Wikidata(object):
    def __init__(self, wdid):
        self.wdid = str(wdid)
        self.wdid_link = '<a href="https://www.wikidata.org/wiki/Q%s">Q%s</a>' %(wdid,wdid)
        self.name = ''
        self.jsondata = ''
        self.data = {}
        
        self.get_data()
        self.read_data()
        
    def get_data(self):
        tmppath = os.path.join(WIKIDATA_TMP, self.wdid + '.json')
        if os.path.exists(tmppath):
            self.jsondata = open(tmppath).read()
        else:
            url=WIKIDATA_SERVER + '?action=wbgetentities&ids=Q%s&format=json' %self.wdid
            reldata = urllib.urlopen(url)
            self.jsondata = reldata.read()
            open(tmppath, 'wt').write(self.jsondata)
            
    def html(self):
        htmlstr = self.wdid
        return htmlstr
        
    def read_data(self):
        if not self.jsondata:
            return
        self.data = json.loads(self.jsondata)
        aliases = self.data.get('entities',{}).get('Q'+self.wdid,{}).get('labels',{})
        self.name = aliases.get('en',{}).get('value','')
                
    def __str__(self):
        return '%s' % self.wdid
            
class Wikipedia(object):
    def __init__(self, name, lang):
        self.page = name
        self.lang = lang
        self.hash = hashlib.sha1(self.page).hexdigest()
        
        self.jsondata = ''
        self.data = {}
        self.wikidata = ''
        self.title = ''
        self.content = ''
        self.coords = []    # list of (lat, lon, 'type_of_coord')
        self.wikilinks = []
        
        self.get_data()
        self.read_data()
        
    def get_data(self):
        tmppath = os.path.join(WIKIPEDIA_TMP, self.lang + '_' + self.hash + '.json')
        if os.path.exists(tmppath):
            self.jsondata = open(tmppath).read()
        else:
            server = WIKIPEDIA_SERVER.get(self.lang)
            pageenc = urllib.quote(self.page)
            if server:
                url=server + '?action=query&titles=%s&prop=revisions|pageprops&rvprop=content&format=json' %pageenc
                reldata = urllib.urlopen(url)
                self.jsondata = reldata.read()
                open(tmppath, 'wt').write(self.jsondata)
            else:
                print 'Error: server "%s" not found' %self.lang
                
    def read_data(self):
        if not self.jsondata:
            return
        self.data = json.loads(self.jsondata)
        pages = self.data.get('query',{}).get('pages',{})
        if not len(pages):
            return
        page = pages.items()[0][1]
        
        self.wikidata = page.get('pageprops',{}).get('wikibase_item','')
        self.title = page.get('title','')
        self.content = page.get('revisions',[{}])[0].get('*','')
        
        wikicode = mwp.parse(self.content)
        
        self.wikilinks = wikicode.filter_wikilinks()
        
        # Analyze Template {{Geobox|River}}
        for t in wikicode.filter_templates():
            if t.name == 'Coord':
                print 'Coord', t.params
            if t.name == 'Geobox': # from en wiki
                print 'Geobox', t.params
                
    def html(self):
        htmlstr = self.page
        return htmlstr

    def __str__(self):
        return '%s' % self.page
        

class RiverHttpHandler(BaseHTTPRequestHandler):
    """
    HTTP handler URL commands from the HTTP server.
    """
    def print_help(self):
        self.send_response(404)
        self.send_header('Content-type',	'text/html')
        self.end_headers()
        self.wfile.write("Riverdata interface<br>")
        self.wfile.write("=====================<br><br>")
        self.wfile.write("valid commands are:<br><br>")
        self.wfile.write("  osm?relid=[id1]<br>")
        self.wfile.write("  wikidata?qid=[id1]<br>")
        self.wfile.write("  wikipedia?page=[name][&lang=]<br>")
        return

    def do_GET(self):
        print (self.path)
        toks = self.path.split('?')
        if len(toks) != 2:
            self.print_help()
            return
        else:
            command = toks[0]
            kvs = toks[1].split('&')
            args = dict([kv.split('=',1) for kv in kvs])
        try:
            if command == '/osm':
                relid = args.get('relid')
                if not relid:
                    self.print_help()
                    return
                else:
                    river = OsmRiver(relid)
                    print(river)
            elif command == '/wikidata':
                qid = args.get('qid')
                if not qid:
                    self.print_help()
                    return
                else:
                    wd = Wikidata(qid)
                    print(wd)
            elif command == '/wikipedia':
                page = args.get('page')
                lang = args.get('lang','en')
                if not page:
                    self.print_help()
                    return
                else:
                    wp = Wikipedia(page, lang)
                    print(wp)

            data = '<h1>ok</h1>'
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write(data)
            return
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

##################### FUNCTIONS
def runserver(port):
    """
    Start the http-server with the given port and osmdb object.
    """
    try:
        server = HTTPServer(('', port), RiverHttpHandler)
        print ('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()

def usage():
    print (sys.argv[0] + " Version " + VERSION)
    print ("  -h, --help: print this help information")
    print ("  --relations=id1[,id2,id3,...]")
    print ("  --wikidata=id1[,id2,id3, ...]")
    print ("  --wikipedia=name1[,name2,name3, ...]")
    print ("  --server=port: start a http-Server on Port")
    print ("Examples:")
    print ("  river_data.py --relations=6188,6249")
    print ("  river_data.py --wikidata=Q584")
    print ("  river_data.py --wikipedia=Murray River&lang=en")
    print ("  river_data.py --server=8889")


###################### MAIN
if __name__ == '__main__':
    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h',
                                   ['relations=', 'wikidata=', 'wikipedia=', 'server=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit()


    for o, a in opts:
        if o in ['--relations']:
            relations = a.split(',')
            for r in relations:
                river = OsmRiver(r)
                print(river)
            sys.exit()
        elif o in ['--wikidata']:
            wikidata = a.split(',')
            for wd in wikidata:
                w = Wikidata(wd)
                print(w)
            sys.exit()
        elif o in ['--wikipedia']:
            wikipedia = a.split(',')
            for wp in wikipedia:
                w = Wikipedia(wp, 'en')
                print(w)
            sys.exit()
        elif o in ['--server']:
            port = int(a)
            runserver(port)
            sys.exit()
        elif o in ['--help']:
            usage()
            sys.exit()
        else:
            usage()
