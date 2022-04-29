from jinja2 import Environment, FileSystemLoader
import math


class CodeGenerator():
    options = {"Arduino":
               {'tmpl_name': 'arduino.ino', 'tmpl_inheritance': ('generic_mic.h')}
              } # sketch for dealing with multiple devices
    def __init__(self, template_path='codegen/templates', template_name='arduino.ino', *args, **kwargs):
        loader = FileSystemLoader(template_path)
        self.environment = Environment(loader=loader)
        self.template = self.environment.get_template(template_name)

    def generate_variables(self, automaton_list):
        pass

    def write(self, automaton_list, output_path='codegen/output/arduino_out.ino'):
        
        # automatons = dict()
        data_pos = dict()
        state_map = dict()
        data = list()
        events = set()
        
        for k_automaton, automaton in enumerate(automaton_list):
            # automatons[k_automaton] = automaton
            data_pos[k_automaton] = len(data)
            for k_state, state in enumerate(automaton.states):
                state_map[state] = k_state
            for k_state, state in enumerate(automaton.states):
                data.append(len(state.out_transitions))
                for k_transition, transition in enumerate(state.out_transitions):
                    if transition.event.name not in [ev.name for ev in events]:  # treats events with identical names as the same event
                        events.add(transition.event)
                    data.append(f'EV_{transition.event.name}')
                    data.append(math.floor(state_map[transition.to_state]/256))
                    data.append(state_map[transition.to_state] % 256)

        _event_map = list()
        for automaton in automaton_list:
            _event_map.append(['1' if event.name in [ev.name for ev in automaton.events] else '0' for event in events])
        _str_event_map = list()
        for ev_in_automaton in _event_map:
            _str_event_map.append(self._create_var_from_array(ev_in_automaton))
        sup_event_map = self._create_var_from_array(_str_event_map)

        ev_controllable = self._create_bool_var(events, 'controllable')
        sup_init_state = self._create_var_from_array(automaton_list, append_from=state_map[automaton.initial_state])
        sup_data_pos = self._create_var_from_array(data_pos)
        sup_data = self._create_var_from_array(data)
        sup_current_state = sup_init_state

        render = self.template.render(
            automaton_list=automaton_list,
            events=events,
            data=data,
            ev_controllable=ev_controllable,
            sup_init_state=sup_init_state,
            sup_current_state=sup_current_state,
            sup_data_pos=sup_data_pos,
            sup_data=sup_data,
            sup_event_map=sup_event_map)

        with open(output_path, 'w') as out_file:
            out_file.write(render)

        self.template = self.environment.get_template('generic_mic.h')
        render = self.template.render(
            automaton_list=automaton_list,
            events=events
        )
        with open('codegen/output/generic_mic.h', 'w') as out_file:
            out_file.write(render)
        
        # sup_events = 


                    
        '''
        
        !! Not sure where sup_events[][] came from !!
        aux_supevents = list()
        sup_events = 
        for k_automaton, automaton in enumerate(automaton_list):
            aux_supevents.append(list())
            for i in range(len(events)):
                aux_supevents[k_automaton].append(aux_supevents[k_automaton][i] and True or False)
        print(aux_supevents)
{ {% for k_automaton, automaton in automata:ipairs() %}{ {% for i = 1, #events %}{{ sup_events[k_automaton][i] and 1 or 0 }}{% notlast %},{% end %} }{% notlast %},{% end %} };
        '''
        # print(f'sup_data_pos: {sup_data_pos}\nstate_map: {state_map}\nsup_data: {sup_data}\nsup_init_state: {sup_init_state}\nev_controllable: {ev_controllable}')
    
    def _create_var_from_array(self, array, append_from=None):
        aux = list()
        for element in array:
            if append_from is None:
                aux.append(str(element))
            else:
                aux.append(str(append_from))
        res = ', '.join(aux)
        res = f'{{{res}}}'
        return res

    def _create_bool_var(self, array, attribute):
        aux = list()
        for obj in array:
            aux.append(getattr(obj, attribute) and '1' or '0')
        data_str = ', '.join(aux)
        res = f'{{{data_str}}}'
        return res
        