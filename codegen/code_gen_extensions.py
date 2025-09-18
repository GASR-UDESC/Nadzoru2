from codegen.code_gen import BaseGenerator, ArduinoGenerator, CGenerator, CPPGenerator, KilobotGenerator, PythonGenerator
import math

##### Public events extension #####

class BaseGeneratorPublic(BaseGenerator):

    def add_extra_properties(self, events):
        str_public = ['1' if event.public else '0' for event in events]
        ev_public = self._gen_str(str_public)
        return {'ev_public': ev_public}

class ArduinoGeneratorPublic(BaseGeneratorPublic, ArduinoGenerator):
    templates_name = ['arduino_public.ino', 'generic_mic.h']

class CGeneratorPublic(BaseGeneratorPublic, CGenerator):
    templates_name = ['generic_mic_public.h', 'generic_mic_public.c']

class CPPGeneratorPublic(BaseGeneratorPublic, CPPGenerator):
    templates_name = ['supervisor_public.yaml', 'sct.cpp', 'sct.h']

class KilobotGeneratorPublic(BaseGeneratorPublic, KilobotGenerator):
    templates_name = ['kilobotAtmega328_public.c']

class PythonGeneratorPublic(BaseGeneratorPublic, PythonGenerator):
    templates_name = ['supervisor_public.yaml', 'sct.py']

##### Probabilistic events extension #####

class BaseGeneratorProbabilistic(BaseGenerator):
    
    def generate_sup(self, automaton_list):
        '''This will generate the information contained in a supervisor.
        
        [data]      : [n of out transitions in a state, 'event_name1', from_state, to_state, 'event_name2', from_state, to_state]...

        {data_pos}  : {automaton0: index, automaton1, index, ...} - contains the initial index for each automaton in [data]

        {state_map} : {state: number}, where number is an arbitrary value that will represent the state

        {events,}   : set of all events. Events with the same name in different automatons are treated as the same event

        [event_map] : [[automaton0], [automaton1], ...] where [automaton0] is a list of booleans with n_events elements. If True, the automaton contains the event in this index (related to the {event, } set)
        
        '''
        data_pos = dict()
        state_map = dict()
        data = list()
        event_map = list()
        events = set()
        initial_state = list()

        self.data_prob = list()
        self.data_prob_pos = dict()

        for k_automaton, automaton in enumerate(automaton_list):
            data_pos[k_automaton] = len(data)
            self.data_prob_pos[k_automaton] = len(self.data_prob)
            for k_state, state in enumerate(automaton.states):
                state_map[state] = k_state
                if state == automaton.initial_state:
                    initial_state.append(k_state)
            for k_state, state in enumerate(automaton.states):
                data.append(len(state.out_transitions))
                num_controllable = sum(
                    1 for transition in state.out_transitions
                    if transition.event.controllable
                )
                self.data_prob.append(num_controllable)
                for k_transition, transition in enumerate(state.out_transitions):
                    # treats events with identical names as the same event
                    if transition.event.name not in [ev.name for ev in events]:
                        events.add(transition.event)
                    data.append(f'EV_{transition.event.name}')
                    data.append(math.floor(state_map[transition.to_state]/256))
                    data.append(state_map[transition.to_state] % 256)

                    # Add probability info if controllable
                    if transition.event.controllable:
                        if transition.probability >= 1.0:
                            self.data_prob.append("1")
                        else:
                            self.data_prob.append(f"{transition.probability:.8f}")

        for automaton in automaton_list:
            event_map.append([True if event.name in [ev.name for ev in automaton.events] else False for event in events])

        return (data, data_pos, state_map, events, event_map, initial_state)
    
    def add_extra_properties(self, events):
        data_prob = self._gen_str(self.data_prob)
        data_prob_pos = self._gen_str(self.data_prob_pos)
        return {'data_prob': self.data_prob, 'sup_data_prob': data_prob, 'sup_data_prob_pos': data_prob_pos}

class CGeneratorProbabilistic(BaseGeneratorProbabilistic, CGenerator):
    templates_name = ['generic_mic_probabilistic.h', 'generic_mic_probabilistic.c']

class CPPGeneratorProbabilistic(BaseGeneratorProbabilistic, CPPGenerator):
    templates_name = ['supervisor_probabilistic.yaml', 'sct.cpp', 'sct.h']

class KilobotGeneratorProbabilistic(BaseGeneratorProbabilistic, KilobotGenerator):
    templates_name = ['kilobotAtmega328_probabilistic.c']

class PythonGeneratorProbabilistic(BaseGeneratorProbabilistic, PythonGenerator):
    templates_name = ['supervisor_probabilistic.yaml', 'sct.py']
