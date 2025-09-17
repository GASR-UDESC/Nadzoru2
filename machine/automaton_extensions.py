from machine.automaton import Event, Transition, Automaton

##### PUBLIC EVENTS #####

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
    

##### PROBABILISTIC EVENTS #####

class TransitionProbabilistic(Transition):
    properties = [{'label': "probability", 'property': 'probability', 'gtk_control': 'entry'}]

    def __init__(self, from_state, to_state, event, probability, *args, **kwargs):
        self.probability = probability
        super().__init__(from_state, to_state, event, probability, *args, **kwargs)

    def copy(self, memo=None):
        return_memo = True
        if memo is None:
            return_memo = False
            memo = {}

        if id(self) in memo:
            if return_memo:
                return memo[id(self)], memo
            return memo[id(self)]
        
        if isinstance(self, TransitionProbabilistic):
            from_state, memo = self.from_state.copy(memo)
            to_state, memo = self.to_state.copy(memo)
            event, memo = self.event.copy(memo)
            probability = self.probability
            new_obj = TransitionProbabilistic(from_state=from_state, to_state=to_state, event=event, probability=probability)
        else:
            new_obj, memo = super().copy(memo)
        
        memo[id(self)] = new_obj
        if return_memo:
            return memo[id(self)], memo
        return memo[id(self)]

    @property
    def probability(self):
        return self._probability
    
    @probability.setter
    def probability(self, value):
        try:
            value = float(value)
            self._probability = value
        except ValueError:
            raise ValueError(f"Probability must be a float, got {value} of type {type(value)}")

    def __str__(self):
        return "{from_state}, {event} --> {to_state}, prob = {prob}".format(from_state=self.from_state, to_state=self.to_state, event=self.event, prob=self.probability)


class AutomatonProbabilistic(Automaton):
    transition_class = TransitionProbabilistic

    def transition_with_probability(G, source_state, target_state, event, state_tuple, args):
        # Extract probabilities from the original transitions
        probabilities = []
        for g, s in zip(args, state_tuple):
            prob = None
            for t in s.out_transitions:
                if t.event.name == event.name:
                    prob = getattr(t, 'probability', None)
                    break
            probabilities.append(prob)
        filtered_probs = [p for p in probabilities if p is not None]
        combined_probability = None
        if filtered_probs:
            combined_probability = 1
            for p in filtered_probs:
                combined_probability *= p
        if combined_probability is not None:
            G.transition_add(source_state, target_state, event, probability=combined_probability)
        else:
            G.transition_add(source_state, target_state, event)

    def synchronization(*args, output_univocal=False):
        return Automaton.synchronization(*args, output_univocal=output_univocal, transition_callback=AutomatonProbabilistic.transition_with_probability)

    def transition_add(self, from_state, to_state, event, probability=1, *args, **kwargs):
        t = self.transition_class(from_state, to_state, event, probability, *args, **kwargs)
        from_state.transition_out_add(t)
        to_state.transition_in_add(t)
        event.transition_add(t)
        return t
    
    def load_add_transition(self, transition_tag, source_state, target_state, event):
        prob = transition_tag.getAttribute('probability')
        # TODO Check if the parsed number is a number e.g. int/float
        return self.transition_add(source_state, target_state, event, probability=prob)

    def get_write_transition_string(self, source_state_id, target_state_id, event_id, transition):
        return f'\t<transition source="{source_state_id}" target="{target_state_id}" event="{event_id}" probability="{transition.probability}"/>\n'
