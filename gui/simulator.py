import os
import sys
import gi

cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins
from machine.automaton import Automaton

import gui
from render import AutomatonRender

from gi.repository import Gtk, Gdk

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, transition):
        super(Gtk.ListBoxRow, self).__init__()
        self.transition = transition
        self.add(Gtk.Label(label=transition.event.name, xalign=0))

def listbox_sort_func(row_1, row_2, data, notify_destroy):
        return row_1.transition.event.name.lower() > row_2.transition.event.name.lower()

class Simulator:
    def __init__(self, automaton):
        self.automaton = automaton
        self.current_state = automaton.initial_state
        self.forward_depth = 1        
        self.backward_depth = 0
        self.ar = AutomatonRender()
        self.build()

    def build(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui/sim_builder.glade')
        
        self.box = self.builder.get_object('toplevel_box')
        self.darea = self.builder.get_object('simulator_draw')
        self.listbox = self.builder.get_object('event_listbox')
        self.backward_depth_spin = self.builder.get_object('backward_depth_spin')
        self.forward_depth_spin = self.builder.get_object('forward_depth_spin')

        self.listbox.set_sort_func(listbox_sort_func, None, False)

        self.darea.connect("draw", self.on_draw)
        self.listbox.connect("row-activated", self.on_row_activated)
        self.forward_depth_spin.connect("value-changed", self.spin_event)
        self.backward_depth_spin.connect("value-changed", self.spin_event)
        self.builder.connect_signals(self)
        self.reset_list_box()

    def get_root_widget(self):
        return self.box

    def list_box_clear(self):
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        
    def reset_list_box(self):
        for transition in self.current_state.out_transitions:
            self.listbox.add(ListBoxRowWithData(transition))
        self.listbox.show_all()
        self.darea.queue_draw()

    def on_row_activated(self, listbox, row):
        self.current_state = row.transition.to_state
        self.list_box_clear()
        self.reset_list_box()

    def on_draw(self, wid, cr):
        self.ar.draw_partial(cr, self.automaton, self.current_state, forward_deep=self.forward_depth, backward_deep=self.backward_depth)

    def spin_event(self, event):
        self.forward_depth = self.forward_depth_spin.get_value_as_int()
        self.backward_depth = self.backward_depth_spin.get_value_as_int()
        self.darea.queue_draw()


# test
if __name__ == '__main__':
    g = Automaton()
    from test_automata import automata_01
    automata_01(g)

    simulator = Simulator(g)

    main_window = Gtk.Window()
    main_window.connect("delete-event", Gtk.main_quit)
    main_window.add(simulator.get_root_widget())
    
    main_window.show_all()
    Gtk.main()




