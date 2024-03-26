
from gi.repository import Gtk
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
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.connect('parent-set', self.on_parent_set)
        self.automaton_loader_panel = self.automaton_panel()
        self.pack_start(self.automaton_loader_panel, True, True, 0)
        self.script_panel = self.script_panel()
        self.pack_start(self.script_panel, True, True, 0)

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:                       
            app = widget.get_application()          
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()

    def automaton_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.automaton_list_box = Gtk.ListBox()
        panel.pack_start(self.automaton_list_box, True, True, 0)
        return panel
    
    def update_automaton_loader_panel(self):
        for child in self.automaton_list_box.get_children():
            self.automaton_list_box.remove(child)

        for automaton in self.automatonlist:
            label = Gtk.Label(label=automaton.get_name())
            self.automaton_list_box.add(label)

        self.automaton_list_box.show_all()
    
    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        self.update_automaton_loader_panel()  

    def script_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.command_entry = Gtk.TextView()
        command_entry_scrolled = Gtk.ScrolledWindow()
        command_entry_scrolled.add(self.command_entry)
        panel.pack_start(command_entry_scrolled, True, True, 0)

        self.result_name_entry = Gtk.Entry()
        self.result_name_entry.set_placeholder_text("Result")
        panel.pack_start(self.result_name_entry, False, False, 0)

        self.open_result_checkbutton = Gtk.CheckButton(label="Open Result")
        panel.pack_start(self.open_result_checkbutton, False, False, 0)

        execute_button = Gtk.Button(label="EXECUTE")
        execute_button.connect("clicked", self.on_exec_btn)
        panel.pack_start(execute_button, False, False, 0)

        return panel

    def push_msg_statusbar(self, message):
        win = self.get_ancestor_window()
        win.statusbar.push(message)
    
    def on_exec_btn(self, button):
        buffer = self.command_entry.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        command_input = buffer.get_text(start_iter, end_iter, True)

        result = self.execute_script(command_input)
        if result:
            self.handle_new_automaton(result)

    def handle_new_automaton(self, automaton):
        user_defined_name = self.result_name_entry.get_text().strip()
        if not user_defined_name:
            user_defined_name = f"automaton_{len(self.automatonlist) + 1}"
        automaton.set_name(user_defined_name)
        automaton.set_file_path_name(f"{user_defined_name}.xml")
        automaton.save()
        
        self.automatonlist.append(automaton)
        self.update_automaton_loader_panel()

        if self.open_result_checkbutton.get_active():
            window = self.get_ancestor_window()
            if window is not None:
                window.add_tab_editor(automaton, automaton.get_name()) 
                window.set_tab_label_color(window.get_current_tab_widget(), 'label-red') 

    def execute_script(self, script):
        loc = {
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

        for automaton in self.automatonlist:
            automaton_id = automaton.get_id_name()
            loc[automaton_id] = automaton

        new_automaton = None

        try:
            exec(script, {}, loc)
            for key, value in loc.items():
                if isinstance(value, Automaton) and value not in self.automatonlist:
                    new_automaton = value 
                    break 
            return new_automaton
            
        except expt.NadzoruError as e:
            self.push_msg_statusbar(str(e))
            return None
