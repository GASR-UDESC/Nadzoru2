import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from gui.base import PageMixin
from gui.automaton_editor import AutomatonEditor
from gui.automaton_simulator import AutomatonSimulator
from machine.automaton import Automaton
#from gui.property_box import PropertyBox

class AutomatonManager(PageMixin, Gtk.Box):
    def __init__(self, application, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.automaton_list = application.get_automatonlist()
        self.application = application
        self.application.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.paned = Gtk.Paned()
        self.pack_start(self.paned, True, True, 0)

        self.build_sidebox()
        self.build_treeview()

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(self.treeview)
        self.paned.pack1(self.scrolled, True, True)
        self.paned.pack2(self.sidebox, False, False)
        
    def build_sidebox(self):
        self.sidebox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
        padding = 5

        savebtn = Gtk.Button(label="Save")
        savebtn.connect('clicked', self.on_savebtn)
        self.sidebox.pack_start(savebtn, False, False, padding)

        editbtn = Gtk.Button(label="Edit")
        editbtn.connect('clicked', self.on_editbtn)
        self.sidebox.pack_start(editbtn, False, False, padding)

        simulatebtn = Gtk.Button(label="Simulate")
        simulatebtn.connect('clicked', self.on_simulatebtn)
        self.sidebox.pack_start(simulatebtn, False, False, padding)

        closebtn = Gtk.Button(label="Close")
        closebtn.connect('clicked', self.on_closebtn)
        self.sidebox.pack_start(closebtn, False, False, padding)

    def on_automatonlist_change(self, widget, automaton_list):
        self.update_treeview()
        self.automaton_list = automaton_list

    def build_treeview(self):
        self.liststore = Gtk.ListStore(str, object)
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview_selection = self.treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        cell = Gtk.CellRendererText()
        cell.set_property('editable', True)
        cell.connect('edited', self.edit_treeview_text)
        column = Gtk.TreeViewColumn("Open Automatons", cell, text=0)
        self.treeview.append_column(column)
        
        self.update_treeview()

    def update_treeview(self):
        self.liststore.clear()
        rows = list()
        for automaton in self.automaton_list:
            rows.append([automaton.get_name(), automaton])

        rows.sort(key=lambda row: row[0])

        for row in rows:
            self.liststore.append(row)

        # rows = list() # to check what happend with too many automatons
        # for i in range(60):
        #     self.liststore.append(['row'+str(i), i])

    def edit_treeview_text(self, cell, path, new_text):
        automaton = self.liststore[path][1]
        if automaton.get_file_path_name() is None: # Should this change the name of a automaton when it has a file_path_name?
            automaton.set_name(new_text)
            for tab_id, window in self.application.is_automaton_open(automaton):
                tab = window.note.get_nth_page(tab_id)
                window.set_tab_page_title(tab, automaton.get_name())
        self.application.emit('nadzoru-automatonlist-change', self.automaton_list)
        self.update_treeview()

    def on_savebtn(self, widget):
        for automaton in self._get_tree_selection():
            self._save_dialog(automaton)
        self.update_treeview()

    def _save_dialog(self, automaton):
        active_window = self.get_ancestor_window()
        
        dialog = Gtk.FileChooserDialog("Choose file", active_window, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK), do_overwrite_confirmation=True)

        result = dialog.run()
        if result ==  Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            dialog.destroy()
            if not(file_path.lower().endswith('.xml')):
                file_path = f'{file_path}.xml'

            # automaton.save saves the file.
            # editor.save saves the file and removes has_changes_to_save status (editor is a AutomatonEditor)

            if not self.application.is_automaton_open(automaton, AutomatonEditor):
                automaton.save(file_path)

            is_saved = False 
            for tab_id, window in self.application.is_automaton_open(automaton, AutomatonEditor): # estranho
                editor = window.note.get_nth_page(tab_id)
                if not is_saved:
                    editor.save(file_path)
                is_saved = True
                window.set_tab_page_title(editor, automaton.get_name())
                window.set_tab_label_color(editor, '#000')


    def on_editbtn(self, widget):
        # If there is already a AutomatonEditor with the selected automaton, a copy will be created
        active_window = self.get_ancestor_window() 
        for automaton in self._get_tree_selection():  
            if not self.application.is_automaton_open(automaton, AutomatonEditor):
                active_window.add_tab_editor(automaton, automaton.get_name())
            else:
                automaton = automaton.copy()
                automaton.clear_file_path_name(automaton.get_name()+ " copy")
                self.application.add_to_automatonlist(automaton)
                active_window.add_tab_editor(automaton, automaton.get_name())
        self.update_treeview()

    def on_simulatebtn(self, widget):

        active_window = self.get_ancestor_window()
        for automaton in self._get_tree_selection():
            active_window.add_tab_simulator(automaton, "Simu: %s" %automaton.get_name())
            # if not self.application.is_automaton_open(automaton, AutomatonSimulator): # Probably OK to have more than 1 simulator instance

        self.update_treeview()

    def on_closebtn(self, widget):
        for automaton in self._get_tree_selection():
            self.application.close_automaton(automaton)

    def _get_tree_selection(self):
        selected_automatons = list()
        _, tree_path_list = self.treeview_selection.get_selected_rows()

        for tree_path in tree_path_list:
            tree_iter = self.liststore.get_iter(tree_path)
            selected = self.liststore.get(tree_iter, 1)[0]
            selected_automatons.append(selected)
        return selected_automatons

