import sys
import gi
from gi.repository import GLib, Gio, Gtk
import os

MENU_XML = """

"""
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.tab = letk.List.new()
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.menubar = Gtk.MenuBar()
        self.note = Gtk.Notebook()
        self.statusbar = Gtk.Statusbar()

        # Without Close Button
        # self.header = Gtk.HeaderBar()
        # self.header.set_show_close_button(False)
        # self.set_titlebar(self.header)

        self.actions = {}

        # Menu
        # self.menu = {}
        # self.menu_item = {}

        # self.append_menu('file', "_File")
        # self.append_menu_item('file', "_Close Tab", "Close The Active Tab", 'gtk-delete', self.remove_current_tab, self )
        # self.append_menu_separator('menubar')
        # self.append_menu_item('file', "_Quit nadzoru", "Quit nadzoru", 'gtk-quit', Gtk.main_quit, self )

        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.menubar, False, False, 0)
        self.vbox.pack_start(self.note, True, True, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        #self.connect("delete-event", Gtk.main_quit)

        self.note.popup_enable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(Gtk.Label(label="Default Page!"))
        self.note.append_page(self.page1, Gtk.Label(label="Current tab"))

        self.show_all()

    def append_menu(self, name, caption):
        self.menu[name] = Gtk.Menu()
        # menu_item = Gtk.MenuItem.new_with_mnemonic(caption)
        # menu_item.set_submenu(self.menu[name])
        # self.menubar.append(menu_item)

        # self.menu_item[name] = {}

        # return menu_item

    def prepend_menu(self, name, caption):
        self.menu[name] = Gtk.Menu.new()
        menu_item = Gtk.MenuItem.new_with_mnemonic(caption)
        menu_item.set_submenu(self.menu[name])
        self.menubar.prepend(menu_item)

        self.menu_item[name] = {}

        return menu_item

    def append_sub_menu(self, parent, name, caption):
        self.menu[name] = Gtk.Menu.new()
        menu_item = Gtk.MenuItem.new_with_mnemonic(caption)
        menu_item.set_submenu(self.menu[name])
        self.menu[parent].append(menu_item)

        self.menu_item[name] = {}

        return menu_item

    def prepend_sub_menu(self, parent, name, caption):
        self.menu[name] = Gtk.Menu.new()
        menu_item = Gtk.MenuItem.new_with_mnemonic(caption)
        menu_item.set_submenu(self.menu[name])
        self.menu[parent].prepend(menu_item)

        self.menu_item[name] = {}

        return menu_item

    def append_menu_separator(self, name):
        separator = Gtk.SeparatorMenuItem.new()
        self.menu[name].append(separator)

    def prepend_menu_separator(self, name):
        separator = Gtk.SeparatorMenuItem.new()
        self.menu[name].prepend(separator)

    def remove_menu(self, name):
        self.menubar.remove(name)
        self.menu_item[name] = None

    def getImage(self, name):
        try:
            f = open(name, 'r')
            return Gtk.Image.new_from_file(name)
        except:
            return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)

    def append_menu_item(self, menu_name, caption, hint, icon, callback, param, *args):
        menu_item = None
        if icon:
            box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            image = self.getImage(icon)
            label = Gtk.Label()
            label.set_markup_with_mnemonic(caption)
            label.set_justify(Gtk.Justification.LEFT)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, False, False, 5)
            menu_item = Gtk.MenuItem.new()
            menu_item.add(box)
        else:
            menu_item = Gtk.MenuItem.new_with_mnemonic(caption)
            menu_item.connect('activate', callback, param)

        if self.menu[menu_name]:
            self.menu[menu_name].append(menu_item)
            self.menu_item[menu_name][len(
                self.menu_item[menu_name]) + 1] = menu_item

        if args:
            return menu_item, self.append_menu_item(menu_name, args)

        return menu_item

    def prepend_menu_item(self, menu_name, caption, hint, icon, callback, param, *args):
        menu_item = None
        if icon:
            box = Gtk.Box()
            image = self.getImage(icon)
            label = Gtk.Label.new()
            label.set_markup_with_mnemonic(caption)
            label.set_justify(Gtk.JUSTIFY_LEFT)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, False, False, 5)
            menu_item = Gtk.MenuItem.new()
            menu_item.add(box)
        else:
            menu_item = Gtk.MenuItem.new_with_mnemonic(caption)
            menu_item.connect('activate', callback, param)

        if self.menu[menu_name]:
            self.menu[menu_name].prepend(menu_item)
            self.menu_item[menu_name][len(
                self.menu_item[menu_name]) + 1] = menu_item

        if args:
            return menu_item, self.append_menu_item(menu_name, args)

        return menu_item

    def remove_menu_item(self, menu_name, menu_item):
        self.menu[menu_name].remove(menu_item)
        pos = None
        for ch, val in enumerate(self.menu_item[menu_name]):
            if val == menu_item:
                pos = ch

        if pos:
            last = self.menu_item[menu_name]
            self.menu_item[menu_name][pos] = None
            self.menu_item[menu_name][pos] = self.menu_item[menu_name][last]

    def add_tab(self, widget, title, destroy_callback, param):
        note = self.note.insert_page(widget, Gtk.Label.new(title), -1)
        # self.tab.add({ destroy_callback = destroy_callback, param = param, widget = widget }, note + 1)
        self.show_all()
        self.note.set_current_page(note)

        return note

    def remove_current_tab(self, *args):
        id = self.note.get_current_page()
        print(id)
        self.remove_tab(id)

    def remove_tab(self, id):
        if id:
            self.note.remove_page(id)
            destroy = self.tab.remove(id + 1)
            if destroy and destroy.destroy_callback:
                destroy.destroy_callback(destroy.param)

        self.show_all()

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
        create_action("edit", self.on_op_editor_automata)
        create_action("quit", self.on_quit)
        builder = Gtk.Builder()
        builder.add_from_file("gui/ui/menubar.ui")
        self.menubar = builder.get_object("menubar")
        self.set_app_menu(self.menubar)
        print(self.menubar)

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self, title="Nadzoru 2")

        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack())

        self.activate()
        return

    def on_new_automata(self, action, param):
        print("You created a new automata")

    def on_load_automata(self, action, param):
        print("You loaded an automata")

    def on_op_editor_automata(self, action, param):
        print("You opened in editor automata")

    def on_save_automata(self, action, param):
        print("You saved the automata")

    def on_quit(self, action, param):
        self.quit()
