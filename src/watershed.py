#!/usr/bin/python
# -*- coding:  utf-8 -*-

import sys, string, re, time, os
from xml.sax import handler, make_parser
import xml.sax.saxutils
import codecs
import numpy

import watershed_config

sys.path.append('../python-osm/src/')
from osm import pyosm
import wikidata_rivers

#################### CONSTANTS
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
TEMPLATEDIR = os.path.join(BASEDIR, 'templates')
PLANET_CONNECTIONS = os.path.join(BASEDIR,'../../data/07_watershed/planet/relations_up.txt')


#################### CLASSES

class WaterwayRelationScanner(object):
    def __init__(self,indir, outdir, osmfile):
        self.indir = indir
        self.outdir = outdir
        print 'loading osm file ...'
        self.osm = pyosm.OSMXMLFile(osmfile)
        self.osm.statistic()
        self.upstream_dict = {}

        print 'load connection table ...'
        self.conn = numpy.loadtxt(indir+'connections', dtype='int32')
        print 'create connection index ...'
        self.conn_dest_ind = numpy.argsort(self.conn[:,0]), 0
        self.conn_src_ind = numpy.argsort(self.conn[:,1]), 1

        print 'load planet upstream table'
        self.planet_destinations = self.load_planetconnections()

        print 'load way relation table ...'
        self.wayrel = numpy.loadtxt(indir+'relation_way', dtype='int32')
        print 'create way relation index ...'
        self.wayrel_relind = numpy.argsort(self.wayrel[:,0]), 0
        self.wayrel_wayind = numpy.argsort(self.wayrel[:,1]), 1
        print 'loading complete.'

    def load_planetconnections(self):
        upstream = {}
        visited = set()
        todo = set()

        for line in open(PLANET_CONNECTIONS).readlines():
            k,v = line.split('=',1)
            upstream[int(k)] = set([int(i) for i in v.split()])
        
        for k,v in watershed_config.dest.items():
            todo.update(v)

        while todo:
            x = todo.pop()
            if x in visited:
                continue
            todo.update(upstream.get(x,set()))
            visited.add(x)

        return visited

    def index_lookup(self, data, index, value):
        ind, col = index
        lower = -1
        upper = len(ind)
        result_ind = []
        found = True
        while upper - lower > 1:
            ind_current = (upper + lower)/2
            value_current = data[ind[ind_current],col]

            if value_current == value:
                found = True
                break
            if value_current > value:
                upper = ind_current
            else:
                lower = ind_current
        
        if not found:
            return []

        ## scan up and down all equal values
        lower = ind_current
        upper = ind_current
        while lower and (data[ind[lower-1],col] == value):
            lower -= 1
        while upper < len(ind) and data[ind[upper],col] == value:
            upper += 1

        return data[ind[lower:upper]]
            
    def scan(self):
        rows = []
        level = 5
        
        relations_up = open(os.path.join(self.outdir,'relations_up.txt'),'wt')

        rows = {}
        osmrivers = {}
        for relid, rel in sorted(self.osm.relations.items()):
            print 'scanning:', relid, rel.tags.get('name', '')

            stat, up, down= self.scan_single(relid)
            self.upstream_dict[relid] = up

            relations_up.write('%d=%s\n' %(relid, ' '.join([str(u) for u in up])))

            osmriver = wikidata_rivers.OsmRiver(relid)            
            osmriver.name = rel.tags.get('name', '')
            osmriver.wikipedia = self.wikipedia_links(rel.tags)
            osmriver.type_ = rel.tags.get('waterway','')
            osmriver.destination = rel.tags.get('destination', '')
            osmriver.sidestreams = list(up)
            osmriver.wd_id = rel.tags.get('wikidata', '')
            osmrivers[relid] = osmriver
            
            row = ['xx', # place holder for level column
                   '<a href="http://www.openstreetmap.org/browse/relation/%i">%i</a> <a href="%i.html">(d)</a>' % (relid,relid,relid),
                    rel.tags.get('name', '') + self.wikipedia_links(rel.tags),
                    ', '.join(['%s=%s' % (k,v) for k,v in rel.tags.items() if k.startswith('ref')]),
                    rel.tags.get('destination','') + ' ' +  rel.tags.get('tributary_of',''),
                    str(stat['way_members']),
                    str(len(down)),
                    str(len(up)),
                    str(stat['downstream_ways']),
                    str(stat['upstream_ways']),
                    ]
            rows[relid] = row
            

        tree = self.traverse_relations()
        colors = {'dest':' bgcolor="#7777FF"',
                  'planet':' bgcolor="#FFFF77"',
                  'missing':' bgcolor="#FF7777"',
                  'sub':''}
        htmlrows = []
        for relid, level, status in tree:
            row = rows[relid]
            row[0] = '<pre>'+'.'*(level-1) + str(level) + '</pre>'
            col = colors.get(status)
            htmlrows.append('<tr%s>\n' %col + '\n'.join(["  <td> %s </td>" %s for s in row]) + '</tr>\n')

        template = string.Template(open(os.path.join(TEMPLATEDIR,'watershed_hierarchical.html')).read())
        subst = {'ROWS': '\n'.join(htmlrows).encode('ascii','xmlcharrefreplace'),
                 'DATE': time.strftime("%Y-%m-%d"),
                 'CONNECTIONS':str(len(self.conn)),
                 'RELATION_COUNT': str(len(self.osm.relations)),
                 'WAY_RELATIONS': str(len(self.wayrel))}
        filename = os.path.join(self.outdir, 'hierarchical.html')
        open(filename,'wt').write(template.safe_substitute(subst))
        
        wikidata_rivers.analyse_wikidata(osmrivers)

        count = 1
        htmlrows = []
        for relid, row in sorted(rows.items()):
            row[0] = str(count)
            count += 1
            htmlrows.append('<tr>\n'  + '\n'.join(["  <td> %s </td>" %s for s in row]) + '</tr>\n')

        template = string.Template(open(os.path.join(TEMPLATEDIR,'watershed_flat.html')).read())
        subst = {'ROWS': '\n'.join(htmlrows).encode('ascii','xmlcharrefreplace'),
                 'DATE': time.strftime("%Y-%m-%d"),
                 'CONNECTIONS':str(len(self.conn)),
                 'RELATION_COUNT': str(len(self.osm.relations)),
                 'WAY_RELATIONS': str(len(self.wayrel))}
        filename = os.path.join(self.outdir, 'flat.html')
        open(filename,'wt').write(template.safe_substitute(subst))

    def scan_single(self,relid):
        upstream_relations = set([])
        downstream_relations = set([])
        upstream_ways = {}     ## relway --> upstream members
        downstream_ways = {}
        relation = self.osm.relations[relid]
        relways = [ m[1] for m in relation.member_data if m[0] == 'w' ]
                
        ## first level upstream
        for w in relways:
            for dest, src, n in self.index_lookup(self.conn, self.conn_dest_ind, w):
                relway = self.index_lookup(self.wayrel, self.wayrel_wayind, src)
                upstream_relations.update(set([rw[0] for rw in relway]))
        upstream_relations.discard(relid)

        visited_ways = set([])
        ## multilevel upstream
        for w in relways:
            upstream_ways[w] = set([])
            upstream_stack = [w]
            while upstream_stack:
                sw = upstream_stack.pop(0)
                if sw in visited_ways:
                    continue
                visited_ways.add(sw)
                for dest, src, n in self.index_lookup(self.conn, self.conn_dest_ind, sw):
                    relway = self.index_lookup(self.wayrel, self.wayrel_wayind, src)
                    if not len(relway):
                        upstream_ways[w].add(src)
                        if src not in visited_ways:
                            upstream_stack.append(src)
                    else:
                        pass

        ## first level downstream
        for w in relways:
            for dest, src, n in self.index_lookup(self.conn, self.conn_src_ind, w):
                relway = self.index_lookup(self.wayrel, self.wayrel_wayind, dest)
                downstream_relations.update(set([rw[0] for rw in relway]))
        downstream_relations.discard(relid)

        ## multilevel downstream
        visited_ways = set([])
        for w in relways:
            downstream_ways[w] = set([])
            downstream_stack = [w]
            while downstream_stack:
                sw = downstream_stack.pop(0)
                if sw in visited_ways:
                    continue
                visited_ways.add(sw)
                for dest, src, n in self.index_lookup(self.conn, self.conn_src_ind, sw):
                    relway = self.index_lookup(self.wayrel, self.wayrel_wayind, dest)
                    if not len(relway):
                        downstream_ways[w].add(dest)
                        if dest not in visited_ways:
                            downstream_stack.append(dest)
                    else:
                        pass
        
        upstream_items = []
        for r in upstream_relations:
            t = self.osm.relations[r].tags
            names = t.get('name','') + ' ' +  t.get('name:en','')
            upstream_items.append('<li> <a href="%d.html">%d</a>: %s </li>' %(r,r,names))

        downstream_items = []
        for r in downstream_relations:
            t = self.osm.relations[r].tags
            names = t.get('name','') + ' ' +  t.get('name:en','')
            downstream_items.append('<li> <a href="%d.html">%d</a>: %s </li>' %(r,r,names))

        upstream_way_count, downstream_way_count = 0, 0
        upstream_rows = []
        downstream_rows = []
        for k,v in sorted(upstream_ways.items()):
            if v:
                row =  '<tr><td>%d</td><td>%s</td></tr>' %(k,' '.join([str(m) for m in sorted(list(v))]))
                upstream_rows.append(row)
                upstream_way_count += len(v)
        for k,v in sorted(downstream_ways.items()):
            if v:
                row =  '<tr><td>%d</td><td>%s</td></tr>' %(k,' '.join([str(m) for m in sorted(list(v))]))
                downstream_rows.append(row)
                downstream_way_count += len(v)

        template = string.Template(open(os.path.join(TEMPLATEDIR, 'waterway.html')).read())

        subst = {'RELATION': str(relid),
                 'NAME': self.xmlenc(relation.tags.get('name', '')),
                 'NAMES': self.xmlenc(' '.join([k+'='+v for k,v in relation.tags.items() if k.startswith('name')])),
                 'DATE': time.strftime("%Y-%m-%d"),
                 'WAY_RELATIONS': str(len(relways)),
                 'OSM_RELATION': '<a href="http://www.openstreetmap.org/browse/relation/%i">%i</a>' %(relid,relid),
                 'REFERENCES': self.xmlenc(' '.join([k+'='+v for k,v in relation.tags.items() if k.startswith('ref')])),
                 'DESTINATION': self.xmlenc(relation.tags.get('destination','') + ' ' +  relation.tags.get('tributary_of','')),
                 'WIKIPEDIA': self.xmlenc(self.wikipedia_links(relation.tags)),
                 'DOWNSTREAM_RELATIONS': self.xmlenc('\n'.join(downstream_items)),
                 'UPSTREAM_RELATIONS': self.xmlenc('\n'.join(upstream_items)),
                 'DOWNSTREAM_WAYS': '\n'.join(downstream_rows),
                 'UPSTREAM_WAYS': '\n'.join(upstream_rows)}
        filename = os.path.join(self.outdir, '%d.html' % relid)
        open(filename,'wt').write(template.safe_substitute(subst))


        stat = {'way_members': len(relways),
                'upstream_relations': len(upstream_relations),
                'downstream_relations':len(downstream_relations),
                'upstream_ways':upstream_way_count,
                'downstream_ways': downstream_way_count}

        return stat, upstream_relations, downstream_relations

    def xmlenc(self, str_):
        return str_.encode('ascii','xmlcharrefreplace')

    def traverse_relations(self):
        rel_tree = []
        upstream_dict = {}
        upstream_dict.update(self.upstream_dict)  ##local copy
        visited = set([])

        dest = set(upstream_dict.keys())
        for k,v in upstream_dict.items():
            dest -= set(v)

        for country, rivers in sorted(watershed_config.dest.items()):
            for river in rivers:
                if river in upstream_dict:
                    rel_tree.append([river,1,'dest'])
                    visited.add(river)
                

        cursor = len(rel_tree)
        last_len = cursor
        while True:
            cursor -= 1
            if cursor == -1:
                if len(upstream_dict) == 0:
                    break
                if len(rel_tree) == last_len:
                    dest -= visited
                    if len(dest):
                        next_ = sorted(dest)[0]
                        dest.remove(next_)
                    else:
                        next_ = upstream_dict.keys()[0]
                    if next_ in self.planet_destinations:
                        rel_tree.append([next_,1,'planet'])
                    else:
                        rel_tree.append([next_,1,'missing'])
                    visited.add(next_)
                last_len = len(rel_tree)
                cursor = len(rel_tree) - 1

            rel, level, status = rel_tree[cursor]
            for sub in upstream_dict.get(rel,[]):
                if sub not in visited:
                    rel_tree.insert(cursor+1, [sub, level+1, 'sub'])
                    visited.add(sub)
            if rel in upstream_dict:
                upstream_dict.pop(rel)

        return rel_tree

    def wikipedia_links(self, tags):
        links = []
        for k,v in tags.items():
            if not re.match('wikipedia',k):
                continue
            toks = k.split(':')
            if len(toks) == 2:
                if re.match('http', v):
                    ref = v
                else:
                    ref = 'http://%s.wikipedia.org/wiki/%s' % (toks[1], v)
                linkname = ':' + toks[1]
            else:
                vtoks = v.split(':',1)
                if len(vtoks) == 2:
                    if vtoks[0] == 'http':
                        ref = v
                        linkname = 'wp'
                    else:
                        linkname = vtoks[0] + ':'
                        ref = 'http://%s.wikipedia.org/wiki/%s' % (vtoks[0], vtoks[1])
                else:
                    linkname = 'wp'
                    ref = 'http://en.wikipedia.org/wiki/%s' %  v
            links.append('<a href="%s"> (%s)</a>' % (ref, linkname))
        if 'wikidata' in tags:
            ref = 'https://www.wikidata.org/wiki/%s' % tags['wikidata']
            links.append('<a href="%s"> (%s)</a>' % (ref, 'wd'))
        return ' '.join(links)


class OsmWaterwayFilter(handler.ContentHandler):
    def __init__(self, write_handler):
        self.write_handler = write_handler
        self.current_object = None
        self.current_subobjects = []
        self.current_tags = {}
        self.types = set(['waterway'])
        self.waterways = set(['river','stream','canal','drain','ditch',
                              'wadi','lakeconnector','derelict_canal'])
        
    def startElement(self, obj, attrs):
        if obj == 'node':
            self.current_object = (obj, dict(attrs))
            self.current_subobjects = []
            self.current_tags = {}
        if obj == 'way':
            self.current_object = (obj, dict(attrs))
            self.current_subobjects = []
            self.current_tags = {}
        if obj == 'relation':
            self.current_object = (obj, dict(attrs))
            self.current_subobjects = []
            self.current_tags = {}
        if obj == 'nd':
            self.current_subobjects.append((obj,dict(attrs)))
        if obj == 'tag':
            self.current_subobjects.append((obj,dict(attrs)))
            self.current_tags[attrs['k']] = attrs['v']
        if obj == 'member':
            self.current_subobjects.append((obj,dict(attrs)))

    def endElement(self, obj):
        if obj == 'way':
            if self.current_tags.get('waterway','x') in self.waterways:
                self.write_object()
            
        elif obj == 'relation':
            if self.current_tags.get('type','x') == 'waterway':
                if self.current_tags.get('waterway','x') in self.waterways:
                    self.write_object()

    def write_object(self):
        tag, attrs = self.current_object
        self.write_handler.characters('  ')
        self.write_handler.startElement(tag, attrs)
        self.write_handler.characters('\n')

        for subtag, attrs in self.current_subobjects:
            self.write_handler.characters('  ')
            self.write_handler.startElement(subtag, attrs)
            self.write_handler.endElement(subtag)
            self.write_handler.characters('\n')

        self.write_handler.endElement(tag)
        self.write_handler.characters('\n')

class OsmWaterwayLister(handler.ContentHandler):
    def __init__(self,relwayfile):
        self.relways = numpy.loadtxt(relwayfile, dtype='int32')
        self.relways = set(self.relways[:,1])
        print len(self.relways)
        self.current_attrs = {}
        self.node_count = 0
        self.current_tags = {}
        self.waterway_dict = {}
        self.weighting = {}
        
        self.waterways = set(['river','stream','canal','drain','ditch',
                              'wadi','lakeconnector','derelict_canal'])
        
    def startElement(self, obj, attrs):
        if obj == 'way':
            self.current_attrs = dict(attrs)
            self.node_count = 0
            self.current_tags = {}
        if obj == 'nd':
            self.node_count += 1
        if obj == 'tag':
            self.current_tags[attrs['k']] = attrs['v']

    def endElement(self, obj):
        if obj == 'way':
            wwtype = self.current_tags.get('waterway','x')
            wwname = self.current_tags.get('name','')
            if wwname and wwtype in self.waterways:
                if int(self.current_attrs['id']) in self.relways:
                    return
                if wwtype == 'river':
                    w = 20
                else:
                    w = 1
                if wwname in self.waterway_dict:
                    self.waterway_dict[wwname].append(self.current_attrs['id'])
                    self.weighting[wwname] += w * self.node_count
                else:
                    self.waterway_dict[wwname] = [ self.current_attrs['id'] ]
                    self.weighting[wwname] = w* self.node_count


class OsmTableCreator(handler.ContentHandler):
    def __init__(self, outfiles, relfile):
        self.NFILES = len(outfiles)
        self.files = outfiles
        self.relfile = relfile
        self.current_wayid = 0
        self.current_relid = 0
        self.current_nodes = []
        self.current_ways = []
                      
    def startElement(self, obj, attrs):
        if obj == 'way':
            self.current_wayid = int(attrs['id'])
            self.current_nodes = []
        if obj == 'relation':
            self.current_relid = int(attrs['id'])
            self.current_ways = []
        if obj == 'nd':
            self.current_nodes.append(int(attrs['ref']))
        if obj == 'member':
            if attrs['type'] == 'way':
                self.current_ways.append(int(attrs['ref']))

    def endElement(self, obj):
        if obj == 'way':
            poslist = numpy.arange(len(self.current_nodes))+1
            poslist[-1] = -1  #mark the last node
            for nodeid, pos in zip(self.current_nodes, poslist):
                # hashsorting: key is the remainder of the modulo operator
                currentfile = self.files[nodeid % self.NFILES]
                currentfile.write('%i\t%i\t%i\n' %(nodeid, self.current_wayid, pos))
        if obj == 'relation':
            for member in self.current_ways:
                self.relfile.write('%i\t%i\n' %(self.current_relid, member))

#################### FUNCTIONS
def waterwayfilter(outfile):
    outfile = open(outfile, 'wt')
    write_handler = xml.sax.saxutils.XMLGenerator(outfile, 'UTF-8')

    osm_handler = OsmWaterwayFilter(write_handler)
    parser = make_parser()
    parser.setContentHandler(osm_handler)

    write_handler.startDocument()
    write_handler.startElement('osm', {'version':'0.6', 'generator': 'waterway_filter.py'})
    write_handler.characters('\n')

    parser.parse(sys.stdin)

    write_handler.endElement('osm')
    write_handler.endDocument()


def waterwaylist(relwayfile, outfile):
    osm_handler = OsmWaterwayLister(relwayfile)
    parser = make_parser()
    parser.setContentHandler(osm_handler)

    parser.parse(sys.stdin)

    outfile = open(outfile, 'wt')

    vk = []
    for k,v in osm_handler.weighting.items():
        vk.append((v,k))

    for weight, name in sorted(vk, reverse=True):
        outfile.write(name.encode('ascii','xmlcharrefreplace') + '\t')
        outfile.write(' '.join(osm_handler.waterway_dict[name]))
        outfile.write('\n\n')

def createtables(outdir):
    ## 1st level hashsorting the output
    ## number of files use to split the output 
    NFILES = 100
    waynode_filenames =  [os.path.join(outdir,'waynode_' + str(n))  for n in range(NFILES)]

    outfiles = [open(f,'wt') for f in waynode_filenames]
    relfile = open(os.path.join(outdir,'relation_way'), 'wt')
    osm_handler = OsmTableCreator(outfiles, relfile)
    parser = make_parser()
    parser.setContentHandler(osm_handler)
    parser.parse(sys.stdin)

    for f in outfiles:
        f.close()

    ## find all connections of waterways and create tables
    # different output tables, currently only the connection file is used for analyses
    # FIXME: maybe use only one table (nodeid, wayid, index of node in way) like the raw tables
    #        current format is (destway, srcway, nodeid)
    dest_file = open(outdir+'destinations','wt')
    con_file =  open(outdir+'connections', 'wt')
    source_file = open(outdir+'sources','wt')
    ee_file = open(outdir+'endpoint_endpoint','wt')
    ss_file = open(outdir+'sourcepoint_sourcepoint','wt')

    for f in waynode_filenames:
        m = numpy.loadtxt(f, dtype='int32')
        ind = numpy.argsort(m[:,0])

        print f, m.shape

        lastnodeid = -1
        nodeid = -1
        srcind = []
        midind = []
        destind = []
        for i in list(ind) + [0]:
            nodeid, wayid, conn = m[i]
            if nodeid != lastnodeid:
                if destind and (srcind or midind):
                    for srcnode, srcway, conn in m[destind]:
                        for destnode, destway, conn in m[srcind + midind]:
                            con_file.write('%i\t%i\t%i\n' %(destway, srcway, srcnode))
                if srcind and midind and not destind:
                    for srcnode, srcway, conn in m[midind]:
                        for destnode, destway, conn in m[srcind]:
                            con_file.write('%i\t%i\t%i\n' %(destway, srcway, srcnode))
                if destind and not (midind or srcind):
                    for destnode, destway, conn in m[destind]:
                        dest_file.write('%i\t%i\n' %(destway, destnode))
                        if len(destind) > 1:
                            ee_file.write('%i\t%i\n' %(destway, destnode))
                if srcind and not (destind or midind):
                    for srcnode, srcway, conn in m[srcind]:
                        source_file.write('%i\t%i\n' %(srcway, srcnode))
                        if len(srcind) > 1:
                            ss_file.write('%i\t%i\n' %(srcway, srcnode))
                srcind = []
                midind = []
                destind = []

            lastnodeid = nodeid
            nodeid, wayid, conn = m[i]
            if conn == 1:
                srcind.append(i)
            elif conn == -1:
                destind.append(i)
            else:
                midind.append(i)

    dest_file.close()
    con_file.close()
    source_file.close()
    ee_file.close()
    ss_file.close()


#################### MAIN
## split up the analyses in different tasks
# usage: program command [args]

if sys.argv[1] == 'filter':
    # input is stdin
    outfile = sys.argv[2]
    waterwayfilter(outfile)

if sys.argv[1] == 'waterwaylist':
    # input is stdin
    relwayfile = sys.argv[2]
    outfile = sys.argv[3]
    waterwaylist(relwayfile, outfile)

if sys.argv[1] == 'createtables':
    # input is sys.stdin
    tabledir = sys.argv[2]
    createtables(tabledir)

if sys.argv[1] == 'analyse':
    tabledir = sys.argv[2]
    outdir = sys.argv[3]
    infile = sys.argv[4]  ## waterway relations
    scanner = WaterwayRelationScanner(tabledir, outdir, infile)
    scanner.scan()
