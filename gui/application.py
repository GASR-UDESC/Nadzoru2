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

    def _create_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def add_window(self, title="Nadzoru 2"):
        new_window = MainWindow(application=self, title=title)
        return new_window

    # def rm_window(self, window):

    #     for note in window.note:
    #         if note.get_tab_label_color() == vermelho:
    #             #pergunta
    #         pass
    #     windows = self.get_windows()
    #     if len(windows) == 1:
    #         self.validade_quit()
    #     else:
    #         for note in window.note:
    #             if windows[0] != window:
    #                 windows[0].append_page(note)
    #             else:
    #                 windows[1].append_page(note)
    #         window.destroy()

        # IF NOT LAST WINDOW:
            # move all tabs from window to another (different) window in the list
        # else
            # close all tabs (which should ask to save)

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
            if window.close_tabs() == False:
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



