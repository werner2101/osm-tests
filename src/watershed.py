#!/usr/bin/python
# -*- coding:  utf-8 -*-

import sys, string, re, time, os
from xml.sax import handler, make_parser
import xml.sax.saxutils
import numpy

sys.path.append('../python-osm/src/')
from osm import pyosm
#################### CLASSES

class WaterwayRelationScanner(object):
    def __init__(self,indir, outdir, osmfile):
        self.indir = indir
        self.outdir = outdir
        print 'loading osm file ...'
        self.osm = pyosm.OSMXMLFile(osmfile)
        self.osm.statistic()

        print 'load connection table ...'
        self.conn = numpy.loadtxt(indir+'connections', dtype='int32')
        print 'create connection index ...'
        self.conn_dest_ind = numpy.argsort(self.conn[:,0]), 0
        self.conn_src_ind = numpy.argsort(self.conn[:,1]), 1

        print 'load way relation table ...'
        self.wayrel = numpy.loadtxt(indir+'relation_way', dtype='int32')
        print 'create way relation index ...'
        self.wayrel_relind = numpy.argsort(self.wayrel[:,0]), 0
        self.wayrel_wayind = numpy.argsort(self.wayrel[:,1]), 1
        print 'loading complete.'

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
        
        relations_up = open(os.path.join(os.path.dirname(__file__),'relations_up.txt'),'wt')
        
        for relid, rel in sorted(self.osm.relations.items()):
#            if relid != 1162834:
#                continue
            print 'scanning:', relid, rel.tags.get('name', '')

            stat, up, down= self.scan_single(relid)

            relations_up.write('%d=%s\n' %(relid, ' '.join([str(u) for u in up])))

            row = []
#            row.append('<pre>'+'.'*(level-1) + str(level) + '</pre>')
            row.append('xx')
            row.append('<a href="http://www.openstreetmap.org/browse/relation/%i">%i</a> <a href="%i.html">(d)</a>' % (relid,relid,relid))
            row.append(rel.tags.get('name', '') + self.wikipedia_links(rel.tags))
            row.append(', '.join(['%s=%s' % (k,v) for k,v in rel.tags.items() if k.startswith('ref')]))
            row.append(rel.tags.get('destination','') + ' ' +  rel.tags.get('tributary_of',''))
            row.append(str(stat['way_members']))
            row.append(str(len(down)))
            row.append(str(len(up)))
            row.append(str(stat['downstream_ways']))
            row.append(str(stat['upstream_ways']))
                       
            if level == 1:
                col = ' bgcolor="#7777FF"' if status else ' bgcolor="#FF7777"'
            else:
                col = ''
            rows.append('<tr%s>\n' %col + '\n'.join(["  <td> %s </td>" %s for s in row]) + '</tr>\n')

        template = string.Template(open(os.path.join(os.path.dirname(__file__),
                                                     'templates','watershed.html')).read())
        subst = {'ROWS': '\n'.join(rows).encode('ascii','xmlcharrefreplace'),
                 'DATE': time.strftime("%Y-%m-%d"),
                 'CONNECTIONS':str(len(self.conn)),
                 'RELATION_COUNT': str(len(self.osm.relations)),
                 'WAY_RELATIONS': str(len(self.wayrel))}
        filename = os.path.join(self.outdir, 'index.html')
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

#        visited_ways.update(set(relways))
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
#                print 'upstream', sw, len(visited_ways), len(upstream_stack)
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
#                print 'downstream', sw, len(visited_ways), len(downstream_stack)
                for dest, src, n in self.index_lookup(self.conn, self.conn_src_ind, sw):
                    relway = self.index_lookup(self.wayrel, self.wayrel_wayind, dest)
                    if not len(relway):
                        downstream_ways[w].add(dest)
                        if dest not in visited_ways:
                            downstream_stack.append(dest)
                    else:
                        pass
        
        ## print single
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

        template = string.Template(open(os.path.join(os.path.dirname(__file__),
                                                     'templates','waterway.html')).read())

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

    def travers_relations(self, config, filename, area):
        rel_tree = []
        ways = set(self.ways.keys())
        rels = set(self.relations.keys())

        df = {}
        for k,v in config.items('dont_follow'):
            df[int(k)] = set([int(i) for i in v.split(',')])

        l = []
        for k,v in config.items('start_relations'):
            l.append((int(v.split(',')[0]),k))
        l.sort()

        for v,k in l:
            if int(k) in self.relations:
                rel_tree.append([int(k),1,True])
                rels.remove(int(k))
            else:
                print k, 'not in self.relations'

        cursor = len(rel_tree)
        last_len = cursor
        while True:
            cursor -= 1
            if cursor == -1:
                if len(rels) == 0:
                    break
                if len(rel_tree) == last_len:
                    rel_tree.append([rels.pop(),1,False])
                last_len = len(rel_tree)
                cursor = len(rel_tree) - 1
            rel, level, status = rel_tree[cursor]
            neighbours = self.relations[rel][3] & rels
            for n in neighbours:
                if n not in df.get(rel, set([])):
                    rel_tree.insert(cursor+1, [n, level+1, False])
                    rels.discard(n)
                else:
                    print 'do not follow: ', rel, n

        rows = []
        for rel, level, status in rel_tree:
            row = []
            row.append('<pre>'+'.'*(level-1) + str(level) + '</pre>')
            row.append('<a href="http://www.openstreetmap.org/browse/relation/%i">%i</a>' % (rel,rel))
            row.append(self.relations[rel][1].get('name', '') + self.wikipedia_links(self.relations[rel][1]))
            row.append(', '.join(['%s=%s' % (k,v) for k,v in self.relations[rel][1].items() if k.startswith('ref')]))
            row.append(self.relations[rel][1].get('destination',''))
            if level == 1:
                col = ' bgcolor="#7777FF"' if status else ' bgcolor="#FF7777"'
            else:
                col = ''
            rows.append('<tr%s>\n' %col + '\n'.join(["  <td> %s </td>" %s for s in row]) + '</tr>\n')

        template = string.Template(open(os.path.join(os.path.dirname(__file__),
                                                     'templates','watershed.html')).read())
        subst = {'ROWS': '\n'.join(rows).encode('ascii','xmlcharrefreplace'),
                 'DATE': time.strftime("%Y-%m-%d"),
                 'AREA': area,
                 'WAY_COUNT': str(len(self.ways)),
                 'CONNECTION_NODES':str(len(self.connecting_nodes)),
                 'RELATION_COUNT': str(len(self.relations)),
                 'WAY_RELATIONS': str(len(self.way_relation))}
        open(filename,'wt').write(template.safe_substitute(subst))

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
        return ' '.join(links)




class OsmWaterwayFilter(handler.ContentHandler):
    def __init__(self, write_handler):
        self.write_handler = write_handler
        self.current_object = None
        self.current_subobjects = []
        self.current_tags = {}
        self.types = set(['waterway'])
        self.waterways = set(['river','stream','canal','drain','ditch','wadi'])
        
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

class OsmWayNodes(handler.ContentHandler):
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
            poslist = [0] + [1]*(len(self.current_nodes)-2) + [2]
            for nodeid, pos in zip(self.current_nodes, poslist):
                currentfile = self.files[nodeid % self.NFILES]
                currentfile.write('%i\t%i\t%i\n' %(nodeid, self.current_wayid, pos))
        if obj == 'relation':
            for member in self.current_ways:
                self.relfile.write('%i\t%i\n' %(self.current_relid, member))
            
        


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


def waynodes(outdir):
    NFILES = 100
    waynode_filenames =  [outdir+'waynode_' + str(n)  for n in range(NFILES)]

    outfiles = [open(f,'wt') for f in waynode_filenames]
    relfile = open(outdir+'relation_way', 'wt')
    osm_handler = OsmWayNodes(outfiles, relfile)
    parser = make_parser()
    parser.setContentHandler(osm_handler)
    parser.parse(sys.stdin)

    for f in outfiles:
        f.close()
        
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
            if conn == 0:
                srcind.append(i)
            elif conn == 1:
                midind.append(i)
            else:
                destind.append(i)

    dest_file.close()
    con_file.close()
    source_file.close()
    ee_file.close()
    ss_file.close()

#################### MAIN

if sys.argv[1] == 'filter':
    waterwayfilter(sys.argv[2])
if sys.argv[1] == 'waynodes':
    waynodes(sys.argv[2])
if sys.argv[1] == 'relations':
    scanner = WaterwayRelationScanner(sys.argv[2], sys.argv[3], sys.argv[4])
    scanner.scan()



    
