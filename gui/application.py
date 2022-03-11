import sys
import gi
import os
import logging
from gi.repository import Gdk, Gio, Gtk, GLib

from gui.main_window import MainWindow

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class Application(Gtk.Application):
    def __init__(self, *args, startup_callback=None, **kwargs):
        super().__init__(*args, application_id="org.nadzoru2.application", flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE, **kwargs)
        self.elements = list()
        self.startup_callback = startup_callback

        self.add_main_option("log", ord("l"), GLib.OptionFlags.NONE, GLib.OptionArg.STRING, "Log level", None)

    def _create_action(self, action_name, callback, *args):
        action = Gio.SimpleAction.new(action_name, None)
        if not args:
            action.connect("activate", callback)
            self.add_action(action)
        else:
            action.connect("activate", callback, args)
            self.add_action(action)

    def add_window(self, title="Nadzoru 2"):
        new_window = MainWindow(application=self, title=title)
        return new_window

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.add_window()

        self._create_action('quit', self.on_quit)
        self._create_action('new-window', self.on_new_window)

        builder = Gtk.Builder()
        builder.add_from_file("gui/ui/menubar.ui")
        self.menubar = builder.get_object("menubar")
        self.set_menubar(self.menubar)

        if self.startup_callback is not None:
            self.startup_callback(self)

    def do_activate(self):
        logging.debug("")
        for window in self.get_windows():
            window.show_all()
            window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        numeric_level = logging.INFO
        if 'log' in options:
            numeric_level = getattr(logging, options['log'].upper(), logging.INFO)
        logging.basicConfig(level=numeric_level, format='%(levelname)s:%(filename)s:%(funcName)s:%(message)s')

        logging.debug("")

        self.activate()
        return True

    def on_quit(self, action, param):
        logging.debug("")
        for window in self.get_windows():
            if window.remove_tabs() == False:
                return  # Abort quitting
        self.quit()

    def on_new_window(self, action, param):
        logging.debug("")
        window = self.add_window()
        window.show_all()
        window.present()

    def on_editor_change(self, editor, *args):
        logging.debug("")
        window = editor.get_ancestor_window()
        window.set_tab_label_color(editor, '#F00')

    def add_to_automatonlist(self, automaton):  # maybe should be moved to application?
        self.elements.append(automaton)
        self.update_menubar()

    def update_menubar(self): # For now, only adds the name of the automaton name in the edit submenu. It isn't linking to any action yet
        menu = self._get_menu(self.menubar, 'Automata', submenu_text='Edit')
        if menu.get_n_items() > 1:
            menu.remove(1)      # maybe write a function to verify the correct position to remove
        if len(self.elements) > 0:
            edit_menu = Gio.Menu()
            section = Gio.MenuItem.new()
            section.set_section(edit_menu)
            for index, automaton in enumerate(self.elements):
                name = automaton.get_name()

                self._create_action('edit-single-automaton'+str(index), self.on_edit_menu, automaton)

                # action = Gio.SimpleAction.new('edit-single-automaton'+str(index))
                # action.connect("activate", self.on_edit_menu, automaton)
                
                # self.add_action(action)
                
                menuitem = Gio.MenuItem.new(name, 'app.edit-single-automaton'+str(index))
                edit_menu.append_item(menuitem)
            
            menu.append_item(section)

    def _get_menu(self, menu, menu_text, submenu_text=None, action_name=None):  # this could be better by scanning all menuitems 
        n_items = menu.get_n_items()                                            # so it wouldn't be needed to specify a menu, eg: 'Automata'
        
        for item_n in range(n_items):
            item_att_iter = menu.iterate_item_attributes(item_n)
            item_link_iter = menu.iterate_item_links(item_n)
            _, _type, value = item_att_iter.get_next()
            _, _link, menumodel = item_link_iter.get_next()

            if _link == 'submenu':
                if value.get_string() == menu_text:
                    r_menu = self._get_menu(menumodel, menu_text, submenu_text, action_name)
                    if r_menu is not None:
                        return r_menu
                elif value.get_string() == submenu_text:
                    return menumodel

            elif _link == 'section':
                r_menu = self._get_menu(menumodel, menu_text, submenu_text, action_name)
                if r_menu is not None:
                    return r_menu
            elif _type == 'action' and value.get_string() == action_name:
                return menu

    def on_edit_menu(self, action, target, args):
        automaton = args[0]
        print(automaton)
        active_win = self.get_active_window()
        active_win.add_tab_editor(automaton, automaton.get_name())

