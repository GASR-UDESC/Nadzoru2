#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk

from renderer import AutomatonRenderer

class AutomatonEditor(Gtk.Box):
    def __init__(self, automaton, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.automaton = automaton
        self.ar = AutomatonRenderer(self.automaton)
        self.selected_state = None
        self._build()

    def _build(self):
        self.paned = Gtk.Paned()
        self.scrolled = Gtk.ScrolledWindow.new()
        self.drawing_area = Gtk.DrawingArea.new()
        # self.listbox = Gtk.

        self.pack_start(self.paned, True, True, 0)
        self.paned.pack1(self.scrolled, True, True)
        self.scrolled.add(self.drawing_area)


        self.drawing_area.connect("draw", self.on_draw)

    def on_draw(self, wid, cr):
        pass
        # self.ar.draw(cr, self.automaton)


