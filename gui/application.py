import sys
import gi
import os
import logging
from gi.repository import Gdk, Gio, Gtk, GLib, GObject

from gui.main_window import MainWindow

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class Application(Gtk.Application):
    def __init__(self, *args, startup_callback=None, **kwargs):
        super().__init__(*args, application_id="org.nadzoru2.application", flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE, **kwargs)
        self.elements = list()
        self.startup_callback = startup_callback
        self.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)

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
        window.set_tab_label_color(editor, 'label-red')
        self.update_menubar()

    def on_automatonlist_change(self, app, automaton_list):
        self.update_menubar()

    def add_to_automatonlist(self, automaton):
        self.elements.append(automaton)
        self.emit('nadzoru-automatonlist-change', self.get_automatonlist())

    def get_automatonlist(self): # TODO: return a iterator
        return self.elements

    def _remove_from_automaton_list(self, automaton):
        self.elements.remove(automaton)
        self.emit('nadzoru-automatonlist-change', self.get_automatonlist())

    def close_automaton(self, automaton):
        if automaton in self.get_automatonlist():
            if not self.is_automaton_open_anytype(automaton):
                self._remove_from_automaton_list(automaton)
            else:
                for tab_id, window in self.is_automaton_open_anytype(automaton):
                    if window.remove_tab(tab_id):
                        self._remove_from_automaton_list(automaton)
            return True
        else:
            return False

    def update_menubar(self):
        self._rebuild_submenubar('Automata', '_Edit', 'edit-automaton', self.on_edit_menu)
        self._rebuild_submenubar('Automata', '_Simulate', 'simulate-automaton', self.on_simulate_menu)

    def _rebuild_submenubar(self, mainmenu_label, submenu_label, new_action, callback, max_items=10):
        menu = self._get_menu(self.menubar, mainmenu_label, submenu_label)

        if menu.get_n_items() > 1:
            menu.remove(1)  # maybe write a function to verify the correct position to remove
        if len(self.get_automatonlist()) > 0:
            new_menu = Gio.Menu()
            section = Gio.MenuItem.new()
            section.set_section(new_menu)

            for index, automaton in enumerate(self.get_automatonlist()):
                if index < max_items:
                    self._create_action(new_action+str(index), callback, automaton)
                    name = automaton.get_name()
                    menuitem = Gio.MenuItem.new(name, 'app.'+new_action+str(index))
                    new_menu.append_item(menuitem)
            menu.append_item(section)

    def _get_menu(self, menu, menu_text, submenu_text=None, action_name=None):
        ''' Looks inside the given menu and returns the Gio.Menu which contains the action_name
            or the submenu that matches the submenu_text

            eg: File (menu) > New Window (action); _getmenu(self.menubar, 'File', action_name='app.new-window')
            would return the menu which contains the New Window
            eg2: Automata (menu) > Import/Export (submenu); _getmenu(self.menubar, 'File', submenu_text='Import/Export')
            would return the menu inside Import/Export submenu
        '''
        n_items = menu.get_n_items()

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
        active_window = self.get_active_window()
        active_window.add_tab_editor(automaton, automaton.get_name())

    def on_simulate_menu(self, action, target, args):
        automaton = args[0]
        active_window = self.get_active_window()
        active_window.add_tab_simulator(automaton, f"Sim: {automaton.get_name()}")

    def is_automaton_open(self, automaton, tab_type=None):
        ''' returns (tab_id, window) if the automaton is open in any tab of type tab_type;
            returns None if anything else
        '''
        windows = self.get_windows()
        automaton_location = None
        for window in windows:
            tabs_list = window.get_tabs_list()
            for tab_id, tab in tabs_list:
                if tab_type is not None and isinstance(tab, tab_type):
                    if tab.automaton is automaton:
                        automaton_location = (tab_id, window)
                        break

        return automaton_location

    def is_automaton_open_anytype(self, automaton):
        '''returns list((tab_id, window)) if the automaton is open in any tab'''
        windows = self.get_windows()
        automaton_location = list()
        for window in windows:
            tabs_list = window.get_tabs_list()
            for tab_id, tab in tabs_list:
                if hasattr(tab, 'automaton') and tab.automaton is automaton:
                    automaton_location.append((tab_id, window))
        return automaton_location


GObject.signal_new('nadzoru-automatonlist-change',
    Application,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT,))
