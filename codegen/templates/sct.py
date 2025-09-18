import random
import yaml

class SCT:

    def __init__(self, filename):

        self.read_supervisor(filename)

        self.callback = {}
        self.input_buffer = None # Clear content after timestep
        self.last_events = [0] * len(self.EV)


    def read_supervisor(self, filename):
        try:
            with open(filename, 'r') as stream:
                self.f = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e) 

        self.num_events = self.f['num_events']
        self.num_supervisors = self.f['num_supervisors']
        self.EV = {}
        for i, ev in enumerate(self.f['events']):
            self.EV[ev] = i
        
        self.ev_controllable = self.f['ev_controllable']
        self.sup_events = self.f['sup_events']
        self.sup_init_state = self.f['sup_init_state']
        self.sup_current_state = self.f['sup_current_state']
        self.sup_data_pos = self.f['sup_data_pos']
        self.sup_data = self.f['sup_data']


    def add_callback(self, event, clbk, ci, sup_data):
        func = {}
        func['callback']    = clbk
        func['check_input'] = ci
        func['sup_data']    = sup_data
        self.callback[event] = func


    def run_step(self):
        self.input_buffer = [] # clear buffer
        self.update_input()

        # Get all uncontrollable events
        uce = self.input_buffer

        # Apply all the uncontrollable events
        while uce:
            event = uce.pop(0)
            self.make_transition(event)
            self.exec_callback(event)

        ce_exists, ce = self.get_next_controllable()

        # Apply the chosen controllable event
        if ce_exists:
            self.make_transition(ce)
            self.exec_callback(ce)


    def input_read(self, ev):
        event_name = self.get_event_name(ev)
        if ev < self.num_events and self.callback[event_name]:
            return self.callback[event_name]['check_input'](self.callback[event_name]['sup_data'])
        return False


    def update_input(self):
        for i in range(0,self.num_events):
            if not self.ev_controllable[i]: # Check the UCEs only
                if self.input_read(i):
                    self.input_buffer.append(i)
                    self.last_events[i] = 1


    def get_state_position(self, supervisor, state):
        position = self.sup_data_pos[supervisor]    # Jump to the start position of the supervisor
        for s in range(0, state):                   # Keep iterating until the state is reached
            en = self.sup_data[position]            # The number of transitions in the state
            position += en * 3 + 1                  # Next state position (Number transitions * 3 + 1)
        return position


    def make_transition(self, ev):
        num_transitions = None

        # Apply transition to each local supervisor
        for i in range(0, self.num_supervisors):
            if self.sup_events[i][ev]: # Check if the given event is part of this supervisor

                # Current state info of supervisor
                position = self.get_state_position(i, self.sup_current_state[i])
                num_transitions = self.sup_data[position]
                position += 1 # Point to first transition

                # Find the transition for the given event
                while num_transitions:
                    num_transitions -= 1
                    value = self.get_value(self.sup_data[position])
                    if value == ev:
                        self.sup_current_state[i] = (self.sup_data[position + 1] * 256) + (self.sup_data[position + 2])
                        break
                    position += 3


    def exec_callback(self, ev):
        event_name = self.get_event_name(ev)
        if ev < self.num_events and self.callback[event_name]['callback']:
            self.callback[event_name]['callback'](self.callback[event_name]['sup_data'])


    def get_next_controllable(self):
        
        # Get controllable events that are enabled -> events
        actives = self.get_active_controllable_events()
        
        if not all(v == 0 for v in actives):
            randomPos = random.randint(0,1000000000) % actives.count(1)
            for i in range(0, self.num_events):
                if not randomPos and actives[i]:
                    return True, i
                elif actives[i]:
                    randomPos -= 1

        return False, None


    def get_active_controllable_events(self):

        events = []

        # Disable all non controllable events
        for i in range(0, self.num_events):
            if not self.ev_controllable[i]:
                events.append(0)
            else:
                events.append(1)

        # Check disabled events for all supervisors
        for i in range(0, self.num_supervisors):

            # Init an array where all events are disabled
            ev_disable = [1] * self.num_events

            # Enable all events that are not part of this supervisor
            for j in range(0, self.num_events):
                if not self.sup_events[i][j]:
                    ev_disable[j] = 0

            # Get current state
            position = self.get_state_position(i, self.sup_current_state[i])
            num_transitions = self.sup_data[position]
            position += 1

            # Enable all events that have a transition from the current state
            while num_transitions:
                num_transitions -= 1
                value = self.get_value(self.sup_data[position])
                ev_disable[value] = 0
                position += 3

            # Remove the controllable events to disable, leaving an array of enabled controllable events
            for j in range(0, self.num_events):
                if ev_disable[j] == 1 and events[j]:
                    events[j] = 0

        return events


    def get_value(self, index):
        if isinstance(index, str):
            return self.EV[index]    
        return index
    

    def get_event_name(self, index):
        if isinstance(index, int):
            return list(self.EV.keys())[list(self.EV.values()).index(index)]
        return index


    # Get function that returns event information (event names and controllability)
    def get_events(self):
        return self.EV, self.ev_controllable


class SCTPub(SCT):

    def __init__(self, filename):
        super().__init__(filename)
        self.ev_public = self.f['ev_public']


    def run_step(self):
        self.input_buffer = [] # clear buffer
        self.input_buffer_pub = []
        self.update_input()

        # Apply all public uncontrollable events
        public_uce = self.input_buffer_pub
        while public_uce:
            event = public_uce.pop(0)
            self.make_transition(event)
            self.exec_callback(event)

        # Apply all private uncontrollable events
        uce = self.input_buffer
        while uce:
            event = uce.pop(0)
            self.make_transition(event)
            self.exec_callback(event)

        ce_exists, ce = self.get_next_controllable()

        # Apply the chosen controllable event
        if ce_exists:
            self.make_transition(ce)
            self.exec_callback(ce)


    def update_input(self):
        for i in range(0,self.num_events):
            if not self.ev_controllable[i]: # Check the UCEs only
                if self.input_read(i):
                    if self.ev_public[i]:
                        self.input_buffer_pub.append(i)
                    else:
                        self.input_buffer.append(i)
                    self.last_events[i] = 1

class SCTProb(SCT):

    def __init__(self, filename):
        super().__init__(filename)
        self.sup_data_prob_pos = self.f['sup_data_prob_pos']
        self.sup_data_prob = self.f['sup_data_prob']

    
    def get_state_position_prob(self, supervisor, state):
        prob_position = self.sup_data_prob_pos[supervisor]  # Jump to the start position of the supervisor
        for s in range(0, state):                           # Keep iterating until the state is reached
            en = self.sup_data_prob[prob_position]          # The number of transitions in the state
            prob_position += en + 1                         # Next state position (Number transitions * 3 + 1)
        return prob_position


    def get_active_controllable_events_prob(self):

        events = []

        # Disable all non controllable events
        for i in range(0, self.num_events):
            if not self.ev_controllable[i]:
                events.append(0)
            else:
                events.append(1)

        # Check disabled events for all supervisors
        for i in range(0, self.num_supervisors):

            # Init an array where all events are disabled
            ev_disable = [1] * self.num_events

            # Enable all events that are not part of this supervisor
            for j in range(0, self.num_events):
                if not self.sup_events[i][j]:
                    ev_disable[j] = 0

            # Get current state
            position = self.get_state_position(i, self.sup_current_state[i])
            position_prob = self.get_state_position_prob(i, self.sup_current_state[i])
            num_transitions = self.sup_data[position]
            position += 1
            position_prob += 1

            # Enable all events that have a transition from the current state
            while num_transitions:
                num_transitions -= 1
                value = self.get_value(self.sup_data[position])

                if self.ev_controllable[value] and self.sup_events[i][value]:
                    ev_disable[value] = 0 # Transition with this event, do not disable it, just calculate its probability contribution
                    events[value] = events[value] * self.sup_data_prob[position_prob]
                    position_prob += 1

                position += 3

            for j in range(self.num_events):
                if ev_disable[j] == 1:
                    events[j] = 0

        return events
    

    def get_next_controllable(self):
        
        # Get controllable events that are enabled -> events
        events = self.get_active_controllable_events_prob()
        prob_sum = sum(events)

        if prob_sum > 0.0001: # If at least one event is enabled do
            random_value = random.uniform(0, prob_sum)
            random_sum = 0.0
            for i in range(self.num_events):
                random_sum += events[i]
                if (random_value < random_sum) and self.ev_controllable[i]:
                    return True, i

        return False, None
    