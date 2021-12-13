import gi
from gi.repository import GLib, Gio, Gtk, GObject

class PageMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__changes_to_save = False

    def get_ancestor_window(self):
        return self.get_ancestor(Gtk.Window)

    def has_changes_to_save(self):
        return self.__changes_to_save
