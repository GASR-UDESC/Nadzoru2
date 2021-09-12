import sys
import gi
from gi.repository import GLib, Gio, Gtk

from render import AutomatonRender

class AutomatonEditor:
    def __init__(self, automaton):
        self.automaton = automaton
        self.ar = AutomatonRender()
        self.selected_state = None
        self.build()

    def build(self):
        # self.builder = Gtk.Builder()
        # self.builder.add_from_file('gui/ui/editor.glade')

        # self.box = self.builder.get_object('toplevel_box')
        # self.darea = self.builder.get_object('draw')
        # self.listbox = self.builder.get_object('event_listbox')

        # self.darea.connect("draw", self.on_draw)
        # self.builder.connect_signals(self)

        self.box = Gtk.Box(spacing=2)
        self.paned = Gtk.Paned()


        #~ self.box.pack_start(self.xxxx, True, True, 0)

    def get_root_widget(self):
        return self.box

    def on_draw(self, wid, cr):
        self.ar.draw(cr, self.automaton)


