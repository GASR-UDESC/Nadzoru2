#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins
from machine.automaton import Automaton

import gui
from render import AutomatonRender

import gi
from gi.repository import Gtk, Gdk

def create_automaton_01():
    a = Automaton()

    e1 = a.event_add('a', True, True)
    e2 = a.event_add('b', False, True)
    e3 = a.event_add('c', True, False)
    e4 = a.event_add('d', False, False)
    s1 = a.state_add('q1', x=100, y=150, marked=True, initial=True)
    s2 = a.state_add('q2', x=400, y=150, marked=True)
    s3 = a.state_add('q3', x=250, y=400, marked=True)
    s4 = a.state_add('q4', x=550, y=400, marked=True)
    s5 = a.state_add('q5', x=700, y=400, marked=True)

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
    a.transition_add(s3, s4, e4)
    a.transition_add(s4, s5, e4)

    return a


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class Example(Gtk.Window):
    def __init__(self, automaton):
        super(Example, self).__init__()
        self.init_ui()
        self.automaton = automaton
        self.current_state = self.automaton.initial_state
        self.lst_state = list(automaton.states)
        self.ar = AutomatonRender()
        self.id = 0

    def init_ui(self):
        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.darea.set_events(Gdk.EventMask.BUTTON_MOTION_MASK |
                              Gdk.EventMask.BUTTON_PRESS_MASK
        )
        self.add(self.darea)

        self.darea.connect("motion-notify-event", self.on_motion_notify)
        self.darea.connect("button-press-event", self.on_button_press)

        self.set_title("Render Automaton test")
        self.resize(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_draw(self, wid, cr):
        # self.ar.draw(cr, self.automaton)
        self.ar.draw_partial(cr, self.automaton, self.current_state)

    def on_motion_notify(self, w, e):
        if e.type == Gdk.EventType.MOTION_NOTIFY and (e.state & Gdk.ModifierType.BUTTON1_MASK):
            pass
            # s = self.lst_state[0]
        elif e.type == Gdk.EventType.MOTION_NOTIFY and (e.state & Gdk.ModifierType.BUTTON3_MASK):
            pass
            # s = self.lst_state[1]
        else:
            return
        s = self.lst_state[self.id]
        s.x = e.x
        s.y = e.y
        self.darea.queue_draw()

    def on_button_press(self, w, e):
        if e.type == Gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.LEFT_BUTTON:
            # s = self.lst_state[0]
            self.id += 1
            if self.id >= len(self.lst_state):
                self.id = 0
        elif e.type == Gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.RIGHT_BUTTON:
            # s = self.lst_state[1]
            self.id -= 1
            if self.id < 0:
                self.id = len(self.lst_state) - 1
        else:
            return
        s = self.lst_state[self.id]
        s.x = e.x
        s.y = e.y
        self.current_state = s
        self.darea.queue_draw()


app = Example(create_automaton_01())
Gtk.main()
