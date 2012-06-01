#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, string, re
from operator import itemgetter
import urllib
import hashlib
import time
import codecs

sys.path.append('python-osm/src/')
from osm import pyosm

from relations_config import TYPE_STATUS, STATUS_COLORS, TYPE_COLLECTIONS

#################### CONST
OUTDIR = '../data/02_Relationstypen/'


#################### FUNCTIONS
def e(entity, content="", tags={}):
    tagstr = ''
    for k,v in tags:
        tagstr += ' %s="%s"' % (k, urllib.quote(v))
        
    return "<%s%s>\n%s</%s>\n" %(entity, tagstr, content, entity)

def eq(entity, content="", tags={}):
    return e(entity, urllib.quote(content), tags)


def tag_hierarchy(obj, cheat=True):
    result = []
    key = 'type'
    if cheat:
        if 'type' not in obj.tags:
            for c in ['public_transport', 'line', 'place', 'boundary']:
                if c in obj.tags:
                    result.append(c)
                    key = c
                    break

    while key in obj.tags:
        val = obj.tags[key]
        if val in result: ## escape from cyclic dependancies
            break
        result.append(val)
        key = val

    return tuple(result)

def stat(osm):
    sdict = {}
    for id, rel in osm.relations.items():
        k = tag_hierarchy(rel)
        if k not in sdict:
            sdict[k] = [rel]
        else:
            sdict[k].append(rel)

    return sdict

def relation_details(filename, keys, relationlist):
    tc_keys = [ x[0] for x in TYPE_COLLECTIONS ]
    if keys in tc_keys:
        keys2 = keys[:-2]
    else:
        keys2 = keys
    tagstat = {}
    # relationlist.sort()
    for r in relationlist:
        for tagname in r.tags.keys():
            if tagname == 'type':
                continue
            if tagname in keys2:
                continue
            if tagname in tagstat:
                tagstat[tagname] += 1
            else:
                tagstat[tagname] = 1

    tagstat = sorted(tagstat.items(), key=itemgetter(1), reverse=True)
    stat_rows = []
    for tag, n in tagstat:
        stat_rows.append('<tr><td>%s</td><td>%d</td><tr>' % (tag, n))

    tag_head = ['<th>Relation-ID</th>']
    for i, (tag, n) in enumerate(tagstat):
        if i < 5:
            tag_head.append('<th>%s</th>' % tag)
        elif i == 5:
            tag_head.append('<th>further tags</th>')
        else:
            break
    if len(tag_head) < 7:
        tag_head.extend(['<th><th>'] * (7- len(tag_head)))
        
    tag_rows = []
    for r in relationlist[:3000]:
        row = ['<a href="http://www.openstreetmap.org/browse/relation/%d">%d</a>' %(r.id, r.id)]
        for i, (tag, n) in enumerate(tagstat):
            val = r.tags.get(tag, '')
            if i < 5:
                row.append(val)
            elif i >= 5:
                if val != '':
                    if len(row) != 7:
                        row.append(tag + '=' + val)
                    else:
                        row[-1] += '<br>' + tag + '=' + val
        if len(row) < 7:
            row.extend([''] * (7- len(row)))
        tag_rows.append('<tr><td>' + '</td><td>'.join(row) + '</td></tr>')

    if len(relationlist) > 3000:
        limit_note = '(only the first 3000 relations)'
    else:
        limit_note = ''

    subst = {'LIMIT_NOTE': limit_note,
             'TAGHIERARCHY': ' --&gt; '.join(keys).encode('ascii','xmlcharrefreplace'),
             'STATROWS': '\n'.join(stat_rows).encode('ascii','xmlcharrefreplace'),
             'TAGHEAD': '<tr>' + ''.join(tag_head).encode('ascii','xmlcharrefreplace') + '</tr>',
             'TAGROWS': '\n'.join(tag_rows).encode('ascii','xmlcharrefreplace')}

    templ = string.Template(open('templates/relationtypes_details.html').read())
    open(filename, 'wt').write(templ.safe_substitute(subst))

def create_regex_collections(relation_dict, type_collections):
    for tc in type_collections:
        tc_match = tc[0][:-1]
        tc_regex = tc[0][-1]
        tc_collection = []
        for k,v in relation_dict.items():
            if not len(k) == len(tc_match) + 1:
                continue
            if not k[:-1] == tc_match:
                continue
            if not re.match(tc_regex, k[-1]):
                continue
            tc_collection.extend(relation_dict.pop(k))
                    
        if tc_collection:
            relation_dict[tc[0]] = tc_collection

def print_rare_relations(filename, relation_dict, status, empty_rel):
    MAXN = 5
    ll = []
    user_dict = {}

    for reltypes, rellist in relation_dict.items():
        if len(rellist) > MAXN and len(reltypes):
            continue
        if status.get(reltypes,{}).get('status') in ['proposed', 'established']:
            continue
        for rel in rellist:
            if type(rel) != pyosm.Relation:
                continue
            if str(rel.id) in empty_rel:
                continue
            tags = rel.tags.copy()
            rtype = tags.pop('type','')
            subtype = tags.pop(rtype,'')
            user_dict[rel.user] = user_dict.get(rel.user, 0) + 1
            ll.append([str(rel.id), str(rel.changeset), rel.user, str(rel.version),
                       rtype, subtype]
                      + ["%s=%s" %(k,v) for k,v in sorted(tags.items())])

    for l in ll:
        l.insert(2, str(user_dict[l[2]]).rjust(3,' '))
    ll.sort(key=itemgetter(1,2,3,0,5,6))

    fout = codecs.open(filename, 'wt', 'utf-8')
    fout.write(u'\t'.join(['Relation','Changeset','UN','User','Version', 'type', 'subtype','tag1','tag2','tag3']) + '\n')
    for l in ll:
        fout.write(u'\t'.join(l) + '\n')
    fout.close()

def build_typestatus():
    dd = {}
    for hierarchy, status, note in TYPE_STATUS + TYPE_COLLECTIONS:
        dd[hierarchy] = {'status':status, 'note':note}
    return dd

def waterway_relations_filter(object):
    waterwayset = set(['waterway', 'stream', 'river', 'canal', 'drain','watershed','river_basin'])
    if type(object) == pyosm.Node:
        return False
    elif type(object) == pyosm.Way:
        return False
    elif type(object) == pyosm.Relation:
        k = set(object.tags.keys())
        if k & waterwayset:
            return True
        v = set(object.tags.values())
        if v & waterwayset:
            return True
        return False
    return True

def power_relations_filter(object):
    if type(object) == pyosm.Node:
        return False
    elif type(object) == pyosm.Way:
        return False
    elif type(object) == pyosm.Relation:
        powerset = set(['power'])
        k = set(object.tags.keys())
        if k & powerset:
            return True
        v = set(object.tags.values())
        if v & powerset:
            return True
        return False
    return True

def street_relations_filter(object):
    streetset = set(['street', 'relatedStreet', 'associatedStreet', 'address', 'street_number'])
    if type(object) == pyosm.Node:
        return False
    elif type(object) == pyosm.Way:
        return False
    elif type(object) == pyosm.Relation:
        k = set(object.tags.keys())
        if k & streetset:
            return True
        v = set(object.tags.values())
        if v & streetset:
            return True
        return False
    return True

def osm_relations_filter(object):
    osmset = set(['osm'])
    if type(object) == pyosm.Node:
        return False
    elif type(object) == pyosm.Way:
        return False
    elif type(object) == pyosm.Relation:
        k = set(object.tags.keys())
        if k & osmset:
            return True
        v = set(object.tags.values())
        if v & osmset:
            return True
        return False
    return True

def load_empty_relations(filename):
    empty_rel = set()
    try:
        for line in open(filename).readlines()[1:]:
            toks = line.split('\t')
            empty_rel.add(toks[3])
        return empty_rel
    except:
        return set()

#################### MAIN
prefix = sys.argv[1]
if len(sys.argv) > 2:
    filterfunc = {'waterway': waterway_relations_filter,
                  'power': power_relations_filter,
                  'street': street_relations_filter,
                  'osm': osm_relations_filter}.get(sys.argv[2])
else:
    filterfunc = None

if not os.path.exists(OUTDIR + prefix):
    os.mkdir(OUTDIR + prefix)

options={'load_relation_members': False, 'filterfunc': filterfunc}
osm = pyosm.OSMXMLFile(sys.stdin, options=options)

## remove all created by tags
for r in osm.relations.values():
    r.tags.pop('created_by','')

statdict = stat(osm)
create_regex_collections(statdict, TYPE_COLLECTIONS)

typestatus = build_typestatus()
status_colors = dict(STATUS_COLORS)

rows = []
for k,v in sorted(statdict.items()):
    if k == ('',):
        k = ("''",)
    nn = hashlib.md5(" ".join(k).encode('ascii','xmlcharrefreplace')).hexdigest()[:16]
    relation_details(OUTDIR + prefix + '/' + nn + '.html', k, v)
    rows.append('<tr bgcolor="%s"><td><a href="%s.html">%s</a></td>\n<td>%d</td><td>%s</td><td>%s</td></tr>' \
                % (status_colors.get(typestatus.get(k,{}).get('status',''),'#FFFFFF'),
                    prefix + '/' + nn, nn[:4],
                   len(v),
                   ' --&gt; '.join(k),
                   typestatus.get(k,{}).get('note','')))
    
rows = '\n'.join(rows).encode('ascii','xmlcharrefreplace')
subst = {'COLOR_ROW': ' '.join([ '<td bgcolor="%s">%s</td>' %(color,name) for name,color in STATUS_COLORS ]),
         'ROWS': rows,
         'RELATION_COUNT': str(len(osm.relations)),
         'RELATION_TYPES': str(len(statdict)),
         'DATE': time.strftime("%Y-%m-%d"),
         'AREA': prefix,
         'TOPLEVEL_TYPES': len(set([k[0] for k in statdict.keys() if len(k)]))}

templ = string.Template(open('templates/relationtypes_index.html').read())
open(OUTDIR + prefix + '.html', 'wt').write(templ.safe_substitute(subst))

## extra list for rare relations
empty_rel = load_empty_relations(OUTDIR + prefix + '/' + 'empty_relations.txt')
print_rare_relations(OUTDIR + prefix + '/' + 'rare_relations.txt', statdict, typestatus, empty_rel)



