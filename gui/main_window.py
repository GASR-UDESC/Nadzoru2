import sys
import gi
from gi.repository import Gdk, Gio, Gtk

from gui.tool_palette import ToolPalette
from gui.automaton_editor import AutomatonEditor


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.toolpallet = ToolPalette(width_request=148)
        self.note = Gtk.Notebook()
        self.statusbar = Gtk.Statusbar()

        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.hbox, True, True, 0)
        self.hbox.pack_start(self.toolpallet, False, True, 0)
        self.hbox.pack_start(self.note, True, True, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        # self.note.popup_enable()
        self.note.popup_disable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

    def do_delete_event(self, event):
        self.props.application.validade_quit()
        return True

    def get_image(self, name):
        try:
            f = open(name, 'r')
            return Gtk.Image.new_from_file(name)
        except:
            return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)

    def add_tab(self, widget, title):
        note = self.note.insert_page(widget, Gtk.Label.new(title), -1)
        self.show_all()
        self.note.set_current_page(note)

        return note

    def remove_tab(self, _id):
        if _id >= 0:
            self.note.remove_page(_id)
            self.show_all()

    def remove_current_tab(self, *args):
        _id = self.note.get_current_page()
        self.remove_tab(_id)

    def get_current_tab_widget(self):
        _id = self.note.get_current_page()
        return self.note.get_nth_page(_id)

    def set_tab_page_title(self, widget, title):
        label = self.note.get_tab_label(widget)
        label.set_text(title)
        self.show_all()

    def set_tab_label_color(self, widget, color="#000000"):
        label = self.note.get_tab_label(widget)

        rgba = Gdk.RGBA(0, 0, 0)
        rgba.parse(color)
        label.override_color(Gtk.StateFlags.NORMAL, rgba)

        self.show_all()
