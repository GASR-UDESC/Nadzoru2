#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk, GObject

from renderer import AutomatonRenderer
from gui.base import PageMixin
from gui.property_box import PropertyBox
import machine.exceptions as expt

from renderer import AutomatonRendererPublic

class AutomatonEditor(PageMixin, Gtk.Box):
    def __init__(self, automaton, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.connect('parent-set', self.on_parent_set)

        self.automaton = automaton
        self.selected_state = None
        self.selected_transitions = None
        self.tool_change_handler_id = None

        self.paned = Gtk.Paned(wide_handle=True)
        self.scrolled = Gtk.ScrolledWindow.new()
        self.automaton_render = AutomatonRenderer(self.automaton)
        self.sidebox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.frame_props = Gtk.Frame(label="Properties", visible=False, no_show_all=True)

        self.propbox = PropertyBox()

        self.pack_start(self.paned, True, True, 0)
        self.paned.pack1(self.scrolled, True, False)
        self.paned.pack2(self.sidebox, False, False)
        self.scrolled.add(self.automaton_render)
        self.automaton_render.renderer_set_size_request(self.scrolled.get_allocation())

        self.build_treeview()
        self.sidebox.pack_start(self.frame_props, False, False, 0)
        self.frame_props.add(self.propbox)

        self.automaton_render.connect('draw', self.on_draw)
        self.automaton_render.connect('motion-notify-event', self.on_motion_notify)
        self.automaton_render.connect('button-press-event', self.on_button_press)
        self.automaton_render.connect("button-release-event", self.on_button_release)
        self.propbox.connect('nadzoru-property-change', self.prop_edited)

        self.index_object = 3

    def build_treeview_create_liststore(self):
        return Gtk.ListStore(str, bool, bool, object)
    
    def add_extra_toggles(self): # By default, do nothing. Overwrite this function in the extensions to add more toggles.
        pass

    def build_treeview(self):
        self.liststore = self.build_treeview_create_liststore()

        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview_selection  = self.treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.treeview.set_enable_search(False)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property('editable', True)
        renderer_editabletext.connect('edited', self.text_edited)

        column_editabletext = Gtk.TreeViewColumn("Event", renderer_editabletext, text=0)
        self.treeview.append_column(column_editabletext)

        # Toggle 1
        renderer_toggle_1 = Gtk.CellRendererToggle()
        renderer_toggle_1.connect('toggled', self.renderer_toggle_controllable)
        column_toggle_1 = Gtk.TreeViewColumn('Controllable', renderer_toggle_1, active=1)
        self.treeview.append_column(column_toggle_1)

        # Toggle 2
        renderer_toggle_2 = Gtk.CellRendererToggle()
        renderer_toggle_2.connect('toggled', self.renderer_toggle_observable)
        column_toggle_2 = Gtk.TreeViewColumn("Observable", renderer_toggle_2, active=2)
        self.treeview.append_column(column_toggle_2)

        self.add_extra_toggles()

        self.sidebox.pack_start(self.treeview, True, True, 0)

        # Add and Delete Cell buttons
        self.add_button = Gtk.Button(label = "Add Event")
        self.add_button.connect('clicked', self.event_add)
        self.sidebox.pack_start(self.add_button, False, False, 0)

        self.delete_button = Gtk.Button(label = "Remove Event")
        self.delete_button.connect('clicked', self.event_remove)
        self.sidebox.pack_start(self.delete_button, False, False, 0)
        
        self.validate_button = Gtk.Button(label = "Validate Events")
        self.validate_button.connect('clicked', self.validate_events)
        self.sidebox.pack_start(self.validate_button, False, False, 0)

        self.update_treeview()

    def validate_events(self, widget):
        print(self.automaton.name_validation())
        if self.automaton.name_validation():
            raise expt.InvalidEventNameError

    def update_treeview_add_events(self, rows):
        for event in self.automaton.events:
            rows.append([event.name, event.controllable, event.observable, event])
        return rows

    def update_treeview(self):
        cursor_path, cursor_focus_column = self.treeview.get_cursor()

        self.liststore.clear()
        rows = list()

        rows = self.update_treeview_add_events(rows)

        rows.sort(key=lambda row: row[0])

        for row in rows:
            self.liststore.append(row)
        
        if cursor_path:
            self.treeview.set_cursor(cursor_path, cursor_focus_column, False)
        

    def text_edited(self, widget, path, event_name):
        event = self.liststore[path][self.index_object]
        self.automaton.event_rename(event, event_name)
        self.update_treeview()
        self.trigger_change()

    def renderer_toggle_controllable(self, widget, path):
        event = self.liststore[path][self.index_object]
        event.controllable = not event.controllable
        self.update_treeview()
        self.trigger_change()

    def renderer_toggle_observable(self, widget, path):
        event = self.liststore[path][self.index_object]
        event.observable = not event.observable
        self.update_treeview()
        self.trigger_change()

    def event_add(self, widget):
        self.automaton.event_add(name="new Event")
        self.update_treeview()
        self.trigger_change()

    def event_remove(self, widget):
        _, tree_path_list = self.treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.liststore.get_iter(tree_path)
            event = self.liststore.get(tree_iter, self.index_object)[0]
            self.automaton.event_remove(event)
        self.update_treeview()
        self.automaton_render.queue_draw()
        self.trigger_change()

    def _get_selected_object(self):
        if self.selected_state is not None:
            return self.selected_state
        else:
            return None
            # return self.selected_arc

    def update_properties_box(self):
        self.frame_props.hide()
        self.propbox.clear()
        selected_object = self._get_selected_object()

        if selected_object is not None:
            for prop in selected_object.properties:
                label_text = prop['label']
                property_name = prop['property']
                value = getattr(selected_object, property_name)
                if prop['gtk_control'] == 'checkbutton':
                    self.propbox.add_checkbutton(label_text, value, property_name)
                elif prop['gtk_control'] == 'entry':
                    self.propbox.add_entry(label_text, value, property_name)
                elif prop['gtk_control'] == 'switch':
                    self.propbox.add_switch(label_text, value, property_name)
                elif prop['gtk_control'] == 'spinbutton':
                    self.propbox.add_spinbutton(label_text, value, property_name, lower=-5000, upper=5000)
            self.propbox.show_all()
            self.frame_props.show()

    def prop_edited(self, propbox, value, data):
        selected_object = self._get_selected_object()
        if selected_object is not None:
            setattr(selected_object, data, value)
            self.automaton_render.queue_draw()
            self.trigger_change()

    def save(self, file_path_name=None):
        status = self.automaton.save(file_path_name)
        if status == True:
            self._changes_to_save = False
        return status

    def has_file_path_name(self):
        return self.automaton.get_file_path_name() is not None

    def trigger_change(self):
        self._changes_to_save = True
        self.update_properties_box()
        self.automaton_render.queue_draw()
        self.emit('nadzoru-editor-change', None)

    def reset_selection(self):
        self.selected_state = None
        self.selected_transitions = None
        self.update_properties_box()
        self.automaton_render.queue_draw()

    def get_tab_name(self):
        return self.automaton.get_name()

    def on_draw(self, automaton_render, cr):
        self.automaton_render.draw(cr, highlight_state=self.selected_state, highlight_transitions=self.selected_transitions)

    def on_motion_notify(self, automaton_render, event):
        window = self.get_ancestor_window()
        x, y = event.get_coords()
        tool_name = window.toolpallet.get_selected_tool()

        if tool_name == 'move':
            if not self.selected_state is None:
                self.selected_state.x = x-automaton_render.offset_x
                self.selected_state.y = y-automaton_render.offset_y
                self.automaton_render.queue_draw()
                self.update_properties_box()
                self.trigger_change()
                self.update_scrolled_window()


    def update_scrolled_window(self):
        hadj = self.scrolled.get_hadjustment()
        vadj = self.scrolled.get_vadjustment()

        delta_x, delta_y = self.automaton_render.renderer_set_size_request(self.scrolled.get_allocation())

        hadj.set_value(hadj.get_value() + delta_x)
        vadj.set_value(vadj.get_value() + delta_y)
        self.scrolled.set_hadjustment(hadj)
        self.scrolled.set_vadjustment(vadj)


    def on_button_press(self, automaton_render, event):
        window = self.get_ancestor_window()
        x, y = event.get_coords()
        tool_name = window.toolpallet.get_selected_tool()
        state = self.automaton_render.get_state_at(x, y)

        if tool_name == 'state_add':
            state = self.automaton.state_add(None, x=x-automaton_render.offset_x, y=y-automaton_render.offset_y)
            self.selected_state = state
            self.trigger_change()
        elif tool_name == 'state_initial':
            if state is not None:
                self.automaton.initial_state = state
                self.selected_state = state
                self.trigger_change()
        elif tool_name == 'state_marked':
            if state is not None:
                state.marked = not state.marked
                self.selected_state = state
                self.trigger_change()
        elif tool_name == 'transition_add':
            if state is None:
                self.selected_state = None
            else:
                if self.selected_state is None:
                    self.selected_state = state
                else:
                    _, tree_path_list = self.treeview_selection.get_selected_rows()
                    added_transition = False
                    for tree_path in tree_path_list:
                        tree_iter = self.liststore.get_iter(tree_path)
                        selected_event = self.liststore.get(tree_iter, self.index_object)[0]
                        transition = self.automaton.transition_add(self.selected_state, state, selected_event)
                        if transition is not None:
                            added_transition = True
                    if added_transition:
                        #  only if add at least one transition, reset 'selected_state'
                        self.selected_state = None
                        self.trigger_change()
        elif tool_name == 'move':
            self.selected_state = state
        elif tool_name == 'delete':
            transitions = self.automaton_render.get_transition_at(x, y)
            if state is not None:
                self.automaton.state_remove(state)
                self.trigger_change()
            for trans in transitions:
                self.automaton.transition_remove(trans)
            self.trigger_change()
        elif tool_name == 'edit':
            transitions = self.automaton_render.get_transition_at(x, y)
            if state is not None:
                self.selected_state = state
            else:
                self.selected_state = None
            if transitions:
                self.selected_transitions = transitions
            else:
                self.selected_transitions = None

        self.update_properties_box()
        self.automaton_render.queue_draw()
    
    def on_button_release(self, automaton_render, event):
        window = self.get_ancestor_window()
        tool_name = window.toolpallet.get_selected_tool()
        
        if tool_name == 'move':
            self.update_scrolled_window()
    def on_tool_clicked(self, toolpallet, tool_id, tab):
        window = self.get_ancestor_window()
        tab = window.get_current_tab_widget()
        if tab == self and window.is_active():
            if tool_id == 'state_enum':
                self.automaton.state_rename_sequential()
                self.trigger_change()

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:
            window = self.get_ancestor_window()
            window.toolpallet.connect('nadzoru-tool-clicked', self.on_tool_clicked, window.get_current_tab_widget())


GObject.signal_new('nadzoru-editor-change', AutomatonEditor, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,))
