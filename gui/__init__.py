import gi
gi.require_version("Gtk", "3.0")

from gui.application import Application
from gui.automaton_editor import AutomatonEditor

__all__ = ['Application', 'AutomatonEditor']
