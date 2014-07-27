#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Notes dump: http://grant.dev.openstreetmap.org/tmp/planet-notes-dump-testing/
# bzcat osm_files/notes-dump.osn.bz2 | python src/osm-tests/src/notes_stat.py

import sys, re
from xml.sax import handler, make_parser
import numpy, pylab, matplotlib
from datetime import datetime

#################### CONSTANTS
OUTDIR='../data/09_osb_phaseout/'

#################### CLASSES
class OsmNotes(handler.ContentHandler):
    def __init__(self):
        self.opened = []
        self.closed = []
        self.__created = ''
        self.__closed = ''
        self.__match = False
        self.__osn_comment_nr = 0
        
    def startElement(self, obj, attrs):
        if obj == 'note':
            self.__created = attrs['created_at']
            if 'closed_at' in attrs:
                self.__closed = attrs['closed_at']
                
        elif obj == 'comment':
            self.__osn_comment_nr += 1

    def characters(self, content):
        if self.__osn_comment_nr > 1:
            return
        if re.match('.*Moved from OSB ID.*|.*OSB.*|.*openstreetbugs.*',content, re.IGNORECASE):
            self.__match = True

    def endElement(self, obj):
        if obj == 'note':
            if self.__match:
                self.opened.append(self.__created)
                if self.__closed:
                    self.closed.append(self.__closed)

            self.__created = ''
            self.__closed = ''
            self.__match = False
            self.__osn_comment_nr = 0


def plot_cdf(opened, closed, filename):
    lenopened = len(opened)
    lenclosed = len(closed)
    opened = numpy.array(opened, dtype='datetime64').astype(datetime)
    closed = numpy.array(closed, dtype='datetime64').astype(datetime)
    opened.sort()
    closed.sort()
    
    all_notes = []
    for n in opened:
        all_notes.append((n,1))
    for n in closed:
        all_notes.append((n,-1))
    all_notes.sort()
    
    pylab.subplot(211)
    pylab.title("Notes moved from Openstreetbugs")
    pylab.plot(opened, numpy.arange(lenopened)+1, label='opened Notes')
    pylab.plot(closed, numpy.arange(lenclosed)+1, label='closed Notes')
    pylab.legend(loc='upper left')
    pylab.grid()

    pylab.subplot(212)
    pylab.plot([n[0] for n in all_notes],
               numpy.cumsum([n[1] for n in all_notes]),
               label='open notes')
    pylab.legend(loc='upper left')
    pylab.xlabel('date')
    pylab.grid()
    pylab.savefig(filename)
    pylab.show()
    pylab.close()    

#################### MAIN
osm_handler = OsmNotes()

parser = make_parser()
parser.setContentHandler(osm_handler)
parser.parse(sys.stdin)

print len(osm_handler.opened), len(osm_handler.closed)
print osm_handler.opened[:5], osm_handler.closed[:5]

plot_cdf(osm_handler.opened, osm_handler.closed, 'notes_from_osb.png')
