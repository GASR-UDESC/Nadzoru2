import sys
import gi
from gi.repository import GLib, Gio, Gtk

class AutomatonEditor:
    def __init__(self, automata):
        self.vbox = Gtk.Box(Gtk.Orientation.VERTICAL, 2)



