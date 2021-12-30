import sys
import gi
import os
from gi.repository import Gdk, Gio, Gtk

from gui.main_window import MainWindow

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class Application(Gtk.Application):
    def __init__(self, *args, startup_callback=None, **kwargs):
        super().__init__(*args, application_id="org.nadzoru2.application", **kwargs)
        self.elements = list()
        self.startup_callback = startup_callback

    def _create_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
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
        for window in self.get_windows():
            window.show_all()
            window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        self.activate()
        return

    def validade_quit(self):
        pass
        # TODO: This must no be used from MainWindow.do_delete_event. This is only the main app quit!
            # For each window build a dialog
                # For each tab (page) of the windows that is NOT saved (use PageMixin methods to query if saved) add to a list of things to be saved
                    # ask: cancel, discard, save with the text of the list to be saved (label of the tab?)

    def on_quit(self, action, param):
        pass
        # for window in self.get_windows():
        #     window.on_close_window(action, param)
        

    def on_new_window(self, action, param):
        window = self.add_window()
        window.show_all()
        window.present()

    def on_editor_change(self, editor, *args):
        window = editor.get_ancestor_window()
        window.set_tab_label_color(editor, '#F00')



