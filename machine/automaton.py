#######################################
# CLASSES
#######################################

import copy
import functools
import random
import os
import sys
from random import seed
from random import randint
from enum import Enum
from xml.dom.minidom import parse
import re

cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

class EventNameDuplicateException(Exception):
    pass

class Base:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            print("Warning: key '{key}' @ '{class_}' was not consumed by any pluggin, value: '{value}'.".format(
                    key=key,
                    value=value,
                    class_=self.__class__
                ))

        # self.__dict__.update(kwargs)

    def copy(self):
        return copy.deepcopy(self)

    @classmethod
    def plugin_append(cls, plugin):
        cls.__bases__ = cls.__bases__ + (plugin, )

    @classmethod
    def plugin_prepend(cls, plugin):
        cls.__bases__ = (plugin, ) + cls.__bases__


class Event(Base):
    def __init__(self, name='', controllable=False, observable=True, tex=None, *args, **kwargs):
        self.name = name
        self.tex = tex if tex is not None else name
        self.controllable = controllable
        self.observable = observable
        self.transitions = set()
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value

    @property
    def tex(self):
        return self._tex

    @tex.setter
    def tex(self, value):
        if isinstance(value, str):
            self._tex = value

    @tex.deleter
    def tex(self):
        self._tex = self._name

    @property
    def controllable(self):
        return self._controllable

    @controllable.setter
    def controllable(self, value):
        if isinstance(value, bool):
            self._controllable = value

    @property
    def observable(self):
        return self._observable

    @observable.setter
    def observable(self, value):
        if isinstance(value, bool):
            self._observable = value

    def transition_add(self, transition):
        self.transitions.add(transition)

    def equivalent_properties(self, other):
        if self.controllable != other.controllable:
            return False
        if self.observable != other.observable:
            return False
        return True


class EventSet(Base):  # TODO
    pass


class TransitionLayout:
    def __init__(self):
        self.render_angle = 0.0
        self.render_factor = 1.0
        self.ref_count = 0

    def inc_ref(self):
        """Use to control when to remove the Transition Layout"""
        self.ref_count = self.ref_count + 1

    def dec_ref(self):
        self.ref_count = self.ref_count - 1

    @property
    def render_angle(self):
        # The default angle to render the self-loop arc or when start and end states
        # are really close to each other
        return self._render_angle

    @render_angle.setter
    def render_angle(self, value):
        self._render_angle = int(value)

    @property
    def render_factor(self):
        return self._render_factor

    @render_factor.setter
    def render_factor(self, value):
        self._render_factor = int(value)

class StateType(Enum):
    NEUTRAL = 0
    NORMAL = 1
    UNCERTAIN = 2
    CERTAIN = 3

class State(Base):
    properties = [{'label': "Name", 'property': 'name', 'gtk_control': 'entry'},
                  {'label': "Marked", 'property': 'marked', 'gtk_control': 'checkbutton'},
                  {'label': "X", 'property': 'x', 'gtk_control': 'spinbutton'},
                  {'label': "Y", 'property': 'y', 'gtk_control': 'spinbutton'}]

    def __init__(self, name=None, marked=False, x=0, y=0, quantity=None, diagnoser_type=StateType.NEUTRAL, diagnoser_bad=False, *args, **kwargs):
        if name is None:
            if quantity is not None:
                name = str(quantity + 1)
            else:
                name = '?'
        self.name = name
        self.marked = marked
        self.diagnoser_type = diagnoser_type
        self.diagnoser_bad = diagnoser_bad
        self.x = x
        self.y = y
        self.in_transitions = set()
        self.out_transitions = set()
        self.transition_layouts = dict()  # maps a destination state, with the layout for all transitions in this ordened pair
        super().__init__(*args, **kwargs)

    def __str__(self):
        if self.marked:
            return "(" + self.name + ")"
        else:
            return "[" + self.name + "]"

    # -------------------------------- def __repr__(self):
    #         if self.marked:
    #             return "(" + self.name + ")"
    #         else:
    #             return "[" + self.name + "]"-------------

    def __repr__(self):
        if self.marked:
            return "(" + self.name + ")"
        else:
            return "[" + self.name + "]"

    def in_transition_exists(self, from_state, event):
        for transition in self.in_transitions:
            if (transition.from_state is from_state) and (transition.event is event):
                return True
        return False

    def out_transition_exists(self, to_state, event):
        for transition in self.out_transitions:
            if (transition.to_state is to_state) and (transition.event is event):
                return True
        return False

    def transition_in_add(self, transition):
        self.in_transitions.add(transition)

    def transition_out_add(self, transition):
        self.out_transitions.add(transition)
        if transition.to_state not in self.transition_layouts:
            self.transition_layouts[transition.to_state] = TransitionLayout()
        self.transition_layouts[transition.to_state].inc_ref()

    def transition_in_remove(self, transition):
        self.in_transitions.discard(transition)

    def transition_out_remove(self, transition):
        self.out_transitions.discard(transition)
        self.transition_layouts[transition.to_state]
        if self.transition_layouts[transition.to_state].ref_count == 0:
            del self.transition_layouts[transition.to_state]

    def get_target_from_event_name(self, event_name):
        for ot in self.out_transitions:
            if ot.event.name == event_name:
                return ot.to_state
        return None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def tex(self):
        return self._tex

    @tex.setter
    def tex(self, value):
        self._tex = str(value)

    @tex.deleter
    def tex(self):
        self._tex = self._name
        # deletes state, its output transitions and all transitions to it

    @property
    def marked(self):
        return self._marked

    @marked.setter
    def marked(self, value):
        self._marked = bool(value)

    @property
    def x(self):
        return self._x
        # deletes transitions which have state as destiny:

    @x.setter
    def x(self, value):
        self._x = int(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = int(value)

    @property
    def position(self):
        return (self.x, self.y)

    @position.setter
    def position(self, value):
        if isinstance(value, tuple) or isinstance(value, list):
            self.x = value[0]
            self.y = value[1]
        else:
            print("State.position tuple or list expected")


class Transition(Base):
    def __init__(self, from_state, to_state, event, *args, **kwargs):
        self.from_state = from_state
        self.to_state = to_state
        self.event = event
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{from_state:<8}, {event:<8} --> {to_state}".format(from_state=str(self.from_state), event=str(self.event), to_state=str(self.to_state))

    @property
    def from_state(self):
        return self._from_state

    @from_state.setter
    def from_state(self, value):
        if isinstance(value, State):
            self._from_state = value

    @property
    def to_state(self):
        return self._to_state

    @to_state.setter
    def to_state(self, value):
        if isinstance(value, State):
            self._to_state = value


    def __str__(self):
        return "{from_state}, {event} --> {to_state}".format(from_state=self.from_state, to_state=self.to_state, event=self.event)


class Automaton(Base):
    event_class = Event
    state_class = State
    transition_class = Transition
    type_str = 'FSA'

    def __init__(self, *args, **kwargs):
        self.events = set()
        self.states = set()
        self.initial_state = None

        # editor related attributes
        self._file_path_name = None
        self._name = None

        super().__init__(*args, **kwargs)

    def __str__(self):
        transitions = list()
        for s in self.states:
            transitions = transitions + list(s.out_transitions)
        return "Events: {events} \nStates: {states}\nInitial: {initial}\nTransitions:\n    {transitions}".format(
            events = ", ".join(map(lambda event: event.name, self.events)),
            states = "; ".join(map(str, self.states)),
            initial = str(self.initial_state),
            transitions = "\n    ".join(map(str, transitions)),
        )

    # --------------------------------------------------------------------------

    def get_file_name(self):
        if self._file_path_name is not None:
            return os.path.basename(self._file_path_name)
        return None
        
    def get_file_path_name(self):
        return self._file_path_name

    def get_name(self):
        if self._file_path_name is not None:
            return self.get_file_name()
        elif self._name is not None:
            return self._name
        return 'untitled'

    def set_file_path_name(self, file_path_name):
        self._file_path_name = file_path_name
        self._name = None 

    def set_name(self, name):
        if self._file_path_name is None:
            self._name = name

    # ------------------------------------------------------------------------ #
    # -------------------------- Event manipulation -------------------------- #
    # ------------------------------------------------------------------------ #

    def event_get_by_name(self, event_name):
        for event in self.events:
            if event.name == event_name:
                return event
        return None

    def event_name_exists(self, event_name):
        return self.event_get_by_name(event_name) is not None

    def event_add(self, *args, **kwargs):
        event = self.event_class(*args, **kwargs)
        if self.event_name_exists(event.name):
            raise EventNameDuplicateException
        self.events.add(event)
        return event

    def event_remove(self, event):
        if event not in self.events:
            return False
        for transition in list(event.transitions):  # list is a copy, avoiding Set changed size during iteration
            self.transition_remove(transition)
        self.events.remove(event)
        return True

    def event_remove_by_name(self, event_name):
        event = self.event_get_by_name(event_name)
        if event is None:
            return False
        return self.event_remove(event)


    def event_rename(self, event, new_event_name):
        if event.name == new_event_name:
            return False  #  This event's name is already event_name
        if self.event_name_exists(new_event_name):  # ANOTHER event is already named 'event_name'
            raise EventNameDuplicateException
        event.name = new_event_name
        return True

    def event_get_name_list(self):
        return {event.name for event in self.events}

    def event_name_map(self):
        """Returns a map (dict) relating events' names with their respective object"""
        event_map = dict()
        for event in self.events:
            event_map[event.name] = event
        return event_map

    def event_map(G1, G2):
        """Returns a (bi-directional) map (dict) relating events in G1 with events in G2 and vice versa based on events' names"""
        event_map = dict()
        G1_only_events = list()
        G2_only_events = list()
        G1_event_name_map = G1.event_name_map()
        G2_event_name_map = G2.event_name_map()

        for event_name, g1_event in G1_event_name_map.items():
            if event_name in G2_event_name_map:
                g2_event = G2_event_name_map[event_name]
                event_map[g1_event] = g2_event
                event_map[g2_event] = g1_event
            else:
                G1_only_events.append(g1_event)

        for event_name, g2_event in G2_event_name_map.items():
            if g2_event not in event_map:
                G2_only_events.append(g2_event)

        return event_map, G1_only_events, G2_only_events

    def check_equivalent_event_set(self, other):
        if len(self.events) != len(other.events):
            return False, None

        event_map, self_only_events, other_only_events = self.event_map(other)
        if len(self_only_events) != 0 or len(other_only_events) != 0:
            return False, None

        for event_a, event_b in event_map.items():
            if not event_a.equivalent_properties(event_b):
                return False, None

        return True, event_map

    # ------------------------------------------------------------------------ #
    # -------------------------- State manipulation -------------------------- #
    # ------------------------------------------------------------------------ #


    def state_add(self, *args, initial=False, **kwargs):
        quantity = len(self.states)
        s = self.state_class(*args, quantity=quantity, **kwargs)
        self.states.add(s)
        if initial:
            self.initial_state = s
        return s

    # TODO: test
    def state_remove(self, state):
        if self.initial_state == state:
            self.initial_state = None
        in_transitions = set()
        for r in state.in_transitions:
            in_transitions.add(r)
        out_transitions = set()
        for r in state.out_transitions:
            out_transitions.add(r)
        for transition in in_transitions:
            self.transition_remove(transition)
        for transition in out_transitions:
            self.transition_remove(transition)
        try:
            self.states.remove(state)
        except KeyError:
            return False
        else:
            if self.initial_state == state:
                self.initial_state = None
            return True

    @property
    def initial_state(self):
        return self._initial_state

    @initial_state.setter
    def initial_state(self, value):
        if isinstance(value, self.state_class) or (value is None):
            self._initial_state = value

    def transition_add(self, from_state, to_state, event, *args, **kwargs):
        # TODO: check if from_state, to_state, and event belong to self
        t = self.transition_class(from_state, to_state, event, *args, **kwargs)
        from_state.transition_out_add(t)
        to_state.transition_in_add(t)
        event.transition_add(t)
        return t

    # TODO: test
    def transition_remove(self, transition):
        transition.event.transitions.discard(transition)
        transition.from_state.transition_out_remove(transition)
        transition.to_state.transition_in_remove(transition)

    def state_rename_sequential(self):
        for _id, state in enumerate(self.states):
            state.name = str(_id)

    # Editor specific methods

    # These should be calculated by the renderer
    def state_get_at(self, x, y):
        pass

    def transition_get_at(self, x, y):
        pass

    def save(self, file_path_name=None):
        if file_path_name is None:
            if self._file_path_name is None:
                return False
            file_path_name = self._file_path_name
        else:
            self.set_file_path_name(file_path_name)

        f = open(file_path_name,'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<model version="0.0" type="FSA" id="Untitled">\n')
        f.write('<data>\n')

        state_to_id_map = dict()
        event_to_id_map = dict()

        for state_id, state in enumerate(self.states):
            state_to_id_map[state] = state_id
            initial = state == self.initial_state
            f.write(f'\t<state id="{state_id}" name="{state.name}" initial ="{initial}" marked="{state.marked}" x="{state.x}" y="{state.y}" />\n')

        for event_id, event in enumerate(self.events):
            event_to_id_map[event] = event_id
            f.write(f'\t<event id="{event_id}" name="{event.name}" controllable="{event.controllable}" observable="{event.observable}"/>\n')

        for source_state in self.states:
            for transition in source_state.out_transitions:
                source_state_id = state_to_id_map[transition.from_state]
                target_state_id = state_to_id_map[transition.to_state]
                event_id = event_to_id_map[transition.event]
                f.write(f'\t<transition source="{source_state_id}" target="{target_state_id}" event="{event_id}"/>\n')

        f.write('</data>\n')
        f.write("</model>\n")

        return True

    def load(self, file_path_name):
        self.set_file_path_name(file_path_name)

        def str2bool(_str):
            return (_str.lower() in ['true'])

        xml = parse(file_path_name).documentElement
        data_tag = xml.getElementsByTagName('data')[0]

        state_tags = data_tag.getElementsByTagName('state')
        event_tags = data_tag.getElementsByTagName('event')
        transition_tags = data_tag.getElementsByTagName('transition')

        id_to_state_map = dict()
        id_to_event_map = dict()

        for state_tag in state_tags:
            state_id = state_tag.getAttribute('id')
            name = state_tag.getAttribute('name')
            is_marked = str2bool(state_tag.getAttribute('marked'))
            is_initial = str2bool(state_tag.getAttribute('initial'))
            x = state_tag.getAttribute('x')
            y = state_tag.getAttribute('y')

            state = self.state_add(name, marked=is_marked, initial=is_initial, x=x, y=y)
            id_to_state_map[state_id] = state

        for event_tag in event_tags:
            event_id = event_tag.getAttribute('id')
            name = event_tag.getAttribute('name')
            is_observable = str2bool(event_tag.getAttribute('observable'))
            is_controllable = str2bool(event_tag.getAttribute('controllable'))

            event = self.event_add(name, observable=is_observable, controllable=is_controllable)
            id_to_event_map[event_id] = event

        for transition_tag in transition_tags:
            event_id = transition_tag.getAttribute('event')
            source_state_id = transition_tag.getAttribute('source')
            target_state_id = transition_tag.getAttribute('target')
            event = id_to_event_map[event_id]
            source_state = id_to_state_map[source_state_id]
            target_state = id_to_state_map[target_state_id]
            self.transition_add(source_state, target_state, event)

        return self


    def ides_import(self, file_path_name, load_layout=True):
        self.set_file_path_name(None)  # check rule

        xml = parse(file_path_name).documentElement
        data_tag = xml.getElementsByTagName('data')[0]

        state_tags = data_tag.getElementsByTagName('state')
        event_tags = data_tag.getElementsByTagName('event')
        transition_tags = data_tag.getElementsByTagName('transition')

        meta_tag = xml.getElementsByTagName('meta')[0]
        meta_state_tags = meta_tag.getElementsByTagName('state')

        id_to_state_map = dict()
        id_to_event_map = dict()

        for state_tag in state_tags:
            name = state_tag.getElementsByTagName('name')[0].childNodes[0].data
            state_id = state_tag.getAttribute('id')

            # getElementsByTagName: returns a list of all descendant elements (not direct children only) with the specified tag name
            # bool of a list returns False if empty list, True otherwise
            is_initial = bool(state_tag.getElementsByTagName('initial'))
            is_marked = bool(state_tag.getElementsByTagName('marked'))

            s = self.state_add(name, marked=is_marked, initial=is_initial)
            id_to_state_map[state_id] = s

        for meta_state_tag in meta_state_tags:  # layout
            state_id = meta_state_tag.getAttribute('id')
            circle_tag = meta_state_tag.getElementsByTagName("circle")[0]
            x = int(float(circle_tag.getAttribute('x')))
            y = int(float(circle_tag.getAttribute('y')))
            id_to_state_map[state_id].x = x
            id_to_state_map[state_id].y = y

        for event_tag in event_tags:
            event_name = event_tag.getElementsByTagName('name')[0].childNodes[0].data
            event_id = event_tag.getAttribute('id')
            is_observable = bool(event_tag.getElementsByTagName('observable'))
            is_controllable = bool(event_tag.getElementsByTagName('controllable'))
            event = self.event_add(event_name, observable=is_observable, controllable=is_controllable)
            id_to_event_map[event_id] = event

        for transition_tag in transition_tags:
            event_id = transition_tag.getAttribute('event')
            source_state_id = transition_tag.getAttribute('source')
            target_state_id = transition_tag.getAttribute('target')
            event = id_to_event_map[event_id]
            source_state = id_to_state_map[source_state_id]
            target_state = id_to_state_map[target_state_id]
            self.transition_add(source_state, target_state, event)

        return self

    def ides_export(self, file_path_name):
        f = open(file_path_name,'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<model version="2.1" type="FSA" id="Untitled">\n')
        f.write('<data>\n')

        state_id_map = dict()
        event_id_map = dict()

        for state_id, state in enumerate(self.states):
            state_id_map[state] = state_id
            initial = state == self.initial_state
            if initial:
                f.write(f'\t<state id="{state_id+1}">\n \t\t<properties>\n \t\t\t<initial />\n \t\t\t<marked />\n \t\t</properties>\n \t\t<name>{state_id+1}</name>\n \t</state>\n')
            else:
                f.write(f'\t<state id="{state_id+1}">\n \t\t<properties>\n \t\t\t<marked />\n \t\t</properties>\n \t\t<name>{state_id+1}</name>\n \t</state>\n')

        for event_id, event in enumerate(self.events):
            event_id_map[event] = event_id
            if event.controllable == True:
                f.write(f'\t<event id="{event_id+1}">\n \t\t<properties>\n \t\t\t<controllable />\n \t\t\t<observable />\n \t\t</properties>\n \t\t<name>{event.name}</name>\n \t</event>\n')
            else:
                f.write(f'\t<event id="{event_id+1}">\n \t\t<properties>\n \t\t\t<observable />\n \t\t</properties>\n \t\t<name>{event.name}</name>\n \t</event>\n')

        for source_state in self.states:
            for transition_id, transition in enumerate(source_state.out_transitions):
                source_id = state_id_map[transition.from_state]
                target_id = state_id_map[transition.to_state]
                event_id = event_id_map[transition.event]
                f.write(f'\t<transition id="{transition_id+1}" source="{source_id}" target="{target_id}" event="{event_id}">\n \t</transition>\n')

        f.write('</data>\n')
        f.write('<meta tag="layout" version="2.1">\n')
        meta_id_map=dict()
        for state in self.states:
            state_id = state_id_map[state]
            initial = state == self.initial_state
            f.write(f'\t<state id="{state_id+1}">\n \t\t<circle r="18.0" x="{state.x}" y="{state.y}" />\n \t</state>\n')

        f.write('</meta>\n')
        f.write("</model>\n")

    def grail_import(self, file_path_name, ncont_name):
        self.set_file_path_name(None)  # check rule

        f = open(file_path_name, 'r')
        ncont = open(ncont_name, 'r')
        initial_state_name = None

        state_name_to_state_map = dict()
        event_name_to_event_map = dict()
        marked_states = set()
        uncontrollable_events = set()
        state_indexes = [0, 2]

        for line in ncont:
            if re.search(r'(START)', line) == None and re.search(r'(FINAL)', line) == None:
                uncontrollable_events.add(re.split(r' ', line)[1].strip('\n'))

        for line in f:
            if re.search(r'(FINAL)', line) != None:
                l = re.split(r' ', line)
                marked_states.add(l[0])
            elif re.search(r'(START)', line) != None:
                initial_state_name = re.split(r' ', line)[2].strip('\n')

        f = open(file_path_name, 'r')
        for line in f:
            if re.search(r'(FINAL)', line) is not None:
                break
            elif re.search(r'(START)', line) is not None:
                pass
            elif initial_state_name is not None:
                l = re.split(r' ', line)
                for each in state_indexes:
                    state = set()
                    s = l[each].strip('\n')
                    state.add(s)
                    if s not in state_name_to_state_map.keys():
                        init = False
                        markd = False
                        if initial_state_name == s:
                            init = True
                        if state.issubset(marked_states):
                            markd = True
                        state_name_to_state_map[s] = self.state_add(s, marked=markd, initial=init)
                if l[1] not in event_name_to_event_map.keys():
                    ev_name = set()
                    ev_name.add(l[1])
                    controllable = True
                    if ev_name.issubset(uncontrollable_events):
                        controllable = False
                    event_name_to_event_map[l[1]] = self.event_add(l[1], controllable, True)
                self.transition_add(state_name_to_state_map[l[0].strip('\n')], state_name_to_state_map[l[2].strip('\n')], event_name_to_event_map[l[1]])
        return self

    def grail_export(self, file_path_name):
        pass

    def tct_import(self, file_path_name):
        f = open(file_path_name, 'r')
        initial_state_name = None

        state_name_to_state_map = dict()
        event_name_to_event_map = dict()
        marked_states = set()
        state_indexes = [0, 2]

        for line in f:
            if re.search(r'(FINAL)', line) != None:
                l = re.split(r' ', line)
                marked_states.add(l[0])
            elif re.search(r'(START)', line) != None:
                initial_state_name = re.split(r' ', line)[2].strip('\n')

        f = open(file_path_name, 'r')
        for line in f:
            if re.search(r'(FINAL)', line) is not None:
                break
            elif re.search(r'(START)', line) is not None:
                pass
            elif initial_state_name is not None:
                l = re.split(r' ', line)
                for each in state_indexes:
                    state_name = l[each].strip('\n')
                    if state_name not in state_name_to_state_map.keys():
                        init = False
                        markd = False
                        if initial_state_name == state_name:
                            init = True
                        if marked_states.issubset(state_name):
                            markd = True
                        state_name_to_state_map[state_name] = self.state_add(state_name, marked=markd, initial=init)
                if l[1] not in event_name_to_event_map.keys():
                    controllable = True
                    if not l[1]%2:
                        controllable = False
                    event_name_to_event_map[l[1]] = self.event_add(l[1], controllable, True)
                self.transition_add(state_name_to_state_map[l[0].strip('\n')], state_name_to_state_map[l[2].strip('\n')], event_name_to_event_map[l[1]])
        return self

    def tct_export(self, file_path_name):
        pass

    # Basic operations (e.g., sync, supC)

    def clone(self):
        return self.copy()


    def detect_accessible_state(self):
        states_dict = dict()
        states_stack = list()

        states_number = 0
        accessible_states = 0

        for state in self.states:
            states_dict[state] = False
            states_number += 1

        if self.initial_state is not None:
            states_stack.append(self.initial_state)
            states_dict[self.initial_state] = True

        """Detect non-accessible states"""
        while len(states_stack) != 0:
            accessible_states += 1
            state = states_stack.pop()
            for transition in state.out_transitions:
                if states_dict[transition.to_state] == False:
                    states_dict[transition.to_state] = True
                    states_stack.append(transition.to_state)

        return states_dict, states_number, accessible_states


    def is_accessible(self):
        states_dict, states_number, accessible_states = self.detect_accessible_state()
        return states_number == accessible_states

    def accessible(self, inplace=False):
        if not inplace:
            pass
            """
            TODO: create non-inplace version (adding states rather than
            copy everythin and then removing
            """
        self = self.copy()

        states_dict, states_number, accessible_states = self.detect_accessible_state()

        if(accessible_states == states_number):
            return self

        non_acessible_states_set = set()
        """Remove non-acessible states"""
        for state, is_accessible in states_dict.items():
            if is_accessible == False:
                non_acessible_states_set.add(state)

        for each in non_acessible_states_set:
            self.state_remove(each)

        return self

    def is_coaccessible(self):
        states_dict, states_number, coaccessible_states = self.detect_coaccessible_state()
        return states_number == coaccessible_states

    def detect_coaccessible_state(self):
        states_dict = dict()
        states_marked_stack = list()

        states_number = 0
        coaccessible_states = 0
        marked_states = 0

        for state in self.states:
            states_dict[state] = state.marked
            if state.marked:
                states_marked_stack.append(state)
                marked_states += 1
            states_number += 1

        while len(states_marked_stack) != 0:
            coaccessible_states += 1
            state = states_marked_stack.pop()
            for transition in state.in_transitions:
                if states_dict[transition.from_state] == False:
                    states_dict[transition.from_state] = True
                    states_marked_stack.append(transition.from_state)

        return states_dict, states_number, coaccessible_states

    def coaccessible(self, inplace=False):
        if not inplace:
            pass
            """
            TODO: create non-inplace version (adding states rather than
            copy everythin and then removing
            """
        self = self.copy()

        states_dict, states_number, coaccessible_states = self.detect_coaccessible_state()

        if (coaccessible_states == states_number):
            return self

        non_coacessible_state_set = set()
        """Remove non-coacessible states"""
        for state, is_coaccessible in states_dict.items():
            if is_coaccessible == False:
                non_coacessible_state_set.add(state)

        for each in non_coacessible_state_set:
            self.state_remove(each)

        return self

    def trim(self, copy=False):
        return self.coaccessible(copy).accessible()

    def non_coaccessible_states_join(self):
        pass

    def selfloop(self, event_set):
        pass

    def _merge_events(self, *args):
        "Add events from *args into self, self may already have events"
        event_names = {event.name for event in self.events}  # set, initiate with events' names already in self
        added_events = list()  # so we can undo in case of error
        for g in args:
            for g_event in g.events:
                if g_event.name not in event_names:
                    new_event = g_event.copy()
                    self.events.add(new_event)
                    added_events.append(new_event)
                    event_names.add(g_event.name)
                else:
                    pass  # TODO (1) check if g_event and self.get_event_by_name(g_event.name) are equivallent (method in Event) - controlabilly, observabilitty
                    #      (2) if not undo previously added events (from added_events)
                    #      (3) raise Error ErrorMultiplePropetiesForEventName

    def synchronization(*args, output_univocal=False):
        """ This function returns the accessible part of the synchronous composition. Instead of calculating all composed
            states and then calculate the accessible part, we only add accessible states to the output."""

        if len(args) < 2:
            return

        G = args[0].__class__()  # function output

        G._merge_events(*args)

        state_stack = list()
        state_map = dict()  # maps tuple of states (from args) to respective state in G

        def G_state_add(state_tuple, initial=False):
            state_type_counter = dict()
            for type in StateType: state_type_counter[type] = 0
            diag_type = StateType.NEUTRAL

            marked = functools.reduce(lambda val, s: val and s.marked, state_tuple, True)
            state_name = ",".join(state.name for state in state_tuple)
            diag_bad = functools.reduce(lambda val, s: s.diagnoser_bad, state_tuple, True)
            for state in state_tuple:
                state_type_counter[state.diagnoser_type] += 1
            if state_type_counter[StateType.NEUTRAL] < len(state_tuple):
                if (state_type_counter[StateType.NEUTRAL] + state_type_counter[StateType.NORMAL]) == len(state_tuple): #only neutral and normal
                    diag_type = StateType.NORMAL
                elif (state_type_counter[StateType.NEUTRAL] + state_type_counter[StateType.CERTAIN]) == len(state_tuple): #only neutral and certain
                    diag_type = StateType.CERTAIN
                else:
                    diag_type = StateType.UNCERTAIN
            s = G.state_add(state_name, initial=initial, marked=marked, diagnoser_type=diag_type, diagnoser_bad=diag_bad)
            state_map[state_tuple] = s
            state_stack.append(state_tuple)
            return s

        init_state_tuple = tuple(state.initial_state for state in args)
        G_state_add(init_state_tuple, True)

        while len(state_stack) != 0:
            state_tuple = state_stack.pop()
            source_state = state_map[state_tuple]
            for event in G.events:
                enabled = True
                target_state_tuple = list()
                for g, s in zip(args, state_tuple):
                    if g.event_name_exists(event.name):
                        target = s.get_target_from_event_name(event.name)
                        if target is None:  # forbidden, so no transition with 'event'
                            enabled = False
                            break
                        target_state_tuple.append(target)
                    else:  # 'event' not in 'g', stay in s
                        target_state_tuple.append(s)
                if enabled:
                    target_state_tuple = tuple(target_state_tuple)
                    if target_state_tuple not in state_map:
                        target_state = G_state_add(target_state_tuple, False)
                    else:
                        target_state = state_map[target_state_tuple]
                    G.transition_add(source_state, target_state, event)
        return G

    def product(self, *args):
        pass

    def projection(self, *args):
        pass

    def univocal(G, R, return_status=False):
        equivalent_events, event_map = G.check_equivalent_event_set(R)
        if not equivalent_events:
            raise Exception   # TODO: custom error that can be catch by application

        univocal_map = {R.initial_state: G.initial_state} # [state in R] to [state in G]
        state_stack = [(R.initial_state, G.initial_state)]
        status = True

        while len(state_stack) > 0:
            s_r, s_g = state_stack.pop()
            for trans_r in s_r.out_transitions:
                t_g = s_g.get_target_from_event_name(event_name)
                if trans_r.to_state not in univocal_map:
                    event_name = trans_r.event.name
                    t_r = trans_r.to_state
                    univocal_map[t_r] = t_g
                    if t_g is not None:
                        state_stack.append((t_r, t_g))
                    else:
                        status = False
                else:
                    if univocal_map[trans_r.to_state] == t_g:
                        status = False
        if return_status:
            return univocal_map, status
        else:
            return univocal_map

    def bad_states(G, R):
        univocal_map = G.univocal(R)
        bad_states = set()

        # TODO ...

        return bad_states


    def sup_c(G, R, univocal_map=None):
        # Look for Bad States in R.
        # If there aren t any, Sup = R
        # If there are, remove bad states from R
        # Calculate TRIM and back to step 1

        sup = R.copy()
        flag_bad_state = True
        set_bad_state = set()
        visited_states_set = set()
        univ_map = G.univocal(sup)
        states_to_be_visited_in_R = list()
        states_to_be_visited_in_R.append(sup.initial_state)

        while flag_bad_state:
            flag_bad_state = False
            flag_end = True
            state_in_R = states_to_be_visited_in_R.pop()

            while flag_end:
                for g_transition in univ_map[state_in_R].out_transitions:
                    r_event_set = set()

                    for r_transition in state_in_R.out_transitions:
                        r_event_set.add(r_transition.event.name)

                    for r_transition in state_in_R.out_transitions:
                        if g_transition.event.name not in r_event_set:
                            if not g_transition.event.controllable:
                                set_bad_state.add(state_in_R)
                                flag_bad_state = True
                        else:
                            next_state = r_transition.to_state
                            if next_state not in visited_states_set:
                                visited_states_set.add(state_in_R)
                                states_to_be_visited_in_R.append(next_state)
                try:
                    state_in_R = states_to_be_visited_in_R.pop()
                except IndexError:
                    flag_end = False

            if flag_bad_state:
                for state in set_bad_state:
                    sup.state_remove(state)
                set_bad_state = set()
                flag_bad_state = False

        sup.trim()

        return sup

    def choice_problem_check(self):
        pass

    def avalanche_effect_check(self):
        pass

    def inexact_synchronization_check(self):
        pass

    def simultaneity_check(self):
        pass

    def empty_closure(self):
        pass

    def determinize(self):

        state_map = dict()
        state_stack = list()
        state_list = list()

        def get_transition_function(list_of_states):
            transition_function = dict()
            for state in list_of_states:
                for transition in state.out_transitions:
                    if transition.event not in transition_function.keys():
                        transition_function[transition.event] = list()
                    transition_function[transition.event].append(transition.to_state)
            return transition_function

        def state_add(state_list, initial=False):
            if len(state_list) > 1:
                new_transitions_map = dict()
                target_state_tuple = tuple(state_list)
                marked = functools.reduce(lambda val, s: val and s.marked, target_state_tuple, True)
                state_name = ",".join(state.name for state in target_state_tuple)
                s = self.state_add(state_name, initial=initial, marked=marked)
                for item in state_list:
                    new_transitions_map[item] = s
            else:
                s = state_list[0]
            state_stack.append(s)
            state_map[s] = state_list
            return s

        state_list.append(self.initial_state)
        state_map[self.initial_state] = state_list
        state_stack.append(self.initial_state)

        while len(state_stack) > 0:
            state = state_stack.pop()
            tf = get_transition_function(state_map[state])
            for event in tf.keys():
                state_list = list()
                for target_state in tf[event]:
                    if target_state not in state_list:
                        state_list.append(target_state)
                if state_list not in state_map.values():
                    state_add(state_list, False)

        #for removable in new_transitions_map.keys():
        #    for transition in removable.in_transitions:
        #        if transition.event.observable:
        #            self.transition_add(transition.from_state, new_transitions_map[removable], transition.event)
        #    for transition in removable.out_transitions:
        #        if transition.event.observable:
        #            self.transition_add(new_transitions_map[removable], transition.to_state, transition.event)
        #    self.state_remove(removable)

        return self

    def complement(self, copy=False):
        pass

    def total(self, copy=False):
        pass

    def minimize(self, copy=False):

        # function calculates the out transition function of the state
        def get_transition_function(state):
            transition_function = dict()
            for transition in state.out_transitions:
                transition_function[transition.event.name] = transition.to_state
            return transition_function

        def transition_already_exists(from_state, to_state, event):
            for t in from_state.out_transitions:
                if t.to_state == to_state and t.event == event:
                    return True
            return False

        # list the events' names
        events_names = self.event_get_name_list()  # list of event's names
        # lists the states of the supervisor
        states = list(self.states)
        # half matrix: dict(frozenset of pair of states) = have or not have same marked attribute
        marked_matrix = dict()
        # creates a half matrix so we can relate all pairs of states
        can_be_equivalent_stack = list()
        # If marked_matrix = True, states are not equivalent
        for i in range(1, len(states)):
            for j in range(0, len(states) - 1):
                if states[i] != states[j]:
                    pair = frozenset((states[i], states[j]))
                    if states[i].marked != states[j].marked:
                        marked_matrix[pair] = True
                    else:
                        marked_matrix[pair] = False
                        can_be_equivalent_stack.append(pair)

        #now we are going to evaluate the transition functions of each unmarked pair
        #ToDo: Does this have to loop?
        while len(can_be_equivalent_stack) != 0:
            pair = can_be_equivalent_stack.pop()
            for event_name in events_names:
                target_states = set()
                for state in pair:
                    trans_function = get_transition_function(state)
                    try:
                        target_states.add(trans_function[event_name])
                    except KeyError:
                        pass
                try:
                    if marked_matrix[frozenset(target_states)] is True:
                        marked_matrix[pair] = True
                except KeyError:
                    pass

        equivalences = set()
        for state_1 in states:
            state_equivalences = set()
            state_equivalences.add(state_1)
            for state_2 in states:
                if state_1 != state_2:
                    pair = frozenset((state_1,state_2))
                    try:
                        if marked_matrix[pair] is False:
                            state_equivalences.add(state_2)
                    except KeyError:
                        pass
            if len(state_equivalences) > 1:
                if not state_equivalences.issubset(equivalences):
                    equivalences.add(frozenset(state_equivalences))

        states_to_remove = set()

        for eq in equivalences:
            state_name = ",".join(each.name for each in eq)
            is_initial = False
            for each in eq:
                if each == self.initial_state:
                    is_initial = True
                    break
            is_marked = False
            for each in eq:
                if each.marked:
                    is_marked = True
                    break
            equivalent_state = self.state_add(state_name, marked=is_marked, initial=is_initial)
            for state in self.states:
                if state in eq:
                    for transition in state.in_transitions:
                        if transition.from_state == transition.to_state and not transition_already_exists(
                                equivalent_state, equivalent_state, transition.event):
                            self.transition_add(equivalent_state, equivalent_state, transition.event)
                        elif not transition_already_exists(transition.from_state, equivalent_state, transition.event):
                            self.transition_add(transition.from_state, equivalent_state, transition.event)
                    for transition in state.out_transitions:
                        if transition.from_state == transition.to_state and not transition_already_exists(
                                equivalent_state, equivalent_state, transition.event):
                            self.transition_add(equivalent_state, equivalent_state, transition.event)
                        elif not transition_already_exists(equivalent_state, transition.to_state, transition.event):
                            self.transition_add(equivalent_state, transition.to_state, transition.event)
                    states_to_remove.add(state)

        for each in states_to_remove:
            self.state_remove(each)

        return self

    def mask(self, masks, copy=False):
        pass

    def distinguish(self, refinements, copy=False):
        pass

    def isomorphic_check(G1, G2, verbose=False):
        if len(G1.states) != len(G2.states):
            if verbose:
                print("Number of states: {} != {}".format(len(G1.states), len(G2.states)))
            return False

        equivalent_events, event_map = G1.check_equivalent_event_set(G2)
        if not equivalent_events:
            if verbose:
                print("Events are not equivalent")
            return False

        state_map = {G1.initial_state: G2.initial_state}
        state_stack = [(G1.initial_state, G2.initial_state)]

        while len(state_stack) > 0:
            s_g1, s_g2 = state_stack.pop()
            if len(s_g1.out_transitions) != len(s_g2.out_transitions):
                if verbose:
                    print("Diferent number of transitions", s_g1, s_g2)
                return False
            for trans_g1 in s_g1.out_transitions:
                event_name = trans_g1.event.name
                target_g1 = trans_g1.to_state
                target_g2 = s_g2.get_target_from_event_name(event_name)  # may be None
                if target_g2 is None:
                    if verbose:
                        print("Transition in G1", trans_g1, "undefined in G2")
                    return False
                elif target_g1 not in state_map:  # OK
                    state_map[target_g1] = target_g2
                    state_stack.append((target_g1, target_g2))
                elif state_map[target_g1] != target_g2:
                    if verbose:
                        print("Not univocal transition:", trans_g1, "|", s_g2, ",", event_name, "-->", target_g2)
                        print("State map", state_map)
                    return False

        return True

    def supervisor_reduction(self, G, criteria):
        univ_map, univocal_status = G.univocal(self, return_status=True)
        if univocal_status == False:
            print('G is not univocal for self')
        control_cover_dict = dict()
        control_cover_state = set()
        state_stack = list()

        #============Private Functions

        # this function returns the set of disabled events in the supervisor
        def get_disabled_events(sup_state):
            enabled_events_in_supervisor = set()
            enabled_events_in_system = set()
            disabled_events = set()

            for transition in sup_state.out_transitions:
                enabled_events_in_supervisor.add(transition.event.name)

            for transition in univ_map[sup_state].out_transitions:
                enabled_events_in_system.add(transition.event.name)

            for event_name in enabled_events_in_system:
                if event_name not in enabled_events_in_supervisor:
                    disabled_events.add(event_name)

            return disabled_events

        # this function returns the set of enabled events in a state
        def get_enabled_events(state):
            enabled_events = set()

            for transition in state.out_transitions:
                enabled_events.add(transition.event.name)

            return enabled_events

        # marked attribute, A(x) Def 4.1
        # T(x) if the univocal state in the plant is marked
        # M(x) if the state in the supervisor is marked
        # returns 1 if T(x) = 1 AND M(x) = 1,
        # returns 0 if T(x) = 0,
        # return -1 if T(x) = 1 AND M(x) = 0
        # T(x) refers to plant G and M(x) refers to supervisor S
        def get_marked_attribute(sup_state):
            if univ_map[sup_state].marked is False:
                return 0
            else:
                if sup_state.marked is True:
                    return 1
                else:
                    return -1

        # Def 4.2 item 2
        def get_marked_action_attribute(x1, x2):
            mx1 = get_marked_attribute(x1)
            mx2 = get_marked_attribute(x2)
            #~ if (mx1 == mx2) or ((mx1 == 0) and (mx2 != 0)) or ((mx2 == 0) and (mx1 != 0)):
            if (mx1 == mx2) or (mx1 == 0) or (mx2 == 0):
                return True
            else:
                return False

        def verify_aggretation(s1, s2):
            count = 0  # TODO: remove
            for state_1 in s1:
                for state_2 in s2:
                    if state_1 != state_2:
                        try:
                            if len(aggregate_matrix[frozenset((state_1, state_2))]) == 0:
                                count = count + 1
                        except:
                            pass  # False
                    else:  # TODO: remove
                        count = count + 1  # TODO: remove
            return count  # True

        # function calculates the out transition function of the state
        def get_transition_function(state):
            transition_function = dict()
            for transition in state.out_transitions:
                transition_function[transition.event.name] = transition.to_state
            return transition_function

        def a_size_criteria(aggregation_indexes, states, current):
            var = False
            cell_sizes = dict()
            sizes = list()
            for j in aggregation_indexes:
                cell_sizes[len(control_cover_dict[j])] = j
                sizes.append(len(control_cover_dict[j]))

            chosen_cell = cell_sizes[max(sizes)]
            if current == control_cover_dict[chosen_cell]:
                var =True

            for state in states:
                if state not in control_cover_dict[chosen_cell]:
                    control_cover_dict[chosen_cell].add(state)

            state_stack.append(control_cover_dict[chosen_cell])
            return var

        def b_min_dependancies_criteria(aggregation_indexes, states):
            pass

        def c_target_state_intersection_criteria(aggregation_indexes, states):
            intersection_dict = dict()
            intersections = list()
            for j in aggregation_indexes:
                intersection_dict[frozenset(control_cover_dict[j].intersection(states))] = j
                intersections.append(control_cover_dict[j].intersection(states))

            chosen_cell = intersection_dict[frozenset(max(intersections))]
            for state in states:
                if state not in control_cover_dict[chosen_cell]:
                    control_cover_dict[chosen_cell].add(state)

            state_stack.append(control_cover_dict[chosen_cell])
            pass

        def d_future_agregation_criteria():
            pass

        def e_random_criteria(aggregation_indexes, states):
            chosen_cell = random.choice(aggregation_indexes)

            for each in states:
                if each not in control_cover_dict[chosen_cell]:
                    control_cover_dict[chosen_cell].add(each)
            state_stack.append(control_cover_dict[chosen_cell])
            pass

        # key is tuple, value is new state
        def Sr_state_add(state_tuple, initial=False):
            marked = functools.reduce(lambda val, s: val and s.marked, state_tuple, True)
            state_name = ",".join(state.name for state in state_tuple)
            s = Sr.state_add(state_name, initial=initial, marked=marked)
            sr_state_map[state_tuple] = s

        def is_cell_covered(dictionary, cell):
            if len(cell) == 0:
                return True
            else:
                for j in range(0, len(dictionary)):
                    if control_cover_state.issubset(dictionary[j]):
                        # there is already a control cover that has this set, do nothing
                        return True
                return False

        def get_possible_aggregation_indexes(dictionary, cell):
            indexes = list()
            for j in range(0, len(dictionary)):
                cnt = verify_aggretation(cell, dictionary[j])
                if cnt == len(dictionary[j]) * len(cell):
                    # aggregation is possible, store the index of control cover to decide later on the criteria
                    indexes.append(j)
            return indexes

        aggregate_stack = list()
        # lists the states of the supervisor
        states = list(self.states)
        # half matrix: dict(frozenset of pair of states) = relatable, not relatable or dependancy
        aggregate_matrix = dict()
        # creates a half matrix so we can relate all pairs of states
        for i in range(1, len(states)):
            for j in range(0, len(states) - 1):
                if states[i] != states[j]:
                    pair = frozenset((states[i], states[j]))
                    # Condition 1: E(x1) Intersection D(x2) = 0 AND E(x2) Intersection D(x1) = 0
                    if (len(get_enabled_events(states[i]).intersection(get_disabled_events(states[j]))) == 0) and (len(get_enabled_events(states[j]).intersection(get_disabled_events(states[i]))) == 0):
                        # Marked Criteria - Sivolella def 4.1
                        if get_marked_action_attribute(states[i], states[j]) is True:
                            # Condition 3: Looking for dependancies
                            common_transitions = get_enabled_events(states[i]).intersection(get_enabled_events(states[j]))
                            if len(common_transitions) == 0:
                                aggregate_matrix[pair] = set()
                                aggregate_stack.append(pair)
                            else:
                                i_transition_function_dict = dict()
                                for transition in states[i].out_transitions:
                                    i_transition_function_dict[transition.event.name] = transition.to_state
                                j_transition_function_dict = dict()
                                for transition in states[j].out_transitions:
                                    j_transition_function_dict[transition.event.name] = transition.to_state
                                dependancies = set()
                                for each in common_transitions:
                                    target_pair = frozenset((i_transition_function_dict[each], j_transition_function_dict[each]))
                                    if target_pair != pair and len(target_pair) == 2:
                                        dependancies.add(frozenset((i_transition_function_dict[each], j_transition_function_dict[each])))
                                aggregate_matrix[pair] = dependancies
                                if len(dependancies) == 0:
                                    aggregate_stack.append(pair)

        while len(aggregate_stack) > 0:
            pair = aggregate_stack.pop()
            for each in aggregate_matrix.keys():
                debug_1 = aggregate_matrix[each]
                if pair in debug_1:
                    aggregate_matrix[each].remove(pair)
                    if len(aggregate_matrix[each]) == 0:
                        aggregate_stack.append(each)

        # Control Cover
        # creates first control cover cell with supervisor's initial state
        control_cover_state.add(self.initial_state)
        control_cover_dict[0] = control_cover_state
        state_stack.append(control_cover_state)
        while len(state_stack) != 0:
            #current is one element of control_cover_dict (a control cover cell)
            current_cell_updated = False
            current = state_stack.pop(0)
            for event_name in self.event_get_name_list():
                control_cover_state = set()
                for state in current:
                    trans_function = get_transition_function(state)
                    try:
                        control_cover_state.add(trans_function[event_name])
                    except KeyError:
                        pass
                # at this point control_cover_state holds a set with the destiny states
                # decide if there is already a control cover that has this set, if not, create it
                if not is_cell_covered(control_cover_dict, control_cover_state):
                    possible_aggregation_indexes = get_possible_aggregation_indexes(control_cover_dict, control_cover_state)
                    # if target states cant be aggregated in any existing cells
                    if len(possible_aggregation_indexes) == 0:
                        control_cover_dict[len(control_cover_dict)] = control_cover_state
                        state_stack.append(control_cover_state)
                    else:
                        # aggregate based on the criteria given
                        #current_cell_updated = True
                        if criteria == 'b':
                            b_min_dependancies_criteria()
                        elif criteria == 'c':
                            c_target_state_intersection_criteria(possible_aggregation_indexes, control_cover_state)
                        elif criteria == 'd':
                            d_future_agregation_criteria()
                        elif criteria == 'e':
                            e_random_criteria(possible_aggregation_indexes, control_cover_state)
                        else: #if 'a' but also default
                            current_cell_updated = a_size_criteria(possible_aggregation_indexes, control_cover_state, current)
                if current_cell_updated is True:
                    break

        Sr = Automaton()
        sr_state_map = dict()
        sr_event_map = dict()
        for key in control_cover_dict:
            state_tuple = tuple(state for state in control_cover_dict[key])
            Sr_state_add(state_tuple, True if key == 0 else False)

        for event_name in self.event_get_name_list():
            sr_event_map[event_name] = Sr.event_add(event_name, True, True)

        for each in sr_state_map:
            for event_name in Sr.event_get_name_list():
                target_states = set()
                for state in each:
                    t_function = get_transition_function(state)
                    try:
                        target_states.add(t_function[event_name])
                    except:
                        pass
                for state in sr_state_map:
                    if target_states.issubset(set(state)) and len(target_states) > 0:
                        Sr.transition_add(sr_state_map[each], sr_state_map[state], sr_event_map[event_name])
                        break

        return (Sr)

    def get_unobservable_range(self):

        unobservable_range_dict = dict()
        state_stack = list()
        for state in self.states:
            state_stack.append(state)

        while len(state_stack) > 0:
            state = state_stack.pop()
            unobservable_range_dict[state] = list()
            range_stack = list()
            range_stack.append(state)
            while len(range_stack) > 0:
                s = range_stack.pop()
                for transition in s.out_transitions:
                    if transition.event.observable == False:
                        if transition.to_state not in unobservable_range_dict[state]:
                            unobservable_range_dict[state].append(transition.to_state)
                            range_stack.append(transition.to_state)

        return unobservable_range_dict

    def get_transition_function(self, state):

        transition_function = dict()

        for transition in state.out_transitions:
            transition_function[transition.event] = list()

        for transition in state.out_transitions:
            transition_function[transition.event].append(transition.to_state)

        return transition_function

    def observer(self):

        observer = Automaton()
        observer_event_dict = dict()
        observer_state_dict = dict()

        unobservable_range_dict = self.get_unobservable_range()
        state_stack = list()
        state_list = list()
        state_list.append(self.initial_state)
        state_stack.append(state_list)

        def merge_states(state_list):

            is_initial = False
            normal_state_counter = 0
            certain_state_counter = 0
            uncertain_state_counter = 0
            diag_type = StateType.NORMAL

            state_tuple = tuple(state_list)
            is_marked = functools.reduce(lambda val, s: val and s.marked, state_tuple, True)
            if self.initial_state in state_list: is_initial = True
            diag_bad = functools.reduce(lambda val, s: val and s.diagnoser_bad, state_tuple, True)
            state_name = ",".join(state.name for state in state_tuple)
            for state in state_list:
                if state.diagnoser_type == StateType.NORMAL:
                    normal_state_counter += 1
                elif state.diagnoser_type == StateType.CERTAIN:
                    certain_state_counter += 1
                else:
                    uncertain_state_counter += 1
            if normal_state_counter < len(state_list):
                if certain_state_counter < len(state_list):
                    diag_type = StateType.UNCERTAIN
                else:
                    diag_type = StateType.CERTAIN
            if state_name not in observer_state_dict.keys():
                state_stack.append(state_list)  # adiciona estado de destino a stack
                observer_state_dict[state_name] = observer.state_add(state_name, initial=is_initial, marked=is_marked, diagnoser_type=diag_type, diagnoser_bad=diag_bad)
            return observer_state_dict[state_name]

        while len(state_stack) > 0:
            states_to_merge = list()
            current_state = state_stack.pop()
            for state in current_state:
                if state not in states_to_merge:
                    states_to_merge.append(state)
                if len(unobservable_range_dict[state]) > 0:
                    for each in unobservable_range_dict[state]:
                        if each not in states_to_merge:
                            states_to_merge.append(each)
            out_state = merge_states(states_to_merge)
            for event in self.events:
                if event.observable:
                    target_states = list()
                    for state in states_to_merge:
                        transition_function = self.get_transition_function(state)
                        if event in transition_function.keys():
                            for target in transition_function[event]:
                                if target not in target_states:
                                    target_states.append(target)
                    for state in target_states:
                        if len(unobservable_range_dict[state]) > 0:
                            for each in unobservable_range_dict[state]:
                                if each not in target_states:
                                    target_states.append(each)
                    if len(target_states) > 0:
                        in_state = merge_states(target_states) #cria estado de destino
                        if event.name not in observer_event_dict.keys(): #if not observer.has_event
                            observer_event_dict[event.name] = observer.event_add(event.name, event.controllable, event.observable)
                        if not out_state.out_transition_exists(in_state, observer_event_dict[event.name]):
                            observer.transition_add(out_state, in_state, observer_event_dict[event.name]) #define as transicoes de out para in

        return observer

    def labeller(self, fault_events):
        #this funtion receives a list of fault events.
        #one event only means that the faults are treated separately
        #two or more fault events means that the faults are treated together
        #ToDo: Do we need to create a copy?

        R = Automaton()
        N = R.state_add('N', initial=True, marked=False, diagnoser_type=StateType.NORMAL, diagnoser_bad=False)
        Y = R.state_add('F', initial=False, marked=False, diagnoser_type=StateType.CERTAIN, diagnoser_bad=False)
        for event in fault_events:
            f = R.event_add(event.name, event.controllable, event.observable)
            R.transition_add(N, Y, f)
            R.transition_add(Y, Y, f)

        return R

    def diagnoser(self, labeller):

        diag = self.synchronization(labeller).observer()

        return diag

    def safe_diag_label(self, ev, forbidden_string):
        #TODO
        pass

    def safe_diagnoser(self, rotulador):

        safe_diag = self.diag_label().synchronization(rotulador).observer()

        return safe_diag

    def get_fb(self):

        fb = list()
        bad_states = list()
        bad_state_backward_reach = dict()

        for state in self.states:
            if state.diagnoser_bad:
                bad_states.append(state)
                bad_state_backward_reach[state] = list()
                for transition in state.in_transitions:
                    if transition.from_state != state:
                        bad_state_backward_reach[state].append(transition.from_state)

        for state in bad_states:
            reach = len(bad_state_backward_reach[state])
            bad_backward_reach = 0
            for each in bad_state_backward_reach[state]:
                if each.diagnoser_bad:
                    bad_backward_reach += 1
            if reach == bad_backward_reach:
                break
            else:
                fb.append(state)

        return fb

    def state_has_diagnosis(self, state):

        if state.diagnoser_type == StateType.CERTAIN:
            return True
        else:
            return False

    def state_has_prognosis(self, state):

        visited = dict()

        for s in self.states:
            visited[s] = False

        def forward_recursive(self, state, visited):
            if visited[s] == True and state.diagnoser_type == StateType.UNCERTAIN:
                return False
            elif state.diagnoser_type == StateType.CERTAIN:
                return True
            else:
                visited[state] = True
                for t in state.out_transitions:
                    if not visited[t.to_state]:
                        if not forward_recursive(self, t.to_state, visited):
                            return False
                    else:
                        return False
            return True

        return forward_recursive(self, state, visited)

    def is_safe_controllable(self):

        fb = self.get_fb()

        def backward_recursive(self, state, visited):
            visited[state] = True
            if self.initial_state == state:
                return False
            for t in state.in_transitions:
                if t.event.controllable:
                    if self.state_has_diagnosis(t.from_state) or self.state_has_prognosis(t.from_state):
                        return True
                if not visited[t.from_state]:
                    if not backward_recursive(self, t.from_state, visited):
                        return False

            return True

        for bad_state in fb:
            visited = dict()
            for s in self.states:
                visited[s] = False
            if not backward_recursive(self, bad_state, visited):
                return False

        return True
