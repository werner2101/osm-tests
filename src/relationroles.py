#!/usr/bin/python
# -*- coding:  utf-8 -*-

import sys, string, re, time, os
from xml.sax import handler, make_parser
import xml.sax.saxutils
import codecs
import numpy

import relations_config

sys.path.append('../python-osm/src/')
from osm import pyosm


#################### CONSTANTS
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
TEMPLATEDIR = os.path.join(BASEDIR, 'templates')
RELATION_ROLES = relations_config.RELATION_ROLES


#################### CLASSES
class BadRolesFilter(handler.ContentHandler):
    def __init__(self):
        self.current_object = None
        self.current_subobjects = []
        self.current_tags = {}
        self.lines = ['\t'.join(['type', 'rel_id', 'name', 'role', 'obj', 'count'])]

        
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
            self.current_tags[attrs['k']] = attrs['v']
        if obj == 'member':
            self.current_subobjects.append((obj,dict(attrs)))

    def endElement(self, obj):
        if obj == 'way':
            if self.current_tags.get('waterway','x') in self.waterways:
                self.write_object()
            
        elif obj == 'relation':
            rtype = self.current_tags.get('type')
            if rtype in RELATION_ROLES:
                pattern = RELATION_ROLES[rtype]

                badrole = {}
                for obj,m in self.current_subobjects:
                    mobj = m['type']
                    robj = m['role']
                    if mobj[0] not in pattern.get(robj,''):
                        k = (str(mobj[0]), robj)
                        if k in badrole:
                            badrole[k] = badrole[k] + 1
                        else:
                            badrole[k] = 1

                for tp_role, count in badrole.items():
                    mobj, robj = tp_role
                    rid = self.current_object[1]['id']
                    rname = self.current_tags.get('name','')
                    self.lines.append('\t'.join([rtype,rid,rname,robj,mobj,str(count)]))

#################### MAIN
## split up the analyses in different tasks
# usage: program command [args]

if True:
    # input is stdin
    outfile = sys.argv[1]
    osm_handler = BadRolesFilter()
    parser = make_parser()
    parser.setContentHandler(osm_handler)
    parser.parse(sys.stdin)

    fout = codecs.open(outfile, 'wt', 'utf-8')
    fout.write('\n'.join(osm_handler.lines))
    fout.close()
               
    
    
