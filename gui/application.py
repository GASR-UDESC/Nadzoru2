import sys
import gi
from gi.repository import GLib, Gio, Gtk

from machine.automaton import Automaton

MENU_XML = """

"""


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.note = Gtk.Notebook()
        self.statusbar = Gtk.Statusbar()

        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.note, True, True, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.note.popup_enable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

        # Create page example
        # self.page1 = Gtk.Box()
        # self.page1.set_border_width(10)
        # self.page1.add(Gtk.Label(label="Default Page!"))
        # self.note.append_page(self.page1, Gtk.Label(label="Current tab"))

        self.show_all()

    def get_image(self, name):
        try:
            f = open(name, 'r')
            return Gtk.Image.new_from_file(name)
        except:
            return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)

    def add_tab(self, widget, title, destroy_callback, param):
        note = self.note.insert_page(widget, Gtk.Label.new(title), -1)
        self.show_all()
        self.note.set_current_page(note)

        return note

    def remove_tab(self, id):
        if id:
            self.note.remove_page(id)
            destroy = self.tab.remove(id + 1)
            if destroy and destroy.destroy_callback:
                destroy.destroy_callback(destroy.param)

        self.show_all()

    def remove_current_tab(self, *args):
        id = self.note.get_current_page()
        self.remove_tab(id)

    def set_tab_page_title(self, widget, title):
        page_label = self.note.get_tab_label(widget)
        page_label.set_text(title)

        self.show_all()


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.nadzoru2.application",
            **kwargs
        )
        self.window = None
        self.elements = list()
        # self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None,)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        def create_action(action_name, callback):
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", callback)
            self.add_action(action)

        create_action("new", self.on_new_automata)
        create_action("load", self.on_load_automata)
        create_action("save", self.on_save_automata)
        create_action("edit", self.on_edit_automata)
        create_action("quit", self.on_quit)

        builder = Gtk.Builder()
        builder.add_from_file("gui/ui/menubar.ui")
        self.menubar = builder.get_object("menubar")
        self.set_menubar(self.menubar)

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self, title="Nadzoru 2")
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        self.activate()
        return

    def on_new_automata(self, action, param):
        print("You created a new automata")
        a = Automaton()
        self.elements.append(a)
        # TODO: open editor with 'a' and add in a new page (tab)

    def on_load_automata(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self.window, Gtk.FileChooserAction.OPEN,
                ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT)
        )
        result = dialog.run()
        if result == Gtk.ResponseType.ACCEPT:
            a = Automaton()
            self.elements.append(a)
            print("You loaded an automata:", dialog.get_filename())
            # TODO: load and create editor tab with a
            # a.load(dialog.get_filename())
        else:
            print("You CANCELED")
        dialog.destroy()

    def on_edit_automata(self, action, param):
        print("You opened in editor automata")

    def on_save_automata(self, action, param):
        print("You saved the automata")

    def on_quit(self, action, param):
        self.quit()
