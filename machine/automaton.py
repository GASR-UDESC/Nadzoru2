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


class State(Base):
    def __init__(self, name=None, marked=False, x=0, y=0, quantity=None, *args, **kwargs):
        if name is None:
            if quantity is not None:
                name = str(quantity + 1)
            else:
                name = '?'
        self.name = name
        self.marked = marked
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

    # ---------------------------------------------

    def __repr__(self):
        if self.marked:
            return "(" + self.name + ")"
        else:
            return "[" + self.name + "]"

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
        #  self.events = set()
        self.events = dict()  # map event_name to event class, names must be unique!
        self.states = set()
        self.initial_state = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        transitions = list()
        for s in self.states:
            transitions = transitions + list(s.out_transitions)
        return "Events: {events} \nStates: {states}\nInitial: {initial}\nTransitions:\n    {transitions}".format(
            events = ", ".join(map(str, self.events)),
            states = "; ".join(map(str, self.states)),
            initial = str(self.initial_state),
            transitions = "\n    ".join(map(str, transitions)),
        )
        # deletes transitions which have state as destiny:

    def event_add(self, *args, **kwargs):
        e = self.event_class(*args, **kwargs)
        if e.name in self.events:
            raise EventNameDuplicateException
        self.events[e.name] = e
        return e

    # TODO: test
    def event_remove_by_name(self, event_name):
        try:
            event = self.events[event_name]
            del self.events[event_name]
        except KeyError:
            return False

        for t in event.transitions:
            print("REMOVING", t)
            self.transition_remove(t)
        return True

    def event_remove(self, event):
        """event's name are unique"""
        return self.event_remove_by_name(event.name)

    def event_rename(self, event, event_name):
        # TODO improve: two sources of truth
        if event_name in self.events:
            raise EventNameDuplicateException

        del self.events[event.name]
        self.events[event_name] = event
        event.name = event_name

    def has_event_name(self, event_name):
        return event_name in self.events  # check if the event_name key exists in self.events

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

    # Editor specific methods

    # These should be calculated by the renderer
    """
    def state_get_at(self, x, y):
        pass

    def transition_get_at(self, x, y):
        pass

    def state_auto_position(self):  # OLD: position_states
        pass
    """

    def save(self, file_name):
        file = open(file_name,'w')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<model version="2.1" type="FSA" id="Untitled">\n')
        file.write('<data>\n')

        state_id_map = dict()
        event_id_map = dict()

        for _id, state in enumerate(self.states):
            state_id_map[state] = _id
            initial = state == self.initial_state
            file.write(f'\t<state id="{_id}" name="{state.name}" initial ="{initial}" marked="{state.marked}" x="{state.x}" y="{state.y}" />\n')

        for _id, event_name in enumerate(self.events.keys()):
            event = self.events[event_name]
            event_id_map[event] = _id
            file.write(f'\t<event id="{_id}" name="{event_name}" controllable="{event.controllable}" observable="{event.observable}"/>\n')

        for source_state in self.states:
            for transition in source_state.out_transitions:
                source_id = state_id_map[transition.from_state]
                target_id = state_id_map[transition.to_state]
                event_id = event_id_map[transition.event]
                file.write(f'\t<transition source="{source_id}" target="{target_id}" event="{event_id}"/>\n')

        file.write('</data>\n')
        file.write("</model>\n")

    def load(self, file_name):

        def str2bool(_str):
            return (_str.lower() in ['true'])

        xml = parse(file_name).documentElement
        data = xml.getElementsByTagName('data')[0]

        states = data.getElementsByTagName('state')
        events = data.getElementsByTagName('event')
        transitions = data.getElementsByTagName('transition')

        stateDict = dict()
        eventDict = dict()

        for state in states:
            _id = state.getAttribute('id')
            name = state.getAttribute('name')
            is_marked = str2bool(state.getAttribute('marked'))
            is_initial = str2bool(state.getAttribute('initial'))
            x = state.getAttribute('x')
            y = state.getAttribute('y')

            s = self.state_add(name, marked=is_marked, initial=is_initial, x=x, y=y)
            stateDict[_id] = s

        for event in events:
            _id = event.getAttribute('id')
            name = event.getAttribute('name')
            is_observable = str2bool(event.getAttribute('observable'))
            is_controllable = str2bool(event.getAttribute('controllable'))

            ev = self.event_add(name, observable=is_observable, controllable=is_controllable)
            eventDict[_id] = ev

        for transition in transitions:
            tEvent = transition.getAttribute('event')
            tSource = transition.getAttribute('source')
            tTarget = transition.getAttribute('target')
            ev = eventDict[tEvent]
            ss = stateDict[tSource]
            st = stateDict[tTarget]
            self.transition_add(ss, st, ev)

        return self


    def ides_import(self, file_name, load_layout=True):
        xml = parse(file_name).documentElement
        data = xml.getElementsByTagName('data')[0]

        states = data.getElementsByTagName('state')
        events = data.getElementsByTagName('event')
        transitions = data.getElementsByTagName('transition')

        meta = xml.getElementsByTagName('meta')[0]
        meta_states = meta.getElementsByTagName('state')

        stateDict = dict()
        eventDict = dict()

        for state in states:
            name = state.getElementsByTagName('name')[0].childNodes[0].data
            _id = state.getAttribute('id')

            # getElementsByTagName: returns a list of all descendant elements (not direct children only) with the specified tag name
            # bool of a list returns False if empty list, True otherwise
            is_initial = bool(state.getElementsByTagName('initial'))
            is_marked = bool(state.getElementsByTagName('marked'))

            s = self.state_add(name, marked=is_marked, initial=is_initial)
            stateDict[_id] = s

        for state in meta_states:  # layout
            _id = state.getAttribute('id')
            circle = state.getElementsByTagName("circle")[0]
            x = int(float(circle.getAttribute('x')))
            y = int(float(circle.getAttribute('y')))
            stateDict[_id].x = x
            stateDict[_id].y = y

        for event in events:
            name = event.getElementsByTagName('name')[0].childNodes[0].data
            _id = event.getAttribute('id')
            is_observable = bool(event.getElementsByTagName('observable'))
            is_controllable = bool(event.getElementsByTagName('controllable'))
            ev = self.event_add(name, observable=is_observable, controllable=is_controllable)
            eventDict[_id] = ev

        for transition in transitions:
            tEvent = transition.getAttribute('event')
            tSource = transition.getAttribute('source')
            tTarget = transition.getAttribute('target')
            ev = eventDict[tEvent]
            ss = stateDict[tSource]
            st = stateDict[tTarget]
            self.transition_add(ss, st, ev)

        return self

    def ides_export(self, file_name):
        pass

    def grail_import(self, file_name, ncont_name):
        file = open(file_name, 'r')
        ncont = open(ncont_name, 'r')
        initial_state_name = None

        stateDict = dict()
        eventDict = dict()
        marked_states = set()
        uncontrollable_events = set()
        state_indexes = [0, 2]

        for line in ncont:
            if re.search(r'(START)', line) == None and re.search(r'(FINAL)', line) == None:
                uncontrollable_events.add(re.split(r' ', line)[1].strip('\n'))

        for line in file:
            if re.search(r'(FINAL)', line) != None:
                l = re.split(r' ', line)
                marked_states.add(l[0])
            elif re.search(r'(START)', line) != None:
                initial_state_name = re.split(r' ', line)[2].strip('\n')

        file = open(file_name, 'r')
        for line in file:
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
                    if s not in stateDict.keys():
                        init = False
                        markd = False
                        if initial_state_name == s:
                            init = True
                        if state.issubset(marked_states):
                            markd = True
                        stateDict[s] = self.state_add(s, marked=markd, initial=init)
                if l[1] not in eventDict.keys():
                    ev_name = set()
                    ev_name.add(l[1])
                    controllable = True
                    if ev_name.issubset(uncontrollable_events):
                        controllable = False
                    eventDict[l[1]] = self.event_add(l[1], controllable, True)
                self.transition_add(stateDict[l[0].strip('\n')], stateDict[l[2].strip('\n')], eventDict[l[1]])
        return self

    def tct_import(self, file_name):
        file = open(file_name, 'r')
        initial_state_name = None

        stateDict = dict()
        eventDict = dict()
        marked_states = set()
        state_indexes = [0, 2]

        for line in file:
            if re.search(r'(FINAL)', line) != None:
                l = re.split(r' ', line)
                marked_states.add(l[0])
            elif re.search(r'(START)', line) != None:
                initial_state_name = re.split(r' ', line)[2].strip('\n')

        file = open(file_name, 'r')
        for line in file:
            if re.search(r'(FINAL)', line) is not None:
                break
            elif re.search(r'(START)', line) is not None:
                pass
            elif initial_state_name is not None:
                l = re.split(r' ', line)
                for each in state_indexes:
                    state = l[each].strip('\n')
                    if state not in stateDict.keys():
                        init = False
                        markd = False
                        if initial_state_name == state:
                            init = True
                        if marked_states.issubset(state):
                            markd = True
                        stateDict[state] = self.state_add(state, marked=markd, initial=init)
                if l[1] not in eventDict.keys():
                    controllable = True
                    if not l[1]%2:
                        controllable = False
                    eventDict[l[1]] = self.event_add(l[1], controllable, True)
                self.transition_add(stateDict[l[0].strip('\n')], stateDict[l[2].strip('\n')], eventDict[l[1]])
        return self

    def tct_import(self, file_name):
        pass

    def tct_export(self, file_name):
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
            for ev_name, ev in g.events.items():
                if ev.name not in event_names:
                    new_event = ev.copy()
                    self.events[new_event] = ev
                    added_events.append(new_event)
                    event_names.add(ev.name)
                else:
                    pass  # TODO (1) check if ev and self.get_event(ev.name) are equivallent (method in event)
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
            marked = functools.reduce(lambda val, s: val and s.marked, state_tuple, True)
            state_name = ",".join(state.name for state in state_tuple)
            s = G.state_add(state_name, initial=initial, marked=marked)
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
                    if g.has_event_name(event.name):
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

    def check_equal_event_set(self, other):
        for event_name in self.events:
            if not other.has_event_name(event_name):
                return False
        for event_name in other.events:
            if not self.has_event_name(event_name):
                return False
        return True

    def univocal(G, R):
        if G.check_equal_event_set(R) is False:
            raise Exception   # TODO: custom error that can be catch by application

        univocal_map = {R.initial_state: G.initial_state} # [state in R] to [state in G]
        state_stack = [(G.initial_state, R.initial_state)]

        while len(state_stack) > 0:
            s_g, s_r = state_stack.pop()
            for trans_r in s_r.out_transitions:
                if trans_r.to_state not in univocal_map:
                    event_name = trans_r.event.name
                    t_r = trans_r.to_state
                    t_g = s_g.get_target_from_event_name(event_name)
                    univocal_map[t_r] = t_g
                    state_stack.append((t_g, t_r))
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

    def determinize(self, copy=False):

        det_automaton = Automaton()
        det_automaton.state_add(self.initial_state.name, initial=True, marked=self.initial_state.marked)

        created_states_dict = dict()
        created_states_dict[det_automaton.initial_state.name] = det_automaton.initial_state

        state_stack = list()
        state_stack.append(det_automaton.initial_state.name)

        events_set = set()

        original_automaton_dict = dict()
        for state in self.states:
            original_automaton_dict[state.name] = state

        def get_transition_function(state, transition_function):
            for transition in original_automaton_dict[state.name].out_transitions:
                if transition.event in transition_function:
                    if not isinstance(transition_function[transition.event], list):
                        if transition_function[transition.event] != transition.to_state:
                            transition_function[transition.event] = [transition_function[transition.event]]
                            transition_function[transition.event].append(transition.to_state)
                else:
                    transition_function[transition.event] = transition.to_state
            return transition_function

        def determinize_state(state, from_state):
            transition_function = dict()
            if type(state) == frozenset:
                for each in state:
                    transition_function = get_transition_function(each, transition_function)
            else:
                transition_function = get_transition_function(state, transition_function)
            for key in transition_function.keys():
                if not isinstance(transition_function[key], list):
                    try:
                        next_state = created_states_dict[transition_function[key].name]
                    except KeyError:
                        next_state = det_automaton.state_add(transition_function[key].name, marked=transition_function[key].marked)
                        created_states_dict[next_state.name] = next_state
                        state_stack.append(next_state.name)
                else:
                    frozen_set = frozenset(each for each in transition_function[key])
                    try:
                        # state already exists
                        next_state = created_states_dict[frozen_set]
                    except KeyError:
                        # create state
                        state_tuple = tuple(each for each in transition_function[key])
                        state_name = ",".join(each.name for each in state_tuple)
                        next_state = det_automaton.state_add(state_name, marked=True)
                        created_states_dict[frozen_set] = next_state
                        state_stack.append(frozen_set)
                if key not in events_set:
                    events_set.add(det_automaton.event_add(key.name, key.controllable, key.observable))
                det_automaton.transition_add(from_state, next_state, key)

        while len(state_stack) != 0:
            state = state_stack.pop(0)
            if type(state) == frozenset:
                determinize_state(state, created_states_dict[state])
            else:
                determinize_state(created_states_dict[state], created_states_dict[state])

        return det_automaton

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

        def transition_already_exists(from_state, to_state, ev):
            for t in from_state.out_transitions:
                if t.to_state == to_state and t.event == ev:
                    return True
            return False

        # list the events
        evs = list(self.events)
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
            for event in evs:
                target_states = set()
                for state in pair:
                    trans_function = get_transition_function(state)
                    try:
                        target_states.add(trans_function[event])
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

    def isomorphic_check(G1, G2):
        pass

    def supervisor_reduction(self, G, criteria):

        # dict[supervisor_state] = plant_state
        univ_map = G.univocal(self)
        control_cover_dict = dict()
        control_cover_state = set()
        state_stack = list()

        #============Private Functions

        # this function returns the set of disabled events in the supervisor
        def get_disabled_events(sup_state):
            enabled_events_in_supervisor = set()
            enabled_events_in_system = set()
            disabled_events = list()

            for transition in sup_state.out_transitions: enabled_events_in_supervisor.add(transition.event.name)
            for transition in univ_map[sup_state].out_transitions: enabled_events_in_system.add(transition.event.name)

            for transition in enabled_events_in_system:
                if transition not in enabled_events_in_supervisor:
                    disabled_events.append(transition)

            return set(disabled_events)

        # this function returns the set of enabled events in a state
        def get_enabled_events(state):
            enabled_events = list()

            for transition in state.out_transitions: enabled_events.append(transition.event.name)

            return set(enabled_events)

        # marked attribute
        # returns 1 if T(x) = 1 AND M(x) = 1, 0 if T(x) = 0, -1 if T(x) = 1 AND M(x) = 0
        # T(x) refers to plant G and M(x) refers to supervisor S
        def get_marked_attribute(sup_state):
            if univ_map[sup_state].marked is False:
                return 0
            else:
                if sup_state.marked is True:
                    return 1
                else:
                    return -1

        def get_marked_action_attribute(x1, x2):
            mx1 = get_marked_attribute(x1)
            mx2 = get_marked_attribute(x2)
            if (mx1 == mx2) or ((mx1 == 0) and (mx2 != 0)) or ((mx2 == 0) and (mx1 != 0)):
                return True
            else:
                return False

        def verify_aggretation(s1, s2):
            count = 0
            for state_1 in s1:
                for state_2 in s2:
                    if state_1 != state_2:
                        try:
                            if len(aggregate_matrix[frozenset((state_1, state_2))]) == 0:
                                count = count + 1
                        except:
                            pass
                    else:
                        count = count + 1
            return count

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
            for event in self.events:
                control_cover_state = set()
                for state in current:
                    trans_function = get_transition_function(state)
                    try:
                        control_cover_state.add(trans_function[event])
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

        for event in self.events:
            sr_event_map[event] = Sr.event_add(event, True, True)

        for each in sr_state_map:
            for event in Sr.events:
                target_states = set()
                for state in each:
                    t_function = get_transition_function(state)
                    try:
                        target_states.add(t_function[event])
                    except:
                        pass
                for state in sr_state_map:
                    if target_states.issubset(set(state)) and len(target_states) > 0:
                        Sr.transition_add(sr_state_map[each], sr_state_map[state], sr_event_map[event])
                        break

        return (Sr)
