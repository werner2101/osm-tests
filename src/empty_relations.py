#!/usr/bin/python
# -*- coding:  utf-8 -*-

import sys, string, re, time, os
from xml.sax import handler, make_parser
from operator import itemgetter
import codecs

#################### CONSTANTS
OUTDIR='../data/02_Relationstypen/'

#################### CLASSES
class OsmEmptyRelations(handler.ContentHandler):
    def __init__(self):
        self.relations = []
        self.member_relations = set([])
        self.__rel_tags = {}
        self.__rel_attrs = {}
        self.__rel_has_member = False

    def startElement(self, obj, attrs):
        if obj == 'relation':
            self.__rel_attrs = attrs
            self.__rel_tags = {}
            self.__rel_has_member = False
        elif obj == 'tag':
            self.__rel_tags[attrs['k']] = attrs['v']
        elif obj == 'member':
            self.__rel_has_member = True
            if attrs.get('type','') == 'relation':
                self.member_relations.add(attrs.get('ref',''))

    def endElement(self, obj):
        if obj == "relation":
            if not self.__rel_has_member:
                self.relations.append((self.__rel_attrs, self.__rel_tags))


def print_empty_relations(filename, relations, member_relations):
    table = []
    user_dict = {}

    for attrs, tags in relations:
        rel_id = attrs.get('id','')
        rel_changeset = attrs.get('changeset', '')
        rel_user = attrs.get('user', '')
        rel_version = attrs.get('version', '')
        rel_date = attrs.get('timestamp', '')[:10]

        tags = tags.copy()
        rtype = tags.pop('type','')
        subtype = tags.pop(rtype,'')
        user_dict[rel_user] = user_dict.get(rel_user, 0) + 1
        table.append(['M', str(rel_date), rel_changeset, str(rel_id), str(rel_version), 
                      'UN', rel_user, rtype, subtype]
                     + ["%s=%s" %(k,v) for k,v in sorted(tags.items())])

    table.sort(key=itemgetter(2))

    for line in table:
        line[5] = str(user_dict[line[6]])
        if line[3] in member_relations:
            line[0] = 'X'
        else:
            line[0] = ''
        line[2] = str(line[2])


    fout = codecs.open(filename, 'wt', 'utf-8')
    fout.write(u'\t'.join(['M','Timestamp','Changeset', 'Relation','Version','UN','User',
                           'type','subtype','tag1','tag2','tag3','tag4','tag5']) + '\n')
    for line in table:
        fout.write(u'\t'.join(line) + '\n')
    fout.close()

    return user_dict

def e(entity, content="", tags={}):
    tagstr = ''
    for k,v in tags:
        tagstr += ' %s="%s"' % (k, urllib.quote(v))
        
    return "<%s%s>\n%s\n</%s>\n" %(entity, tagstr, content, entity)


def create_user_stat(filename, user_dict):

    count_dict = {}
    total = 0

    for user, count in user_dict.items():
        if count in count_dict:
            count_dict[count].append(user)
        else:
            count_dict[count] = [user]

        total += count

    rows = []
    for count, users in sorted(count_dict.items(), reverse=True):
        users.sort()
        row = e('tr',
                e('td', str(count)) + \
                e('td', "%.3f%%" % (100.0*count*len(users)/total)) + \
                e('td', ',\n'.join(users)) + \
                e('td', ''))
                  
        rows.append(row)

    subst = {'RELATION_COUNT': str(total),
             'DATE': time.strftime("%Y-%m-%d"),
             'USERROWS': '\n'.join(rows).encode('ascii','xmlcharrefreplace')}

    templ = string.Template(open(os.path.dirname(__file__) + '/templates/empty_relations.html').read())
    open(filename, 'wt').write(templ.safe_substitute(subst))
    

#################### MAIN
osm_handler = OsmEmptyRelations()
area = sys.argv[1]

if not os.path.exists(OUTDIR + area):
    os.mkdir(OUTDIR + area)

parser = make_parser()
parser.setContentHandler(osm_handler)
parser.parse(sys.stdin)

user_dict = print_empty_relations(OUTDIR + area + '/empty_relations.txt',
                                  osm_handler.relations, osm_handler.member_relations)
create_user_stat(OUTDIR + '/empty_relations.html', user_dict)


