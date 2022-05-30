from re import template
from jinja2 import Environment, FileSystemLoader, meta
import math



class BaseGenerator():
    template_path = 'codegen/templates'
    def __init__(self, *args, **kwargs):
        self.options = dict()
        self.device = None
        loader = FileSystemLoader(self.template_path)
        self.environment = Environment(loader=loader)

    def show(self):
        devs = ''
        opts = ''
        for k, v in self.items():
            devs += f'{k}, '
            opts += f'{k}: {v}\n\t'
        print(f'{__class__}\nDevice: {devs}\nOptions: {opts}')
        return f'{__class__}\nDevice: {devs}\nOptions: {opts}'

    def set_device(self, device):
        self.options = dict()
        self.device = device
    
    def get_options(self):
        return self.options.items()

    def set_option(self, opt_name, label, widget_type, opt):
        self.options[opt_name] = opt
        self.options[opt_name].update({'label': label, 'widget_type': widget_type})

    def set_template_path(self, template_path):
        self.template_path = template_path

    def _write(self, output_path=None, arguments:dict={}):
        for tmplt_name in self.templates_name:
            
            if output_path is None:
                out_path = f'codegen/output/{tmplt_name}'
            else:
                out_path = f'{output_path}/{tmplt_name}'
            
            tmplt_vars = self.get_template_variables(tmplt_name)
            vars_to_render = {key: arguments[key] for key in arguments.keys() & tmplt_vars}

            template = self.environment.get_template(tmplt_name)
            render = template.render(**vars_to_render)
            with open(out_path, 'w') as out_file:
                out_file.write(render)

    def get_template_variables(self, filename):
        template_source = self.environment.loader.get_source(self.environment, filename)
        parsed_content = self.environment.parse(template_source)
        return meta.find_undeclared_variables(parsed_content)
    
class GenericMcu(BaseGenerator):
    templates_name = ['generic_mic.h']
    template_path = 'codegen/templates'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_template_path(self.template_path)

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

        for k_automaton, automaton in enumerate(automaton_list):
            # automatons[k_automaton] = automaton
            data_pos[k_automaton] = len(data)
            for k_state, state in enumerate(automaton.states):
                state_map[state] = k_state
                if state == automaton.initial_state:
                    initial_state.append(k_state)
            for k_state, state in enumerate(automaton.states):
                data.append(len(state.out_transitions))
                for k_transition, transition in enumerate(state.out_transitions):
                    # treats events with identical names as the same event
                    if transition.event.name not in [ev.name for ev in events]:
                        events.add(transition.event)
                    data.append(f'EV_{transition.event.name}')
                    data.append(math.floor(state_map[transition.to_state]/256))
                    data.append(state_map[transition.to_state] % 256)

        for automaton in automaton_list:
            event_map.append([True if event.name in [ev.name for ev in automaton.events] else False for event in events])

        return (data, data_pos, state_map, events, event_map, initial_state)

class ArduinoGenerator(GenericMcu):
    templates_name = ['arduino.ino', 'generic_mic.h']
    template_path = 'codegen/templates'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_device('arduino')

        self.set_template_path(self.template_path) 

        RANDOM_PSEUDOFIX = 0
        RANDOM_PSEUDOAD = 1
        RANDOM_AD = 2
        INPUT_TIMER = 0
        INPUT_MULTIPLEXED = 1
        INPUT_RS232 = 2

        self.set_option('random_fn', "Random Type", 'choice', {
            'options': [
                ("Pseudo Random Seed Fixed",    RANDOM_PSEUDOFIX),
                ("Pseudo Random Seed AD input", RANDOM_PSEUDOAD),
                ("AD input",                    RANDOM_AD)
            ]})
        self.set_option('input_fn', "Input (Delay Sensitibility)", 'choice', {
            'options': [
                ("Timer Interruption",                  INPUT_TIMER),
                ("Multiplexed External Interruption",   INPUT_MULTIPLEXED),
                ("RS232 with Interrupt",                INPUT_RS232)
                       ]     
        })
        self.set_option('ad_port', "AD Port", 'choice', {
            'options': [
                ("AN0", '0'), ("AN1", '1'), ("AN2", '2'),
                ("AN4", '4'), ("AN5", '5'), ("AN6", '6'),
                ("AN7", '7'), ("AN8", '8'), ("AN9", '9')
                       ]
        })

    def write(self, automatons, vars_dict, output_path):
        output_dict = self.generate_strings(automatons)
        output_dict.update(vars_dict)
        self._write(output_path, output_dict)

    def generate_strings(self, automatons):
        data, data_pos, state_map, events, event_map, initial_state = self.generate_sup(automatons)

        def _gen_str(data_to_gen):
            aux = list()
            if type(data_to_gen) == dict:
                for v in data_to_gen.values():
                    aux.append(str(v))
            elif type(data_to_gen) == list:
                for element in data_to_gen:
                    aux.append(str(element))
            res = ', '.join(aux)
            res = f'{{{res}}}'
            return res

        sup_data_pos = _gen_str(data_pos)
        sup_data = _gen_str(data)
        sup_init_state = _gen_str(initial_state)
        sup_current_state = sup_init_state

        str_controllable = ['1' if event.controllable else '0'  for event in events]
        ev_controllable = _gen_str(str_controllable)

        str_event_map = list()
        for automaton_event_list in event_map:
            str_event_map.append(['1' if event else '0' for event in automaton_event_list])
        sup_event_map = _gen_str(str_event_map)

        return {'automaton_list': automatons,
                'events': events,
                'data': data,
                'ev_controllable': ev_controllable,
                'sup_init_state': sup_init_state,
                'sup_current_state': sup_current_state,
                'sup_data_pos': sup_data_pos,
                'sup_data': sup_data,
                'sup_event_map': sup_event_map}