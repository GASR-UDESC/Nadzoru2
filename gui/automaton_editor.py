#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk, GObject

from renderer import AutomatonRenderer
from gui.base import PageMixin


class AutomatonEditor(PageMixin, Gtk.Box):
    def __init__(self, automaton, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.automaton = automaton
        self.selected_state = None
        self.selected_transitions = None
        self.tool_change_handler_id = None

        self.paned = Gtk.Paned(wide_handle=True)
        self.scrolled = Gtk.ScrolledWindow.new()
        self.automaton_render = AutomatonRenderer(self.automaton)

        self.pack_start(self.paned, True, True, 0)
        self.paned.pack1(self.scrolled, True, False)
        self.scrolled.add(self.automaton_render)

        self.build_treeview()

        self.automaton_render.connect("draw", self.on_draw)
        self.automaton_render.connect("motion-notify-event", self.on_motion_notify)
        self.automaton_render.connect("button-press-event", self.on_button_press)
        # self.automaton_render.connect("button-release-event", self.on_button_release)

    def build_treeview(self):
        self.liststore = Gtk.ListStore(str, bool, bool, object)

        self.treeview_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview_selection  = self.treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)

        column_editabletext = Gtk.TreeViewColumn("Event", renderer_editabletext, text=0)
        self.treeview.append_column(column_editabletext)

        renderer_editabletext.connect("edited", self.text_edited)

        # Toggle 1
        renderer_toggle_1 = Gtk.CellRendererToggle()
        renderer_toggle_1.connect("toggled", self.renderer_toggle_controllable)
        column_toggle_1 = Gtk.TreeViewColumn("Controllable", renderer_toggle_1, active=1)
        self.treeview.append_column(column_toggle_1)

        # Toggle 2
        renderer_toggle_2 = Gtk.CellRendererToggle()
        renderer_toggle_2.connect("toggled", self.renderer_toggle_observable)
        column_toggle_2 = Gtk.TreeViewColumn("Observable", renderer_toggle_2, active=2)
        self.treeview.append_column(column_toggle_2)

        self.treeview_box.pack_start(self.treeview, True, True, 0)

        #Add and Delete Cell buttons

        self.add_button = Gtk.Button(label = 'Add Event')
        self.add_button.connect("clicked", self.event_add)
        self.treeview_box.pack_start(self.add_button, False, False, 0)

        self.delete_button = Gtk.Button(label = 'Remove Event')
        self.delete_button.connect("clicked", self.event_remove)
        self.treeview_box.pack_start(self.delete_button, False, False, 0)
        self.paned.pack2(self.treeview_box, False, False)

        self.update_treeview()

    def update_treeview(self):
        self.liststore.clear()
        rows = list()

        for event in self.automaton.events:
            rows.append([event.name, event.controllable, event.observable, event])

        rows.sort(key=lambda row: row[0])

        for row in rows:
            self.liststore.append(row)

    def text_edited(self, widget, path, event_name):
        event = self.liststore[path][3]
        self.automaton.event_rename(event, event_name)
        self.update_treeview()
        self.trigger_change()

    def renderer_toggle_controllable(self, widget, path):
        event = self.liststore[path][3]
        event.controllable = not event.controllable
        self.update_treeview()
        self.trigger_change()

    def renderer_toggle_observable(self, widget, path):
        event = self.liststore[path][3]
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
            event = self.liststore.get(tree_iter, 3)[0]
            self.automaton.event_remove(event)
        self.update_treeview()
        self.automaton_render.queue_draw()
        self.trigger_change()

    def save(self, file_path_name):
        status = self.automaton.save(file_path_name)
        if status == True:
            self.__changes_to_save = False
        return status

    def trigger_change(self):
        self.emit('nadzoru-editor-change', None)
        self.__changes_to_save = True

    def reset_selection(self):
        self.selected_state = None
        self.selected_transitions = None
        self.automaton_render.queue_draw()

    def on_draw(self, automaton_render, cr):
        self.automaton_render.draw(cr, highlight_state=self.selected_state, highlight_transitions=self.selected_transitions)

    def on_motion_notify(self, automaton_render, event):
        window = self.get_ancestor_window()
        x, y = event.get_coords()
        tool_name = window.toolpallet.get_selected_tool()

        if tool_name == 'move':
            if not self.selected_state is None:
                self.selected_state.x = x
                self.selected_state.y = y
                self.automaton_render.queue_draw()
                self.trigger_change()

    def on_button_press(self, automaton_render, event):
        window = self.get_ancestor_window()
        x, y = event.get_coords()
        tool_name = window.toolpallet.get_selected_tool()
        state = self.automaton_render.get_state_at(x, y)

        if tool_name == 'state_add':
            state = self.automaton.state_add(None, x=x, y=y)
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
                        selected_event = self.liststore.get(tree_iter, 3)[0]
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
        self.automaton_render.queue_draw()


GObject.signal_new('nadzoru-editor-change', AutomatonEditor, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,))
