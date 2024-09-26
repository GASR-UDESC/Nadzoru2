from machine.automaton import Event, Automaton

class EventPublic(Event):
    def __init__(self, name='', controllable=False, observable=True, public=False, tex=None, *args, **kwargs):
        self.public = public
        super().__init__(name, controllable, observable, tex, *args, **kwargs)
    
    def copy_new_object(self):
        return EventPublic(str(self.name), self.controllable, self.observable, self.public, str(self.tex))
    
    @property
    def public(self):
        return self._public
    
    @public.setter
    def public(self, value):
        if isinstance(value, bool):
            self._public = value

    def equivalent_properties(self, other):
        return super().equivalent_properties(other) and self.public == other.public


class AutomatonPublic(Automaton):
    event_class = EventPublic

    def get_write_event_string(self, event_id, event):
        return f'\t<event id="{event_id}" name="{event.name}" controllable="{event.controllable}" observable="{event.observable}" public="{event.public}"/>\n'
        
    def load_add_event(self, name, event_tag, is_observable, is_controllable):
        is_public = self.str2bool(event_tag.getAttribute('public'))
        return self.event_add(name, observable=is_observable, controllable=is_controllable, public=is_public)
    
    def get_event_data_str(self, event_content_str):
        event_data_str = self.get_data({ ('id', ' = {'),
                                        ('observable', '["observable"] = '),
                                        ('name', '["name"] ='),
                                        ('controllable', '["controllable"] = '),
                                        ('public', '["shared"] = ')},
                                        event_content_str)
        return event_data_str

    def legacy_nadzoru_import_add_events(self, data_str):
        is_controllable = is_public = False
        for prop_name, prop in data_str:
            if prop_name == 'id':
                ev_id = prop
            elif prop_name == 'observable':
                is_observable = prop.lower() == 'true'
            elif prop_name == 'controllable':
                is_controllable = prop.lower() == 'true'
            elif prop_name == 'public':
                is_public = prop.lower() == 'true'
            elif prop_name == 'name':
                prop = prop.lstrip()
                ev_name = prop.replace('"', "")
        event = self.event_add(ev_name, observable=is_observable, controllable=is_controllable, public=is_public)
        return ev_id, event
    
    def determinize_event_add(self, determinized_automaton, event):
        return determinized_automaton.event_add(event.name, event.controllable, event.observable, event.public)
    