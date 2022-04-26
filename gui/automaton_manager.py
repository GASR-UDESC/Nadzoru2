from machine.automaton import Automaton
from gui.automaton_editor import AutomatonEditor
from gui.base import PageMixin
from gi.repository import GLib, Gio, Gtk


class AutomatonManager(PageMixin, Gtk.Box):
    def __init__(self, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.connect('parent-set', self.on_parent_set)
        self.automatonlist = list()

        self.paned = Gtk.Paned()
        self.pack_start(self.paned, True, True, 0)

        self.build_sidebox()
        self.build_treeview()

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(self.treeview)
        self.paned.pack1(self.scrolled, True, True)
        self.paned.pack2(self.sidebox, False, False)

    def on_parent_set(self, widget, oldparent):
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:
            app = widget.get_application()
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()
            self.update_treeview()

    def build_sidebox(self):
        self.sidebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)

        def _add_btn_to_sidebox(btn_label, callback, padding=5):
            btn = Gtk.Button(label=btn_label)
            btn.connect('clicked', callback)
            self.sidebox.pack_start(btn, False, False, padding)

        _add_btn_to_sidebox("Save", self.on_savebtn)
        _add_btn_to_sidebox("Clone", self.on_clonebtn)
        _add_btn_to_sidebox("Edit", self.on_editbtn)
        _add_btn_to_sidebox("Simulate", self.on_simulatebtn)
        _add_btn_to_sidebox("Close", self.on_closebtn)
        _add_btn_to_sidebox("Send to Arduino", self.on_arduinobtn)

    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        self.update_treeview()

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
        for automaton in self.automatonlist:
            rows.append([automaton.get_name(), automaton])

        rows.sort(key=lambda row: row[0])

        for row in rows:
            self.liststore.append(row)

    def edit_treeview_text(self, cell, path, new_text):
        automaton = self.liststore[path][1]
        if automaton.get_file_path_name() is None:  # Should this change the name of a automaton when it has a file_path_name?
            automaton.set_name(new_text)
            for tab_id, window in self.get_application().is_automaton_open_anytype(automaton):
                tab = window.note.get_nth_page(tab_id)
                window.set_tab_page_title(tab, automaton.get_name())
        self.get_application().emit('nadzoru-automatonlist-change', self.automatonlist)
        self.update_treeview()

    def _get_tree_selection(self):
        selected_automatons = list()
        _, tree_path_list = self.treeview_selection.get_selected_rows()

        for tree_path in tree_path_list:
            tree_iter = self.liststore.get_iter(tree_path)
            selected = self.liststore.get(tree_iter, 1)[0]
            selected_automatons.append(selected)
        return selected_automatons

    def on_savebtn(self, widget):
        for automaton in self._get_tree_selection():
            file_path_name = automaton.get_file_path_name()
            if file_path_name is None:
                file_path_name = self._save_dialog(automaton)
            # Note that file_path_name can be None, the dialog opens and the user Cancels it, thus remaining None
            if file_path_name is not None:
                # automaton.save saves the file.
                # editor.save saves the file and removes has_changes_to_save status (editor is a AutomatonEditor)
                already_open = self.get_application().is_automaton_open(automaton, AutomatonEditor)
                if already_open is None:
                    automaton.save(file_path_name)
                else:
                    tab_id, window = already_open
                    editor = window.note.get_nth_page(tab_id)
                    editor.save(file_path_name)
                    window.set_tab_page_title(editor, automaton.get_name())
                    window.set_tab_label_color(editor, '#000')
        self.update_treeview()

    def _save_dialog(self, automaton):
        active_window = self.get_ancestor_window()

        dialog = Gtk.FileChooserDialog(
            "Choose file", active_window, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK),
            do_overwrite_confirmation=True)

        def _add_filefilter(name, pattern):
            filefilter = Gtk.FileFilter()
            filefilter.set_name(name)
            filefilter.add_pattern(pattern)
            return filefilter
        dialog.add_filter(_add_filefilter(".xml files", '*.xml'))
        dialog.add_filter(_add_filefilter("All files", '*'))
        dialog.set_current_name(f'{automaton.get_name()}.xml')
        result = dialog.run()

        if result == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            dialog.destroy()
            return file_path
        dialog.destroy()
        return None

    def on_editbtn(self, widget):
        active_window = self.get_ancestor_window()
        for automaton in self._get_tree_selection():
            active_window.add_tab_editor(automaton, automaton.get_name())
        self.update_treeview()

    def on_clonebtn(self, widget):
        for automaton in self._get_tree_selection():
            automaton = automaton.copy()
            automaton.clear_file_path_name(f"{automaton.get_name()} copy")
            self.get_application().add_to_automatonlist(automaton)

    def on_simulatebtn(self, widget):
        active_window = self.get_ancestor_window()
        for automaton in self._get_tree_selection():
            active_window.add_tab_simulator(automaton, f"Sim: {automaton.get_name()}")
        self.update_treeview()

    def on_closebtn(self, widget):
        for automaton in self._get_tree_selection():
            self.get_application().close_automaton(automaton)

    def on_arduinobtn(self, widget):
        pass