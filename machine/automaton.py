#######################################
# CLASSES
#######################################

import copy

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
        return "(" + self.name + ")"

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
        self.events = set()
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
        self.events.add(e)
        return e

    # TODO: test
    def event_remove(self, event):
        try:
            self.events.remove(event)
        except KeyErorr:
            return False
        else:
            for t in event.transitions:
                self.transition_remove(t, rmRefEvent=True)
            return True

    def has_event(self, event_name):
        for ev in self.events:
            if ev.name == event_name:
                return True
        return False

    def state_add(self, *args, initial=False, **kwargs):
        s = self.state_class(*args, **kwargs)
        self.states.add(s)
        if initial:
            self.initial_state = s
        return s

    def has_state(self, state_name):
        for s in self.states:
            if s.name == state_name:
                return True
        return False

    def get_state(self, state_name):
        for state in self.states:
            if state.name == state_name:
                return state
        return None

    # TODO: test
    def state_remove(self, state):
        try:
            self.states.remove(state)
        except KeyErorr:
            return False
        else:
            for t in state.in_transitions:
                self.transition_remove(t, rmRefToState=True)
            for t in state.out_transitions:
                self.transition_remove(t, rmRefFromState=True)
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
    def transition_remove(self, transition, rmRefEvent=True, rmRefFromState=True, rmRefToState=True):
        if rmRefEvent:
            transition.event.transitions.discard(transition)
        if rmRefFromState:
            # transition.from_state.out_transitions.discard(transition)
            transition.from_state.transition_out_remove(transition)
        if rmRefToState:
            # transition.to_state.in_transitions.discard(transition)
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
        pass

    def is_accessible(self):
        isAccessible = True
        for state in self.states:
            if ((state != self.initial_state) and not(len(state.in_transitions))):
                isAccessible = False
                break
        return isAccessible

    def accessible(self, copy=False):
        self = self if not copy else self.clone()

        stateStack = list()
        visitedStack = list()
        stateStack.append(self.initial_state)

        while len(stateStack) != 0:
            for transition in stateStack[0].out_transitions:
                if transition.to_state != None:
                    stateStack.append(transition.to_state)
            visitedStack.append(stateStack[0])
            stateStack.pop(0)

        statesToRemove = list()
        transitionsToRemove = list()

        for state in self.states:
            if not(visitedStack.__contains__(state)):
                statesToRemove.append(state)
                for transition in state.in_transitions:
                    transitionsToRemove.append(transition)
                for transition in state.out_transitions:
                    transitionsToRemove.append(transition)

        for transition in transitionsToRemove:
            if transition != None:
                self.transition_remove(transition)
        for state in statesToRemove:
            if state != None:
                self.state_remove(state)

        return self

    def is_coaccessible(self):
        pass

    def coaccessible(self, copy=False):
        pass

    def trim(self, copy=False):
        return self.coaccessible(copy).accessible()

    def incoaccessible_states_join(self):
        pass

    def selfloop(self, event_set):
        pass

    def synchronization(*args):
        """ This function returns the accessible part of the synchronous composition. Instead of calculating all composed
            states and then calculate the accessible part, we only add accessible states to the output."""

        if len(args) < 2:
            return

        G = Automaton()  # function output

        stateTupleStack = list()
        stateVisitedStack = list()

        initialStateTuple = tuple(state.initial_state for state in args)
        initialStateName = ",".join(state.name for state in initialStateTuple)
        G.state_add(initialStateName, initial=True)

        stateTupleStack.append(initialStateTuple)
        stateVisitedStack.append(initialStateTuple)

        transitionlist = list()
        nameList = list()

        while len(stateTupleStack) != 0:
            transitionlist.clear()
            for each in stateTupleStack[0]:
                for transition in each.out_transitions:
                    #this is not working
                    if transitionlist.__contains__(transition) == False:
                        transitionlist.append(transition)  # transitionlist holds the available transitions in the state of the tuple
            for t in transitionlist:
                nameList.clear()
                # if event is common, it has to be enabled in all states of the tuple
                for state in stateTupleStack[0]:
                    currStateName = ",".join(state.name for state in stateTupleStack[0])
                    transitioned = False
                    for transition in state.out_transitions:
                        if transition.event.name == t.event.name:
                            transitioned = True
                            if(G.has_event(transition.event.name) == False):
                                G.event_add(transition.event.name, transition.event.controllable, transition.event.observable)
                            nameList.append(transition.to_state)
                    if transitioned == False:
                        nameList.append(state)
                stateTuple = tuple(s for s in nameList)
                stateName = ",".join(state.name for state in stateTuple)
                if G.has_state(stateName) == False:
                    G.state_add(stateName)
                    stateTupleStack.append(stateTuple)
                # TODO how to add only transitions that werent already added
                t = G.transition_add(G.get_state(currStateName), G.get_state(stateName), transition.event)
            stateVisitedStack.append(stateTupleStack[0])
            stateTupleStack.pop(0)
        return G


    def merge_events(self, *args):
        "Add events from *args into self"
        event_names = {event.name for event in self.events}  # set
        added_events = list()  # so we can undo in case of error
        for g in args:
            for ev in g.events:
                if ev.name not in event_names:
                    new_event = ev.copy()
                    self.events.add(new_event)
                    added_events.append(new_event)
                    event_names.add(ev.name)
                else:
                    pass  # TODO (1) check if ev and self.get_event(ev.name) are equivallent (method in event)
                          #      (2) if not undo previously added events (from added_events)
                          #      (3) raise Error ErrorMultiplePropetiesForEventName

    def synchronization2(*args):
        """ This function returns the accessible part of the synchronous composition. Instead of calculating all composed
            states and then calculate the accessible part, we only add accessible states to the output."""

        if len(args) < 2:
            return

        G = args[0].__class__()  # function output

        G.merge_events(*args)

        state_stack = list()
        state_map = dict()  # maps tuple of states (from args) to respective state in G

        def G_state_add(state_tuple, initial=False):
            state_name = ",".join(state.name for state in state_tuple)
            s = G.state_add(state_name, initial=initial)
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
                    if g.has_event(event.name):
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

    def univocal(self, *args):
        pass

    def supC(G, K):
        pass

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
        pass

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

