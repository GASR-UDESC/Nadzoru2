#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk

from renderer import AutomatonRenderer


class AutomatonEditor(Gtk.Box):
    def __init__(self, automaton, application, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.automaton = automaton
        self.application = application
        self.selected_state = None

        self.paned = Gtk.Paned()
        self.scrolled = Gtk.ScrolledWindow.new()
        self.automaton_render = AutomatonRenderer(self.automaton)
        # self.listbox = Gtk.ListBox()

        self.pack_start(self.paned, True, True, 0)
        self.paned.pack1(self.scrolled, True, True)
        self.scrolled.add(self.automaton_render)

        self.automaton_render.connect("draw", self.on_draw)
        self.automaton_render.connect("motion-notify-event", self.on_motion_notify)
        self.automaton_render.connect("button-press-event", self.on_button_press)

    def on_draw(self, automaton_render, cr):
        self.automaton_render.draw(cr)

    def on_motion_notify(self, automaton_render, event):
        pass

    def on_button_press(self, automaton_render, event):
        x, y = event.get_coords()
        tool_name = self.application.window.toolpallet.get_selected_tool()

        if tool_name == 'state_add':
            self.automaton.state_add(None, x=x, y=y)
        elif tool_name == 'transition_add':
            pass

        self.automaton_render.queue_draw()


