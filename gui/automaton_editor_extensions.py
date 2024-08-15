from gi.repository import Gtk

from gui.automaton_editor import AutomatonEditor

class AutomatonEditorPublic(AutomatonEditor):
    def __init__(self, automaton, *args, **kwargs):
        super().__init__(automaton, *args, **kwargs)
        self.index_object = 4
    
    def build_treeview_create_liststore(self):
        return Gtk.ListStore(str, bool, bool, bool, object)
    
    def add_extra_toggles(self):
        # Toggle 3
        renderer_toggle_3 = Gtk.CellRendererToggle()
        renderer_toggle_3.connect('toggled', self.renderer_toggle_public)
        column_toggle_3 = Gtk.TreeViewColumn("Public", renderer_toggle_3, active=3)
        self.treeview.append_column(column_toggle_3)

    def update_treeview_add_events(self, rows):
        for event in self.automaton.events:
            rows.append([event.name, event.controllable, event.observable, event.public, event])
        return rows

    def renderer_toggle_public(self, widget, path):
        event = self.liststore[path][self.index_object]
        event.public = not event.public
        self.update_treeview()
        self.trigger_change()
