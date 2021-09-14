#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk

from renderer import AutomatonRenderer


class FileIconMixin:
    def __init__(self, *args, icon_file_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not icon_file_name is None:
            image_widget = Gtk.Image()
            image_widget.set_from_file(icon_file_name)
            self.set_icon_widget(image_widget)


class FileIconToolButton(FileIconMixin, Gtk.ToolButton):
    pass


class FileIconToggleToolButton(FileIconMixin, Gtk.ToggleToolButton):
    def __init__(self, *args, tool_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_id = tool_id


class AutomatonEditorToolPalette(Gtk.ToolPalette):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tool = None

        self.grp_file = Gtk.ToolItemGroup.new("File")
        self.grp_build = Gtk.ToolItemGroup.new("Build")

        self.add(self.grp_file)
        self.add(self.grp_build)

        self.btn_save = Gtk.ToolButton(label="Save", icon_name='gtk-floppy')
        self.grp_file.insert(self.btn_save, -1)

        self._new_toggle_button(self.grp_build, tool_id='state_add', label="Add State", icon_file_name='./res/icons/state_add.png')
        self._new_toggle_button(self.grp_build, tool_id='state_initial', label="Make Initial State", icon_file_name='./res/icons/state_initial.png')
        self._new_toggle_button(self.grp_build, tool_id='state_marked', label="Mark State", icon_file_name='./res/icons/state_marked.png')
        self._new_toggle_button(self.grp_build, tool_id='transition_add', label="Add Transition", icon_file_name='./res/icons/transition_add.png')

    def _new_toggle_button(self, grp, *args, position=-1, **kwargs):
        btn = FileIconToggleToolButton(*args, **kwargs)
        grp.insert(btn, position)
        btn.connect('toggled', self.on_toggled)


    def get_selected_tool(self):
        if self.tool is None:
            return ''
        return self.tool.tool_id

    def clear_selection(self):
        if not self.tool is None:
            self.tool.set_active(False)
            self.tool = None

    def on_toggled(self, btn):
        if btn.get_active():
            if self.tool != btn:
                self.clear_selection()
            self.tool = btn

class AutomatonEditor(Gtk.Box):
    def __init__(self, automaton, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.automaton = automaton
        self.ar = AutomatonRenderer(self.automaton)
        self.selected_state = None
        self._build()

    def _build(self):
        self.paned = Gtk.Paned()
        self.scrolled = Gtk.ScrolledWindow.new()
        self.drawing_area = Gtk.DrawingArea.new()
        # self.listbox = Gtk.ListBox()

        self.pack_start(self.paned, True, True, 0)
        self.paned.pack1(self.scrolled, True, True)
        self.scrolled.add(self.drawing_area)


        self.drawing_area.connect("draw", self.on_draw)

    def on_draw(self, wid, cr):
        pass
        # self.ar.draw(cr, self.automaton)


