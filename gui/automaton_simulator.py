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

    def spin_event(self, event):
        self.forward_depth = self.forward_depth_spin.get_value_as_int()
        self.backward_depth = self.backward_depth_spin.get_value_as_int()
        self.renderer.queue_draw()




