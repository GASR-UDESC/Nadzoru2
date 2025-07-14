#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk

#~ cur_path = os.path.realpath(__file__)
#~ base_path = os.path.dirname(os.path.dirname(cur_path))
#~ sys.path.insert(1, base_path)

#~ import pluggins
#~ from machine.automaton import Automaton

#~ import gui
from renderer import AutomatonRenderer
from gui.base import PageMixin


class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, transition):
        super(Gtk.ListBoxRow, self).__init__()
        self.transition = transition
        self.add(Gtk.Label(label=transition.event.name, xalign=0))

def listbox_sort_func(row_1, row_2, data, notify_destroy):
        return row_1.transition.event.name.lower() > row_2.transition.event.name.lower()


class DialogSimulator(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Simulate", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Simulate", Gtk.ResponseType.OK
        )
        self.set_default_size(300, 5)
        self.set_border_width(5)
        self.connect('response', self._on_response)
        self.parent = parent
        self.result = list()
        box = self.get_content_area()
        label = Gtk.Label(label="Choose a automaton to simulate")
        box.add(label)

        treeview = self._build_treeview()
        box.pack_start(treeview, True, True, 5)

        self.show_all()

    def get_result(self):
        return self.result

    def _build_treeview(self):
        self.liststore = Gtk.ListStore(str, object)
        treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)
        self.treeview_selection = treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Automatons", cell, text=0)
        treeview.append_column(column)

        self.liststore.clear()
        rows = list()
        for automaton in self.parent.get_application().get_automatonlist():
            rows.append([automaton.get_name(), automaton])
        rows.sort(key=lambda row: row[0])
        for row in rows:
            self.liststore.append(row)

        return treeview

    def _get_tree_selection(self):
        selected_automatons = list()
        _, tree_path_list = self.treeview_selection.get_selected_rows()

        for tree_path in tree_path_list:
            tree_iter = self.liststore.get_iter(tree_path)
            selected = self.liststore.get(tree_iter, 1)[0]
            selected_automatons.append(selected)
        return selected_automatons

    def _on_response(self, dialog, response_id):
        self.result = self._get_tree_selection()


class AutomatonSimulator(PageMixin, Gtk.Box):
    def __init__(self, automaton, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.automaton = automaton
        self.current_state = automaton.initial_state
        self.forward_depth = 1
        self.backward_depth = 0
        self.build()

    def build(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('gui/ui/simulator.glade')

        # TODO: remove the use of glade
        self.box = self.builder.get_object('toplevel_box')  # TODO: remove (not need for a box inside a box
        self.viewport = self.builder.get_object('viewport')
        self.listbox = self.builder.get_object('event_listbox')
        self.backward_depth_spin = self.builder.get_object('backward_depth_spin')
        self.forward_depth_spin = self.builder.get_object('forward_depth_spin')
        self.renderer = AutomatonRenderer(self.automaton)

        self.listbox.set_sort_func(listbox_sort_func, None, False)

        self.pack_start(self.box, True, True, 0)
        self.viewport.add(self.renderer)
        self.viewport.connect("size-allocate", self.on_viewport_resize)

        self.renderer.connect("draw", self.on_draw)
        self.listbox.connect("row-activated", self.on_row_activated)
        self.forward_depth_spin.connect("value-changed", self.spin_event)
        self.backward_depth_spin.connect("value-changed", self.spin_event)
        self.builder.connect_signals(self)
        self.reset_list_box()

    def list_box_clear(self):
        for row in self.listbox.get_children():
            self.listbox.remove(row)

    def reset_list_box(self):
        if self.current_state is not None:
            for transition in self.current_state.out_transitions:
                self.listbox.add(ListBoxRowWithData(transition))
            self.listbox.show_all()
            self.renderer.queue_draw()

    def on_row_activated(self, listbox, row):
        self.current_state = row.transition.to_state
        self.list_box_clear()
        self.reset_list_box()

    def on_draw(self, wid, cr):
        self.renderer.draw_partial(cr, highlight_state=self.current_state, forward_deep=self.forward_depth, backward_deep=self.backward_depth)

    def on_viewport_resize(self, widget, allocation):
        self.renderer.renderer_set_size_request(allocation)

    def spin_event(self, event):
        self.forward_depth = self.forward_depth_spin.get_value_as_int()
        self.backward_depth = self.backward_depth_spin.get_value_as_int()
        self.renderer.queue_draw()