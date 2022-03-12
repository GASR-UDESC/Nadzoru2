import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from gui.base import PageMixin
from gui.automaton_editor import AutomatonEditor
from machine.automaton import Automaton
#from gui.property_box import PropertyBox

class AutomatonManager(PageMixin, Gtk.Box):
    def __init__(self, automaton_list, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.automaton_list = automaton_list
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

    def build_treeview(self):
        self.liststore = Gtk.ListStore(str, object)
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview_selection = self.treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        cell = Gtk.CellRendererText()
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
            app = active_window.get_application()
            file_path = dialog.get_filename()
            dialog.destroy()
            if not(file_path.lower().endswith('.xml')):
                file_path = f'{file_path}.xml'

            is_saved = False 
            for tab_id, window in app.is_automaton_open(automaton, AutomatonEditor): # estranho
                if not is_saved:
                    tab = window.note.get_nth_page(tab_id)
                    tab.save(file_path)
                is_saved = True
                window.set_tab_page_title(tab, automaton.get_file_name())
                window.set_tab_label_color(tab, '#000')
            if not is_saved:
                automaton.save(file_path)

    def on_editbtn(self, widget):
        window = self.get_ancestor_window()
        for automaton in self._get_tree_selection():
            window.add_tab_editor(automaton, automaton.get_name())
        self.update_treeview()

    def on_simulatebtn(self, widget):
        app = self.get_ancestor_window().get_application()
        self.update_treeview()
        #app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
        #print("Sim", self._get_tree_selection().get_name())

    def on_closebtn(self, widget):
        app = self.get_ancestor_window().get_application()
        for automaton in self._get_tree_selection():
            for tab_id, window in app.is_automaton_open(automaton):
                if window.remove_tab(tab_id):
                    app.remove_from_automatonlist(automaton)
        self.update_treeview()

    def _get_tree_selection(self):
        selected_automatons = list()
        _, tree_path_list = self.treeview_selection.get_selected_rows()

        for tree_path in tree_path_list:
            tree_iter = self.liststore.get_iter(tree_path)
            selected = self.liststore.get(tree_iter, 1)[0]
            selected_automatons.append(selected)
        return selected_automatons

