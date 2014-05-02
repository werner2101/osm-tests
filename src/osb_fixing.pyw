#!/usr/bin/python

import sys
import urllib
import HTMLParser
from xml.dom.minidom import parse

import pygtk
pygtk.require('2.0')
import gtk

#################### CONSTANTS
VERSION = '0.0.1'


#################### CLASSES
class Bug(object):
    def __init__(self, wpt):
        self.read_wpt(wpt)
    
    def read_wpt(self, wpt):
        self.lon = float(wpt.getAttribute('lon'))
        self.lat = float(wpt.getAttribute('lat'))
        desc = wpt.getElementsByTagName('desc')[0].firstChild.data
        self.message = HTMLParser.HTMLParser().unescape(desc)
        extensions = wpt.getElementsByTagName('extensions')[0]
        self.id = int(extensions.getElementsByTagName('id')[0].firstChild.data)
        self.status = int(extensions.getElementsByTagName('closed')[0].firstChild.data)

class OpenStreetBug(object):
    def __init__(self, osb_area):
        self.osb_area = osb_area
        self.bugs = []
        self.closedbugs = 0
        self.get_osbbugs()
        self.sort_maeander()
        
    def get_osbbugs(self):
        API = 'http://openstreetbugs.schokokeks.org/api/0.1/'
        command = 'getGPX?open=yes&' + self.osb_area
        tempfile, message = urllib.urlretrieve(API+'/'+ command)
        ## TODO: check for success
        xml = parse(tempfile)
        gpx = xml.getElementsByTagName('gpx')[0]
        for wpt in gpx.getElementsByTagName('wpt'):
            bug = Bug(wpt)
            if bug.status == 0:
                self.bugs.append(bug)
            else:
                self.closedbugs += 1
        print 'Open Bugs:', len(self.bugs), 'Closed Bugs:', self.closedbugs

    def sort_maeander(self):
        self.bugs.sort(self.cmp_maeander)

    def cmp_maeander(self,a,b):
        """
        compare function for meander sort
        when the nodes are fixed in this order, the changsets will be small
        """
        MIN_X, MAX_X = -90, 90
        MIN_Y, MAX_Y = 0, 180
        DIVISOR = 3
        MAXLEVEL = 15

        ax, ay = a.lat, a.lon
        bx, by = b.lat, b.lon

        # normalise points to (0,0) to (1,1) area
        ax = (float(ax) - MIN_X)/ (MAX_X-MIN_X)
        bx = (float(bx) - MIN_X)/ (MAX_X-MIN_X)
        ay = (float(ay) - MIN_Y)/ (MAX_Y-MIN_Y)
        by = (float(by) - MIN_Y)/ (MAX_Y-MIN_Y)

        for x in xrange(MAXLEVEL):
            dirx = (int(DIVISOR*ay)%2)*2-1
            cmp_row = cmp(int(DIVISOR*ay), int(DIVISOR*by))
            if cmp_row:
                return cmp_row
            else:
                cmp_col = cmp(int(DIVISOR*ax), int(DIVISOR*bx)) * dirx
                if cmp_col:
                    return cmp_col

            diry = int(DIVISOR*ax) % 2
            dirx = int(DIVISOR*ay) % 2 # + int(DIVISOR*ax)) % 2
            ay = ay*DIVISOR - int(DIVISOR*ay)
            by = by*DIVISOR - int(DIVISOR*by)
            if diry == 1:
                ay = 1-ay
                by = 1-by
            ax = ax*DIVISOR - int(DIVISOR*ax)
            bx = bx*DIVISOR - int(DIVISOR*bx)
            if dirx == 1:
                ax = 1-ax
                bx = 1-bx
        return 0

    def josm_zoomload(self, n):
        lat = self.bugs[n].lat
        lon = self.bugs[n].lon
        d = 0.003

        command = 'load_and_zoom?left=%f&right=%f&top=%f&bottom=%f' %(lon-d, lon+d, lat+d, lat-d)
        print command
        URL='http://localhost:8111'
        answer = urllib.urlretrieve(URL+'/'+command)
        print answer
        ## second call is against a JOSM bug
        answer = urllib.urlretrieve(URL+'/'+command)
        
    def movetonotes(self, n):
        bug = self.bugs[n]
        if bug.status == 1:
            return
        # create entry in os notes
        OSM_API = 'http://api.openstreetmap.org/api/0.6/'
        message = 'Moved from OSB ID%i:\n ' %bug.id + bug.message.replace('<hr />','\n ')
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        osm_cmd = 'notes'
        post =  'lat=%f&lon=%f&text=%s' %(bug.lat, bug.lon, urllib.quote(message))
        url = OSM_API + osm_cmd
        print url, post
        tempfile, message = urllib.urlretrieve(url, data=post)
        print tempfile, message
        xml = parse(tempfile)
        note = xml.getElementsByTagName('note')[0]
        osn_id = note.getElementsByTagName('id')[0].firstChild.data

        bug.status = 1        
        # close entry in osb        
        OSB_API = 'http://openstreetbugs.schokokeks.org/api/0.1/'
        message = 'Moved to OSNotes ID' + osn_id
        osb_cmd = 'editPOIexec?id=%i&text=' %bug.id + urllib.quote(message+'. ')
        print OSB_API + osb_cmd
        tempfile, message = urllib.urlretrieve(OSB_API + osb_cmd)
        osb_cmd = 'closePOIexec?id=%i' %bug.id
        print OSB_API + osb_cmd
        tempfile, message = urllib.urlretrieve(OSB_API + osb_cmd)



class NextGPXPoint(object):

    def __init__(self):
        self.spin_items = 0
        self.create_gui()

    def create_gui(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(5)
        self.window.set_title('osb_fixing V'+VERSION)

        ## container for all elements
        vbox = gtk.VBox()
        self.window.add(vbox)

        # OSB line
        hbox_osb = gtk.HBox()
        hbox_osb.pack_start(gtk.Label('OSB area: '), False, False, 5)
        self.osb_entry = gtk.Entry()
        self.osb_entry.set_text('b=48&t=49&l=11&r=12')
        self.osb_entry.connect("activate", self.callback_osbload, None)
        hbox_osb.pack_start(self.osb_entry, True, True, 5)
        osb_button = gtk.Button('Load')
        osb_button.connect("clicked", self.callback_osbload, None)
        hbox_osb.pack_start(osb_button, False, False, 5)
        vbox.pack_start(hbox_osb, False, False, 5)

        ## point number row
        hbox_point = gtk.HBox()
        hbox_point.pack_start(gtk.Label('Bug number:'), False, False, 5)
        self.spin = gtk.SpinButton(climb_rate=1)
        self.spin.set_increments(1,10)
        self.spin.set_text('0')
        self.spin.connect('activate', self.callback_spinactivate, None)
        hbox_point.pack_start(self.spin, False, False, 5)
        self.no_points = gtk.Label()
        self.no_points.set_text('/ %i' %(self.spin_items))
        hbox_point.pack_start(self.no_points, False, False, 5)
        vbox.pack_start(hbox_point, False, False, 5)

        ## Button row
        hbox_button = gtk.HBox()
        
        button_prev = gtk.Button("Prev.")
        button_prev.connect("clicked", self.callback_prevgpx, None)
        hbox_button.pack_start(button_prev, True, True, 5)

        button_next = gtk.Button("Next")
        button_next.connect("clicked", self.callback_nextgpx, None)
        hbox_button.pack_start(button_next, True, True, 5)

        vbox.pack_start(hbox_button, False, False, 5)

        ## Bug id and description
        self.name = gtk.Label('Bug ID:')
        self.name.set_alignment(0,0)
        vbox.pack_start(self.name, False, False, 5)

        self.desc_buffer = gtk.TextBuffer()
        self.desc_buffer.set_text('bug description')
        description = gtk.TextView(self.desc_buffer)
        description.set_wrap_mode(gtk.WRAP_WORD)
        vbox.pack_start(description, True, True, 5)
      
        ## OSB to Notes
        label = gtk.Label('Transfer bug entry to OSM Notes:')
        label.set_alignment(0,0)
        vbox.pack_start(label, False, False, 5)
        move_button = gtk.Button('Move OSB bug to OSM Note')
        move_button.connect('clicked', self.callback_movetonotes)
        vbox.pack_start(move_button, False, False, 5)

        # The final step is to display this newly created widgets
        self.window.show_all()

    def main(self):
        gtk.main()

    def initdata(self):
        self.spin_items = len(self.osb.bugs)
        self.spin.set_range(1, self.spin_items + 1)
        self.no_points.set_text('/ %i  (... and %i closed bugs)' % (self.spin_items,self.osb.closedbugs))
        self.spin.set_text('0')
        self.name.set_text('Bug ID: ')
        self.desc_buffer.set_text('')

    def callback_osbload(self, widget, data=None):
        self.osb = OpenStreetBug(self.osb_entry.get_text().strip())
        self.initdata()        

    def callback_spinactivate(self, widget, data=None):
        n = int(self.spin.get_text())
        self.osb.josm_zoomload(n-1)
        self.update_content(n-1)
    
    def callback_prevgpx(self, widget, data=None):
        n = int(self.spin.get_text()) - 1
        if n < 1:
            self.out_of_range()
            return
        self.osb.josm_zoomload(n-1)
        self.spin.set_text(str(n))
        self.update_content(n-1)

    def callback_nextgpx(self, widget, data=None):
        n = int(self.spin.get_text()) + 1
        if n > self.spin_items:
            self.out_of_range()
            return
        self.osb.josm_zoomload(n-1)
        self.spin.set_text(str(n))
        self.update_content(n-1)
        
    def callback_movetonotes(self, widget, data=None):
        n = int(self.spin.get_text())
        self.osb.movetonotes(n-1)

    def update_content(self,n):
        bid = self.osb.bugs[n].id
        desc = self.osb.bugs[n].message.replace('<hr />','\n\n')

        self.name.set_text('Bug ID: ' + str(bid))
        self.desc_buffer.set_text(desc)

    def out_of_range(self):
        d = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                              type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                              message_format='Point number out of range')

        d.run()
        d.destroy()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

#################### FUNCTIONS

#################### MAIN
if __name__ == "__main__":
    hello = NextGPXPoint()
    hello.main()
