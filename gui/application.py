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

    # def rm_window(self, window):
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
        for window in self.get_windows():
            window.show_all()
            window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        self.activate()
        return

    def validade_quit(self):
        # TODO: For each file not save ask: cancel, discard, save. If no file just quit!
        dialog = Gtk.Dialog("Nadzoru 2", self.get_windows()[0])
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_DISCARD, Gtk.ResponseType.YES, Gtk.STOCK_SAVE, Gtk.ResponseType.APPLY)
        dialog.set_default_size(150, 100)

        label = Gtk.Label()
        #label.set_text("File {} not saved!")
        label.set_text("Do you really want to exit? All work will be lost")
        label.set_justify(Gtk.Justification.LEFT)

        box_dialog = dialog.get_content_area()
        box_dialog.add(label)
        box_dialog.show_all()

        result = dialog.run()
        dialog.destroy()

        if result == Gtk.ResponseType.YES or result == Gtk.ResponseType.APPLY:
            if len(self.elements) ==1:
                self.quit()
            else:
                return False
        return True


    def on_quit(self, action, param):
        self.validade_quit()

    def on_new_window(self, action, param):
        window = self.add_window()
        window.show_all()
        window.present()

    def on_editor_change(self, editor, *args):
        window = editor.get_ancestor_window()
        window.set_tab_label_color(editor, '#F00')



