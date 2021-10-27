import sys
import gi
import os
from gi.repository import Gdk, Gio, Gtk

from machine.automaton import Automaton
from gui.automaton_editor import AutomatonEditor
from gui.automaton_simulator import AutomatonSimulator
from gui.main_window import MainWindow

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.nadzoru2.application", **kwargs)
        self.window = None
        self.elements = list()

    def create_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.create_action('new-automaton', self.on_new_automaton)
        self.create_action('load-automaton', self.on_load_automaton)
        self.create_action('save-automaton', self.on_save_automaton)
        self.create_action('edit-automaton', self.on_edit_automaton)
        self.create_action('simulate-automaton', self.on_simulate_automaton)
        self.create_action('import-ides', self.on_import_ides)       
        self.create_action('close-tab', self.on_close_tab)
        self.create_action('quit', self.on_quit)
        self.create_action('export-ides', self.on_export_ides)

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

    def validade_quit(self):
        # TODO: For each file not save ask: cancel, discard, save. If no file just quit!
        dialog = Gtk.Dialog("Nazoru2", self.window)
        dialog.modify_style
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
            self.quit()

    def on_new_automaton(self, action, param):
        from test_automata import automata_01  # For testing
        automaton = Automaton()
        automata_01(automaton)  # For testing
        self.elements.append(automaton)
        editor = AutomatonEditor(automaton, self)
        self.window.add_tab(editor, "[new] *")

    def on_load_automaton(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self.window, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for full_path_name in dialog.get_filenames():
                file_name = os.path.basename(full_path_name)
                automaton = Automaton()
                automaton.load(full_path_name)
                self.elements.append(automaton)
                if result == Gtk.ResponseType.OK:
                    editor = AutomatonEditor(automaton, self)
                    self.window.add_tab(editor, "{} *".format(file_name))
        dialog.destroy()

    def on_save_automaton(self, action, param):
        print("You saved the automata")

    def on_edit_automaton(self, action, param):
        print("You opened in editor automata")

    def on_simulate_automaton(self, action, param):
        # TODO: open dialog to select from self.elements
        from test_automata import automata_01  # For testing
        automaton = Automaton()
        automata_01(automaton)  # For testing
        simulator = AutomatonSimulator(automaton)
        self.window.add_tab(simulator, "Simulator")

    def on_close_tab(self, action, param):
        self.window.remove_tab(self.window.note.get_current_page())

    def on_import_ides(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self.window, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for full_path_name in dialog.get_filenames():
                file_name = os.path.basename(full_path_name)
                automaton = Automaton()
                automaton.ides_import(full_path_name)
                self.elements.append(automaton)
                if result == Gtk.ResponseType.OK:
                    editor = AutomatonEditor(automaton, self)
                    self.window.add_tab(editor, "{} *".format(file_name))
        dialog.destroy()
        
    def on_export_ides(self, action, default_filename=None):
        dialog = Gtk.FileChooserDialog("Choose Path", self.window, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Export", Gtk.ResponseType.ACCEPT))
        dialog.resize(700, 500)
        if default_filename:
            dialog.set_filename(os.path.abspath(default_filename))
        filename = None
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        dialog.destroy()
        return filename
        
    def on_quit(self, action, param):
        self.validade_quit()



