
from gi.repository import Gtk, GtkSource
from gui.base import PageMixin
from machine.automaton import Automaton
import machine.exceptions as expt
import re

class AutomatonScriptOperation(PageMixin, Gtk.Box):

    def __init__(self, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.automatonlist = list()
        self.automaton_tree_store = Gtk.ListStore(str)
        self.automaton_loader_panel = self.automaton_panel()
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.connect('parent-set', self.on_parent_set)
        self.loc = {
            'Sync': Automaton.synchronization,
            'SupC': Automaton.sup_c,
            'Observer': Automaton.observer,
            'Accessible': Automaton.accessible,
            'Coaccessible': Automaton.coaccessible,
            'Trim': Automaton.trim,
            'Minimize': Automaton.minimize,
            'Supervisor Reduction': Automaton.supervisor_reduction,
            'Labeller': Automaton.labeller,
            'Diagnoser': Automaton.diagnoser,
        }
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(self.paned, True, True, 0)

        self.left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.left_box.set_size_request(170, -1)
        self.operations_panel = self.operations_panel()
        self.left_box.pack_start(self.operations_panel, True, True, 0)
        self.automaton_loader_panel = self.automaton_panel()
        self.left_box.pack_start(self.automaton_loader_panel, True, True, 0)
        #self.pack_start(self.left_box, True, True, 0)
        #self.paned.add1(self.left_box)
        self.paned.pack1(self.left_box, True, False)

        self.right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.right_box.set_size_request(400, -1)
        self.script_panel = self.script_panel()
        self.right_box.pack_start(self.script_panel, True, True, 0)
        #self.pack_start(self.right_box, True, True, 0)
        #self.paned.add2(self.right_box)
        self.paned.pack2(self.right_box, True, False)

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:                       
            app = widget.get_application()          
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()
        self.update_automaton_loader_panel()

    def operations_tree_view(self, items):
        list_store = Gtk.ListStore(str)
        for item in items:
            list_store.append([item])

        tree_view = Gtk.TreeView(model=list_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Operations", renderer, text=0)
        tree_view.append_column(column)

        tree_view.connect("row-activated", self.on_operations_activated)

        return tree_view
    
    def on_operations_activated(self, tree_view, path, column):
        model = tree_view.get_model()
        iter_ = model.get_iter(path)
        operation_name = model.get_value(iter_, 0)
        
        text_buffer = self.command_entry.get_buffer()
        insert_mark = text_buffer.get_insert()
        cursor_iter = text_buffer.get_iter_at_mark(insert_mark)

        operation_text = f"{operation_name}()"
        text_buffer.insert(cursor_iter, operation_text)

        position = cursor_iter.get_offset() - 1
        cursor_iter = text_buffer.get_iter_at_offset(position)
        text_buffer.place_cursor(cursor_iter)
        
        self.command_entry.grab_focus()

    def operations_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        operations_tree_view = self.operations_tree_view(list(self.loc.keys()))
        operations_scrolled_window = Gtk.ScrolledWindow()
        operations_scrolled_window.set_min_content_height(200)
        operations_scrolled_window.add(operations_tree_view)
        panel.pack_start(operations_scrolled_window, True, True, 0)
        return panel
    
    def automaton_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        automaton_view = Gtk.TreeView(model=self.automaton_tree_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Automatons", renderer, text=0)
        automaton_view.append_column(column)
        automaton_view.connect("row-activated", self.on_automaton_activated)
        automaton_scrolled_window = Gtk.ScrolledWindow()
        automaton_scrolled_window.set_min_content_height(200)
        automaton_scrolled_window.add(automaton_view)
        panel.pack_start(automaton_scrolled_window, True, True, 0)
        return panel
    
    def update_automaton_loader_panel(self):
        self.automaton_tree_store.clear()
        for automaton in self.automatonlist:
            self.automaton_tree_store.append([automaton.get_id_name()])
    
    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        self.update_automaton_loader_panel() 

    def on_automaton_activated(self, tree_view, path, column):
        model = tree_view.get_model()
        iter_ = model.get_iter(path)
        automaton_name = model.get_value(iter_, 0)
        
        text_buffer = self.command_entry.get_buffer()
        insert_mark = text_buffer.get_insert()
        cursor_iter = text_buffer.get_iter_at_mark(insert_mark)

        text_buffer.insert(cursor_iter, automaton_name)  

        cursor_iter = text_buffer.get_iter_at_mark(insert_mark)
        text_buffer.place_cursor(cursor_iter)
        self.command_entry.grab_focus()

    def script_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.command_entry = GtkSource.View()
        self.command_entry.set_show_line_numbers(True)

        command_entry_scrolled = Gtk.ScrolledWindow()
        command_entry_scrolled.add(self.command_entry)
        panel.pack_start(command_entry_scrolled, True, True, 0)

        self.open_result_checkbutton = Gtk.CheckButton(label="Open Result")
        panel.pack_start(self.open_result_checkbutton, False, False, 0)

        execute_button = Gtk.Button(label="EXECUTE")
        execute_button.connect("clicked", self.on_exec_btn)
        panel.pack_start(execute_button, False, False, 0)

        open_button = Gtk.Button(label="OPEN SCRIPT")
        open_button.connect("clicked", self.on_open_btn)
        panel.pack_start(open_button, False, False, 0)

        save_button = Gtk.Button(label="SAVE SCRIPT")
        save_button.connect("clicked", self.on_save_btn)
        panel.pack_start(save_button, False, False, 0)

        return panel

    def push_msg_statusbar(self, message):
        win = self.get_ancestor_window()
        win.statusbar.push(message)
    
    def on_exec_btn(self, button):
        buffer = self.command_entry.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        command_input = buffer.get_text(start_iter, end_iter, True)
        self.execute_script(command_input) 

    def execute_script(self, script):
        loc = dict(self.loc)  # copy of self.loc, as local loc will be updated

        for automaton in self.automatonlist:
            automaton_id = automaton.get_id_name()
            loc[automaton_id] = automaton

        try:
            exec(script, {}, loc)
            window = self.get_ancestor_window()
            for name, automaton in loc.items():
                if isinstance(automaton, Automaton) and automaton not in self.automatonlist:
                    automaton.set_name(name)
                    automaton.set_file_path_name(f"{name}.xml")
                    automaton.arrange_states_position()
                    automaton.save()
                    self.automatonlist.append(automaton)  #  adding obj to app.elements
                    if window is not None and self.open_result_checkbutton.get_active():
                        window.add_tab_editor(automaton, automaton.get_name()) 
                        window.set_tab_label_color(window.get_current_tab_widget(), 'label-red') 
            self.update_automaton_loader_panel()
            
        except expt.NadzoruError as e: #TODO: statusbar error
            self.push_msg_statusbar(str(e))

    def on_open_btn(self, button):
        buffer = self.command_entry.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        command_input = buffer.get_text(start_iter, end_iter, True)
        
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            parent=self.get_ancestor_window(),
            action=Gtk.FileChooserAction.OPEN,
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
        )

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_pattern("*.txt")
        dialog.add_filter(filter_text)
        
        filter_any = Gtk.FileFilter()
        filter_any.set_name("All files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            with open(filename, 'r') as file:
                command_input = file.read()
                buffer = self.command_entry.get_buffer()
                buffer.set_text(command_input)

        dialog.destroy()

    def on_save_btn(self, button):
        buffer = self.command_entry.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        command_input = buffer.get_text(start_iter, end_iter, True)
        
        dialog = Gtk.FileChooserDialog(
            title="Save File",
            parent=self.get_ancestor_window(),
            action=Gtk.FileChooserAction.SAVE,
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
        )

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_pattern("*.txt")
        dialog.add_filter(filter_text)
        
        filter_any = Gtk.FileFilter()
        filter_any.set_name("All files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        dialog.set_current_name("script.txt")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            with open(filename, 'w') as file:
                file.write(command_input)

        dialog.destroy()