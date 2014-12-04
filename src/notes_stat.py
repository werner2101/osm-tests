#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Notes dump: http://grant.dev.openstreetmap.org/tmp/planet-notes-dump-testing/
# bzcat osm_files/notes-dump.osn.bz2 | python src/osm-tests/src/notes_stat.py

import sys, re
from xml.sax import handler, make_parser
import numpy, pylab, matplotlib
from datetime import datetime

#################### CONSTANTS
OUTDIR='data/10_notes_statistics/'

#################### CLASSES
class OsmNotes(handler.ContentHandler):
    def __init__(self, filter_osb='no'):
        self.opened = []
        self.closed = []
        self.filter_osb = filter_osb
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
                    
        if self.filter_osb == 'yes':
            if re.match('.*Moved from OSB ID.*|.*OSB.*|.*openstreetbugs.*',content, re.IGNORECASE):
                self.__match = True
        else:
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
    pylab.plot(opened, numpy.arange(lenopened)+1, label='opened Notes')
    pylab.plot(closed, numpy.arange(lenclosed)+1, label='closed Notes')
    pylab.legend(loc='upper left')
    pylab.grid()

    pylab.subplot(212)
    pylab.plot([n[0] for n in all_notes],
               numpy.cumsum([n[1] for n in all_notes]),
               label='open notes')
    pylab.legend(loc='upper left')
    pylab.grid()
    pylab.savefig(filename)
#    pylab.show()
    pylab.close()    

#################### MAIN

plotname = sys.argv[1]
filter_osb = sys.argv[2]

osm_handler = OsmNotes(filter_osb)

parser = make_parser()
parser.setContentHandler(osm_handler)
parser.parse(sys.stdin)

#print len(osm_handler.opened), len(osm_handler.closed)
#print osm_handler.opened[:5], osm_handler.closed[:5]

plot_cdf(osm_handler.opened, osm_handler.closed, OUTDIR + plotname)
