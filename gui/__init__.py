import gi
gi.require_version("Gtk", "3.0")

from gui.application import Application
#~ from gui.editor import Editor

from gui.render.automaton import AutomatonRender

__all__ = ['Application', 'AutomatonRender']
