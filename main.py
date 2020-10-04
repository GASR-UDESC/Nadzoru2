#!/usr/bin/python

import pluggins

from machine.automata import Automaton

a = Automaton()

e1 = a.event_add('a', False, True)
e2 = a.event_add('b', False, True)
s1 = a.state_add('q1', market=True, initial=True)
s2 = a.state_add('q2', market=True)

t1 = a.transition_add(s1, s2, e1)
t2 = a.transition_add(s2, s1, e2, probability=0.2)
a.transition_add(s1, s1, e2)
a.transition_add(s2, s2, e1)

t1.probability = 0.5

print(a)
print(t1.probabilistic_str())
print(t2.probabilistic_str())
