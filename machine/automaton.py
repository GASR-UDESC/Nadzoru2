#######################################
# CLASSES
#######################################

import copy
import functools

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


class EventSet(Base):  # TODO
    pass


class TransitionLayout:
    def __init__(self):
        self.render_angle = 0.0
        self.render_factor = 1.0
        self.ref_count = 0

    def inc_ref(self):
        """Use to control when to remove the Transition Layout"""
        self. ref_count = self.ref_count + 1

    def dec_ref(self):
        self. ref_count = self.ref_count - 1

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
    def __init__(self, name=None, marked=False, x=0, y=0, tex=None, *args, **kwargs):
        self.name = name
        self.tex = tex
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
        self.transition_layouts[transition.to_state].dec_ref()
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
            return None
        self.events[e.name] = e
        return e

    # TODO: test
    def event_remove_by_name(self, event_name):
        try:
            event = self.events[event_name]
            del self.events[event_name]
        except KeyError:
            return False
        else:
            for t in event.transitions:
                self.transition_remove(t)
            return True

    def event_remove(self, event):
        """event's name are unique"""
        return self.event_remove_by_name(event.name)

    def has_event_name(self, event_name):
        return event_name in self.events  # check if the event_name key exists in self.events

    def state_add(self, *args, initial=False, **kwargs):
        s = self.state_class(*args, **kwargs)
        self.states.add(s)
        if initial:
            self.initial_state = s
        return s

    # TODO: test
    def state_remove(self, state):
        try:
            self.states.remove(state)
        except KeyError:
            return False
        else:
            if self.initial_state == state:
                self.initial_state = None
            for t in state.in_transitions:
                self.transition_remove(t)
            for t in state.out_transitions:
                self.transition_remove(t)
            return True

    @property
    def initial_state(self):
        return self._initial_state

    @initial_state.setter
    def initial_state(self, value):
        if isinstance(value, self.state_class) or (value is None):
            self._initial_state = value

    def transition_add(self, from_state, to_state, *args, **kwargs):
        t = self.transition_class(from_state, to_state, *args, **kwargs)
        from_state.transition_out_add(t)
        to_state.transition_in_add(t)
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
        pass

    def load(self, file_name):
        pass

    def ides_import(self, file_name, load_layout=True):
        pass

    def ides_export(self, file_name):
        pass

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

        """Remove non-acessible states"""
        for state, is_accessible in states_dict.items():
            if is_accessible == False:
                self.state_remove(state)
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

        """Remove non-coacessible states"""
        for state, is_coaccessible in states_dict.items():
            if is_coaccessible == False:
                self.state_remove(state)

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
                    self.events.add(new_event)
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

            ev_set = set()
            for g_transition in univ_map[state_in_R].out_transitions:
                ev_set.add(g_transition.event.name)

            while flag_end:

                for g_transition in univ_map[state_in_R].out_transitions:
                    r_event_set = set()

                    for r_transition in state_in_R.out_transitions:
                        r_event_set.add(r_transition.event.name)

                    if g_transition.event.name not in r_event_set:
                        if not g_transition.event.controllable:
                            set_bad_state.add(state_in_R)
                            flag_bad_state = True
                    else:
                        next_state = r_transition.to_state
                        if next_state not in visited_states_set:
                            visited_states_set.add(next_state)
                            states_to_be_visited_in_R.append(next_state)
                try:
                    state_in_R = states_to_be_visited_in_R.pop()
                except IndexError:
                    flag_end = False

            if flag_bad_state:
                for state in set_bad_state:
                    sup.state_remove(state)
                set_bad_state = set()
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

        def determinize_state(state):
            transition_function = dict()
            for transition in original_automaton_dict[state.name].out_transitions:
                if transition.event in transition_function:
                    if not isinstance(transition_function[transition.event], list):
                        transition_function[transition.event] = [transition_function[transition.event]]
                    transition_function[transition.event].append(transition.to_state)
                else:
                    transition_function[transition.event] = transition.to_state
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
                    events_set.add(det_automaton.event_add(key.name, key.controllable,key.observable))
                det_automaton.transition_add(state, next_state, key)

        while len(state_stack) != 0:
            state = state_stack.pop(0)
            if type(state) == frozenset:
                for item in state:
                    determinize_state(item)
                selfloop = set()
                for transition in created_states_dict[state].in_transitions:
                    if transition not in selfloop:
                        selfloop.add(transition.event)
                for ev in selfloop:
                    det_automaton.transition_add(created_states_dict[state], created_states_dict[state], ev)
            else:
                determinize_state(created_states_dict[state])


        return det_automaton

    def complement(self, copy=False):
        pass

    def total(self, copy=False):
        pass

    def minimize(self, copy=False):
        pass

    def mask(self, masks, copy=False):
        pass

    def distinguish(self, refinements, copy=False):
        pass

    def isomorphic_check(G1, G2):
        pass

