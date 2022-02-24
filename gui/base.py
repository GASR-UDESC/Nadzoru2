import gi
from gi.repository import GLib, Gio, Gtk, GObject

class PageMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._changes_to_save = False

    def get_ancestor_window(self): # use this to pegar a window # Perguntar se o usuario quer abrir o automato
        return self.get_ancestor(Gtk.Window)

    def has_changes_to_save(self):
        return self._changes_to_save

    def has_file_path_name(self):
        return False

    def get_tab_name(self):
        return ''
        
