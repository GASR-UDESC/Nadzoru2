import sys
import gi
import os
from gi.repository import Gdk, Gio, Gtk

from machine.automaton import Automaton
from gui.automaton_editor import AutomatonEditor
from gui.automaton_simulator import AutomatonSimulator
from gui.tool_palette import ToolPalette


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.expander = Gtk.Expander(expanded=True)
        self.toolpallet = ToolPalette(width_request=148, vexpand=True)
        self.note = Gtk.Notebook(group_name='0', scrollable=True)
        self.statusbar = Gtk.Statusbar()

        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.hbox, True, True, 0)
        self.hbox.pack_start(self.expander, False, False, 0)
        self.expander.add(self.toolpallet)
        self.hbox.pack_start(self.note, True, True, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        # self.note.popup_enable()
        self.note.popup_disable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

        self.note.connect('create-window', self.nootbook_create_window)
        self.note.connect('page-removed', self.notebook_page_removed)
        self.toolpallet.connect('nadzoru-tool-change', self.on_tool_change)

        self._create_action('new-automaton', self.on_new_automaton)
        self._create_action('open-automaton', self.on_open_automaton)
        self._create_action('save-automaton', self.on_save_automaton)
        self._create_action('save-as-automaton', self.on_save_as_automaton)
        self._create_action('edit-automaton', self.on_edit_automaton)
        self._create_action('simulate-automaton', self.on_simulate_automaton)
        self._create_action('import-ides', self.on_import_ides)
        self._create_action('close-tab', self.on_close_tab)
        self._create_action('export-ides', self.on_export_ides)

        self.toolpallet.add_button('file', label="Save", icon_name='gtk-save', callback=self.on_save_automaton)
        self.toolpallet.add_button('file', label="Save", icon_name='gtk-save-as', callback=self.on_save_as_automaton)
        self.toolpallet.add_button('file', label="Open", icon_name='gtk-open', callback=self.on_open_automaton)

    def nootbook_create_window(self,notebook,widget,x,y): #is widget a automaton Editor?? is  Notebook a page??
        # handler for dropping outside of current window
        new_window = self.props.application.add_window()

        # new_window.connect('destroy', self.sub_window_destroyed, new_notebook, notebook)
        #~ new_window.set_transient_for(self)  # this creates a bug: window 'self' will always be behind new_window
        # new_window.set_destroy_with_parent(True)
        # new_window.set_size_request(1000, 1000)
        new_window.move(x, y)
        new_window.show_all()
        new_window.present()
        return new_window.note


    def notebook_page_removed(self, notebook, child, page):
        #destroy the sub window after the notebook is empty
        if notebook.get_n_pages() == 0:
            self.destroy()

    # def sub_window_destroyed (self, window, cur_notebook, dest_notebook):
        # if the sub window gets destroyed, push pages back to the main window
        # detach the notebook pages in reverse sequence to avoid index errors
        # for page_num in reversed(range(cur_notebook.get_n_pages())):
        #     widget = cur_notebook.get_nth_page(page_num)
        #     tab_label = cur_notebook.get_tab_label(widget)
        #     cur_notebook.detach_tab(widget)
        #     dest_notebook.append_page(widget, tab_label)
        #     dest_notebook.set_tab_detachable(widget, True)

    def _create_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def do_delete_event(self, event):
        # TODO: how to proper integrate with application?
        # closing window: move all tabs (or unsaved tabs) to other window
        # ... but if last window, perform the check save/discard
        return self.props.application.validade_quit()

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
        self.note.set_tab_detachable(widget, True)

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

    def _save_dialog(self, widget):
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK))
        result = dialog.run()
        if result ==  Gtk.ResponseType.OK:
            file_path = (dialog.get_filename())
            if not(file_path.lower().endswith('.xml')):
                file_path = f'{file_path}.xml'
            widget.save(file_path)
        dialog.destroy()

    def on_save_automaton(self, action, param=None):
        widget = self.get_current_tab_widget()
        if (widget is None) or type(widget) != AutomatonEditor:
            return
        automata = widget.automaton

        file_path_name = automata.get_file_path_name()
        if file_path_name == None:
            self._save_dialog(widget)
            self.set_tab_page_title(widget, automata.get_file_name())
        else:
            widget.save(file_path_name)
        self.set_tab_label_color(widget, '#000')

    def on_new_automaton(self, action, param=None):
        automaton = Automaton()
        self.props.application.elements.append(automaton)
        editor = AutomatonEditor(automaton)
        editor.connect('nadzoru-editor-change', self.props.application.on_editor_change)
        self.add_tab(editor, editor.automaton.get_file_name())

    def on_open_automaton(self, action, param=None):
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for file_path_name in dialog.get_filenames():
                file_name = os.path.basename(file_path_name)
                automaton = Automaton()
                try:
                    automaton.load(file_path_name)
                except error:
                    print("Fail to load", error)
                    dialog.destroy()
                    return
                self.props.application.elements.append(automaton)
                if result == Gtk.ResponseType.OK:
                    editor = AutomatonEditor(automaton)
                    editor.connect('nadzoru-editor-change', self.props.application.on_editor_change)
                    self.add_tab(editor, file_name)
        dialog.destroy()

    def on_save_as_automaton(self, action, param=None):
        widget = self.get_current_tab_widget()
        if (widget is None) or type(widget) != AutomatonEditor:
            return
        automata = widget.automaton
        self._save_dialog(widget)
        self.set_tab_page_title(widget, automata.get_file_name())
        self.set_tab_label_color(widget, '#000')

    def on_edit_automaton(self, action, param):
        print("You opened in editor automata", self)

    def on_simulate_automaton(self, action, param):
        # TODO: open dialog to select from self.props.application.elements
        from test_automata import automata_01  # For testing
        automaton = Automaton()
        automata_01(automaton)  # For testing
        simulator = AutomatonSimulator(automaton)
        self.add_tab(simulator, "Simulator")

    def on_close_tab(self, action, param):
        # TODO: check if needs saving
        self.remove_tab(self.note.get_current_page())

    def on_tool_change(self, toolpallet, tool_id):
        for page_num in range(self.note.get_n_pages()):
            widget = self.note.get_nth_page(page_num)
            if type(widget) == AutomatonEditor:
                widget.reset_selection()

    def on_import_ides(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for full_path_name in dialog.get_filenames():
                file_name = os.path.basename(full_path_name)
                automaton = Automaton()
                automaton.ides_import(full_path_name)
                self.props.application.elements.append(automaton)
                if result == Gtk.ResponseType.OK:
                    editor = AutomatonEditor(automaton)
                    editor.connect('nadzoru-editor-change', self.props.application.on_editor_change)
                    self.add_tab(editor, "{} *".format(file_name))
        dialog.destroy()

    def on_export_ides(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose File", self, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Export", Gtk.ResponseType.OK))
        result = dialog.run()
        if result == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            file_path = f'{file_path}.xmd'
            widget = self.get_current_tab_widget()
            if type(widget) == AutomatonEditor:
                automata = widget.automaton
                automata.ides_export(file_path)
        dialog.destroy()
