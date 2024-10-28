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

class AutomatonEditorProbabilistic(AutomatonEditor):
    def _get_selected_object(self):
        if self.selected_state is not None:
            return self.selected_state
        elif self.selected_transitions is not None:
            return self.selected_transitions
        else:
            return None

    def update_properties_box(self):
        self.frame_props.hide()
        self.propbox.clear()
        selected_object = self._get_selected_object()

        if selected_object is not None:
            if self.selected_state is not None:
                for prop in selected_object.properties:
                    label_text = prop['label']
                    property_name = prop['property']
                    value = getattr(selected_object, property_name)
                    if prop['gtk_control'] == 'checkbutton':
                        self.propbox.add_checkbutton(label_text, value, property_name)
                    elif prop['gtk_control'] == 'entry':
                        self.propbox.add_entry(label_text, value, property_name)
                    elif prop['gtk_control'] == 'switch':
                        self.propbox.add_switch(label_text, value, property_name)
                    elif prop['gtk_control'] == 'spinbutton':
                        self.propbox.add_spinbutton(label_text, value, property_name, lower=-5000, upper=5000)
            elif self.selected_transitions is not None:
                for transition in selected_object:
                    for prop in transition.properties:
                        label_text = f'{transition.event}:\t{prop["label"]}'
                        property_name = prop['property']
                        value = getattr(transition, property_name)
                        if prop['gtk_control'] == 'checkbutton':
                            self.propbox.add_checkbutton(label_text, value, property_name)
                        elif prop['gtk_control'] == 'entry':
                            self.propbox.add_entry(label_text, value, property_name, event_name=transition.event.name)
                        elif prop['gtk_control'] == 'switch':
                            self.propbox.add_switch(label_text, value, property_name)
                        elif prop['gtk_control'] == 'spinbutton':
                            self.propbox.add_spinbutton(label_text, value, property_name, lower=-5000, upper=5000)
            self.propbox.show_all()
            self.frame_props.show()
        
    def prop_edited(self, propbox, value, data, widget_name):
        selected_object = self._get_selected_object()
        if selected_object is not None:
            if self.selected_state is not None:
                setattr(selected_object, data, value)
            elif self.selected_transitions is not None:
                for i, transition in enumerate(selected_object):
                    if transition.event.name == widget_name:
                        setattr(selected_object[i], data, value)
            self.automaton_render.queue_draw()
            self.trigger_change()