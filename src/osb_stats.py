#!/usr/bin/python
# -*- coding:  utf-8 -*-

import string, time, os
import MySQLdb
import pylab,numpy
import matplotlib.pyplot as plt

#################### CONSTANTS
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
TEMPLATEDIR = os.path.join(BASEDIR, 'templates')
DB_DIR = os.path.join(BASEDIR, '../../osb/db/')
OUTDIR = os.path.join(BASEDIR, '../../data/09_osb_phaseout/')

DATE = time.strftime("%Y-%m-%d")

## db setup
DB_HOST = "localhost"
DB_NAME = "osb"
#DB_USER = "werner@localhososb_user2"
#DB_PASSWORD = "PASSWORD"

#################### classes
class Point(object):
    def __init__(self, bugid, lon, lat, text, btype, last_changed, date_created, nearby_place):
        self.id = bugid
        self.lon = lon
        self.lat = lat
        self.text = text
        self.type = btype
        self.last_changed = last_changed
        self.date_created = date_created
        self.nearby_place = nearby_place

class Batch(object):
    def __init__(self, points, name=''): 
        self.name = name
        self.points = points
        self.len = len(points)
        self.max_lat = max([p.lat for p in self.points])
        self.min_lat = min([p.lat for p in self.points])
        self.max_lon = max([p.lon for p in self.points])
        self.min_lon = min([p.lon for p in self.points])
    
    def get_area(self):
        tol = 0.000001
        return 'b=%f&t=%f&l=%f&r=%f' % (self.min_lat-tol, self.max_lat+tol, 
                                        self.min_lon-tol, self.max_lon+tol)

#################### FUNCTIONS
def batch_splitter(batch, MAXN=100, SPLITTER=2):
    batches_todo = [batch]
    batches_complete = []

    while batches_todo:
        batch_cp = list(batches_todo)
        batches_todo = []
        for batch in batch_cp:
            if (batch.max_lat-batch.min_lat) > (batch.max_lon - batch.min_lon):
                points = [(p.lat, p) for p in batch.points]
                namesuffix = 'y'
            else:
                points = [(p.lon, p) for p in batch.points]
                namesuffix='x'
            points.sort()

            npoints = batch.len/SPLITTER + 1
            for s in xrange(SPLITTER):
                newname = batch.name + namesuffix + str(s)
                newbatch = Batch([p[1] for p in points[s*npoints:(s+1)*npoints]], newname)
                if newbatch.len > MAXN:
                    batches_todo.append(newbatch)
                else:
                    batches_complete.append(newbatch)

    return batches_complete

def open_bugs():
    """
    read all open bugs from local database
    """
    bugs = []

##    conn = MySQLdb.connect(DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
    conn = MySQLdb.connect(DB_HOST, db=DB_NAME)
    curs = conn.cursor()
    ## since 1. oct    
    #curs.execute("SELECT id, lon, lat, text, type, last_changed, date_created, nearby_place FROM bugs WHERE type = 0 and id > 752300")
    ## since 15. Oct    
    #curs.execute("SELECT id, lon, lat, text, type, last_changed, date_created, nearby_place FROM bugs WHERE type = 0 and id > 754500")
    ## all
    curs.execute("SELECT id, lon, lat, text, type, last_changed, date_created, nearby_place FROM bugs WHERE type = 0")
    
    for c in curs:
        bug = Point(*c)
        bugs.append(bug)
    conn.close()
    return bugs

#################### MAIN

bugs = open_bugs()
print len(bugs)

## create and split batch
batches_complete = batch_splitter(Batch(bugs))

## bugs by country
country = {}
for bug in bugs:
    nb = bug.nearby_place[-4:]
    if nb in country:
        country[nb].append(bug)
    else:
        country[nb] = [bug]
country_rows = []
for v,k,bl in sorted([(len(i[1]),i[0],i[1]) for i in country.items()], reverse=True):
    batch = Batch(bl)
    country_rows.append('<tr><td>%s</td><td>%i</td><td>%s</td></tr>' %(k,v,batch.get_area()))

## view / print the batches
font = {'family' : 'serif',
        'color'  : 'darkblue',
        'weight' : 'normal',
        'size'   : 8,
        }
htmlrows = []
for n,b in enumerate(batches_complete):
    osbarea_str = b.get_area()
    osbarea = (b.max_lon - b.min_lon)*(b.max_lat - b.min_lat)
    nbplace = b.points[0].nearby_place.decode('utf_8')
    nbplace = nbplace.encode('ascii','xmlcharrefreplace')
    print n, b.name, b.len, osbarea_str, nbplace, osbarea
    tds = ['%i' %n,
           '%i' %b.len,
           nbplace[-4:] + ' ' + nbplace[:-5],
           osbarea_str + ' (<a href="http://openstreetbugs.schokokeks.org/api/0.1/getGPX?%s&open=yes">gpx</a>)'%osbarea_str,
           '%.3f' % osbarea,
           b.name]
    htmlrows.append('<tr><td>' + '</td><td>'.join(tds) + '</td></tr>')

    plt.plot([p.lon for p in b.points],[p.lat for p in b.points],'r,')
    plt.plot([b.min_lon,b.min_lon,b.max_lon,b.max_lon,b.min_lon],
             [b.min_lat,b.max_lat,b.max_lat,b.min_lat,b.min_lat],'k')
    if (b.max_lon - b.min_lon)> 5 and (b.max_lat - b.min_lat)>2:
        plt.text((b.min_lon+b.max_lon)/2,(b.min_lat+b.max_lat)/2,
                 str(n),fontdict=font,
                 horizontalalignment='center', verticalalignment='center')

plt.grid()
plt.title('Open Bugs in OSB (<100 bugs/rectangle) Date: '+ DATE)
plt.savefig(OUTDIR+'osb_openbugs.png')
#plt.show()
plt.xlim((-10,50))
plt.ylim((30,70))
plt.savefig(OUTDIR+'osb_openbugs_eu.png')
plt.close()

template = string.Template(open(os.path.join(TEMPLATEDIR,'osb_stats.html')).read())
subst = {'ROWS': '\n'.join(htmlrows),
         'STAT': '\n'.join(country_rows),
         'NO_COUNTRIES': str(len(country)),
         'DATE': DATE}
filename = os.path.join(OUTDIR, 'index.html')
open(filename,'wt').write(template.safe_substitute(subst))    

## statistics
bid = numpy.array([b.id for b in bugs])
d_open = numpy.array([b.date_created for b in bugs])
d_comment = numpy.array([b.last_changed for b in bugs])
d_open_s = numpy.array(sorted(d_open))
d_comment_s = numpy.array(sorted(d_comment))
y = numpy.linspace(1,len(d_open),len(d_open))
pylab.plot(d_open_s, y, label='opening date')
pylab.plot(d_comment_s, y, label='comment date')
pylab.title('open Bugs in OSB ordered by creation date')
pylab.legend(loc='best')
pylab.grid()
pylab.savefig(OUTDIR + 'osb_creation_date.png')
#pylab.show()
pylab.close()

## plot date vs. ID
pylab.plot(numpy.array(d_open),bid,'.')
pylab.grid()
pylab.title('Creation date vs. Bug ID')
pylab.savefig(OUTDIR + 'osb_creation_vs_bugid.png')
#pylab.show()
pylab.close()

## plot open bugs over time
conn = MySQLdb.connect(DB_HOST, db=DB_NAME)
curs = conn.cursor()
curs.execute("SELECT type, date_created, last_changed FROM bugs")

bugs = []
for t, dc, lc in curs:
    if t == 0:
        bugs.append((dc,1))
    else:
        bugs.append((dc,1))
        bugs.append((lc,-1))
bugs.sort()

date = numpy.array([b[0] for b in bugs])
inc_dec = numpy.array([b[1] for b in bugs])
bugs_open = numpy.cumsum(inc_dec)

pylab.subplot(211)
pylab.plot(date,bugs_open)
pylab.grid()
pylab.title('Open Bugs in OSB (currently %i)' %bugs_open[-1])

pylab.subplot(212)
nhide = 570000
pylab.plot(date[nhide:],bugs_open[nhide:])
pylab.grid()
pylab.savefig(OUTDIR + 'osb_open_bugs.png')
#pylab.show()
pylab.close()

## bugs created and closed by month
conn = MySQLdb.connect(DB_HOST, db=DB_NAME)
curs = conn.cursor()
curs.execute("SELECT YEAR(date_created)+MONTH(date_created)/12,count(distinct id) FROM bugs GROUP BY YEAR(date_created)+ MONTH(date_created)/12;")
b_created = curs.fetchall()

curs.execute("SELECT YEAR(last_changed)+MONTH(last_changed)/12,count(distinct id) FROM bugs WHERE type <> 0 GROUP BY YEAR(last_changed)+ MONTH(last_changed)/12;")
b_closed = curs.fetchall()
pylab.plot([x[0]-2000 for x in b_created],[y[1] for y in b_created],label='bugs created')
pylab.plot([x[0]-2000 for x in b_closed],[y[1] for y in b_closed],label='bugs closed')
pylab.grid()
pylab.title('Opend and closed bugs (by month)')
pylab.legend(loc='best')
pylab.xlabel('Year 20xx')
#pylab.show()
pylab.savefig(OUTDIR + 'osb_opendclosed.png')
pylab.close()




               
        
    
