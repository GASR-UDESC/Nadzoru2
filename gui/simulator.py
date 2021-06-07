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
    a = Automaton()

    e1 = a.event_add('a', True, True)
    e2 = a.event_add('b', False, True)
    e3 = a.event_add('c', True, False)
    e4 = a.event_add('d', False, False)
    s1 = a.state_add('q1', x=100, y=150, marked=True, initial=True)
    s2 = a.state_add('q2', x=400, y=150, marked=True)
    s3 = a.state_add('q3', x=250, y=400, marked=True)

    a.transition_add(s1, s2, e1)
    a.transition_add(s2, s1, e2)
    a.transition_add(s1, s1, e2)
    a.transition_add(s2, s2, e1)
    a.transition_add(s1, s3, e3)
    a.transition_add(s2, s3, e3)
    a.transition_add(s3, s1, e1)
    a.transition_add(s3, s2, e2)
    t = a.transition_add(s3, s3, e3)
    # a.transition_remove(t)
    a.transition_add(s1, s2, e4)
    a.transition_add(s2, s1, e4)

    return a

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
        self.ar = AutomatonRender()
        self.build()

    def build(self):
        self.darea.connect("draw", self.on_draw)
        self.listbox.connect("row-selected", self.on_row_selected)
        self.reset_list_box()

    def list_box_clear(self, row):
        for r in self.listbox.get_children():
            if r != row:
                self.listbox.remove(r)

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
        print(self.current_state)
        self.ar.draw_partial(cr, self.automaton, self.current_state)

    def on_window_destroy(self, window):
        Gtk.main_quit()

builder.connect_signals(Simulator(create_automaton_01()))
main_window = builder.get_object('window')
main_window.show_all()
Gtk.main()




