#######################################
# CLASSES
#######################################


class Event:
    def __init__(self, name, controllable=False, observable=True, **kwargs):
        """kwargs holds other properties"""
        self.name = name
        self.controllable = controllable
        self.observable = observable
        self.__dict__.update(kwargs)

    def __repr__(self):
        return self.name


class State:
    """
    A state that is a node in the Automaton singly-linked list.
    Also, create a singly-linked list for the transitions of the state.
    Takes O(1) time.
    """
    def __init__(self, name=None, mark=False, **kwargs):
        self.name = name
        self.mark = mark
        self.__dict__.update(kwargs)

    def __repr__(self):
        """
        Return a string representation of the transitions list of the state.
        Takes O(n) time.
        """

        return self.name


class Automaton:
    def __init__(self, transitions, initial_state):
        """
        Create a structure for Automata.
        """
        self.transitions = transitions
        self.initial_state = initial_state
        # self.marked_states = marked_states

    def states_set(self):
        """
        Return states list
        """
        s = set(self.transitions.keys())
        return s

    def events_set(self):
        """
        Return events list
        """
        s = set(val for dic in self.transitions.values() for val in dic.keys())
        return s

    def transitions_number(self):
        num = 0
        for s in self.transitions.keys():
            num = num + len(self.transitions[s])
        return num

    def remove_state(self, state):
        # deletes state, its output transitions and all transitions to it
        try:
            del self.transitions[state]
        except KeyError:
            print("State not found:", state)

        if state == self.initial_state:
            self.initial_state = None

        # deletes transitions which have state as destiny:
        deletion = {}
        for s in self.transitions.keys():
            for e, s2 in self.transitions[s].items():
                if s2 == state:
                    deletion[s] = e

        for s, e in deletion.items():
            del self.transitions[s][e]

    def remove_states(self, states):
        # deletes a set of state, its output transitions and all transitions to them
        for state in states:
            try:
                del self.transitions[state]
            except KeyError:
                print("State not found:", state)

        if self.initial_state in states:
            self.initial_state = None

        # deletes transitions which have state as destiny:
        deletion = list()
        for s in self.transitions.keys():
            for e, s2 in self.transitions[s].items():
                if s2 in states:
                    deletion.append([s, e])

        for v in deletion:
            del self.transitions[v[0]][v[1]]
