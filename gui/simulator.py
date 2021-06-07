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

builder = Gtk.Builder()
builder.add_from_file('sim_builder.glade')

def create_automaton_01():
    g = Automaton()

    q0 = g.state_add('q0', x=50, y=150, marked=True, initial=True)
    q1 = g.state_add('q1', x=250, y=150, marked=True)
    q12 = g.state_add('q12', x=450, y=150, marked=True)
    q13 = g.state_add('q13', x=250, y=400, marked=True)
    q2 = g.state_add('q2', x=450, y=400, marked=True)
    q123 = g.state_add('q123', x=650, y=150, marked=True)

    a = g.event_add('a', True, True)
    b = g.event_add('b', False, True)
    c = g.event_add('c', True, False)


    g.transition_add(q0, q0, c)
    g.transition_add(q0, q0, b)
    g.transition_add(q0, q1, a)
    g.transition_add(q1, q12, b)
    g.transition_add(q1, q13, c)
    g.transition_add(q1, q1, a)
    g.transition_add(q12, q1, a)
    g.transition_add(q12, q2, b)
    g.transition_add(q12, q123, c)
    g.transition_add(q123, q1, a)
    g.transition_add(q123, q2, b)
    g.transition_add(q13, q1, a)
    g.transition_add(q13, q2, b)
    g.transition_add(q13, q13, c)
    g.transition_add(q2, q2, b)
    g.transition_add(q2, q1, a)
    g.transition_add(q2, q13, c)

    return g

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, transition):
        super(Gtk.ListBoxRow, self).__init__()
        self.transition = transition
        self.add(Gtk.Label(label=transition.event.name, xalign=0))

class Simulator(Gtk.Window):
    def __init__(self, automaton):
        super(Simulator, self).__init__()
        self.automaton = automaton
        self.current_state = automaton.initial_state
        self.darea = builder.get_object('simulator_draw')
        self.listbox = builder.get_object('event_listbox')
        self.forward_depth_spin = builder.get_object('forward_depth_spin')
        self.forward_depth = 1
        self.backward_depth_spin = builder.get_object('backward_depth_spin')
        self.backward_depth = 0
        self.ar = AutomatonRender()
        self.build()

    def build(self):
        self.darea.connect("draw", self.on_draw)
        self.listbox.connect("row-selected", self.on_row_selected)
        self.forward_depth_spin.connect("value-changed", self.spin_event)
        self.backward_depth_spin.connect("value-changed", self.spin_event)
        self.reset_list_box()

    def list_box_clear(self, row):
        self.listbox = Gtk.ListBox()

    def reset_list_box(self):
        for transition in self.current_state.out_transitions:
            self.listbox.add(ListBoxRowWithData(transition))
        self.listbox.show_all()
        self.darea.queue_draw()

    def on_row_selected(self, listbox, row):
        self.current_state = row.transition.to_state
        self.list_box_clear(row)
        self.reset_list_box()

    def on_draw(self, wid, cr):
        self.ar.draw_partial(cr, self.automaton, self.current_state, forward_deep=self.forward_depth, backward_deep=self.backward_depth)

    def spin_event(self, event):
        self.forward_depth = self.forward_depth_spin.get_value_as_int()
        self.backward_depth = self.backward_depth_spin.get_value_as_int()
        self.darea.queue_draw()

    def on_window_destroy(self, window):
        Gtk.main_quit()

builder.connect_signals(Simulator(create_automaton_01()))
main_window = builder.get_object('window')
main_window.show_all()
Gtk.main()




