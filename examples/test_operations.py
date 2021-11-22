#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins
from machine.automaton import Automaton

def create_automata():
    G1 = Automaton()
    G2 = Automaton()

    G1_e_a = G1.event_add('a', True, True)
    G1_e_b = G1.event_add('b', False, True)
    G1_e_c = G1.event_add('c', True, False)

    G2_e_a = G2.event_add('a', True, True)
    G2_e_b = G2.event_add('b', False, True)
    G2_e_c = G2.event_add('c', True, False)

    G1_q1 = G1.state_add(marked=False, initial=True)
    G1_q2 = G1.state_add()
    G1_q3 = G1.state_add()

    G2_q1 = G2.state_add(marked=False, initial=True)
    G2_q2 = G2.state_add()
    G2_q3 = G2.state_add()

    G1.transition_add(G1_q1, G1_q2, G1_e_a)
    G1.transition_add(G1_q1, G1_q3, G1_e_b)
    G1.transition_add(G1_q1, G1_q1, G1_e_c)
    G1.transition_add(G1_q2, G1_q3, G1_e_b)
    G1.transition_add(G1_q3, G1_q1, G1_e_c)

    G1.transition_add(G1_q3, G1_q1, G1_e_a)

    G2.transition_add(G2_q1, G2_q2, G2_e_a)
    G2.transition_add(G2_q1, G2_q3, G2_e_b)
    G2.transition_add(G2_q1, G2_q1, G2_e_c)
    G2.transition_add(G2_q2, G2_q3, G2_e_b)
    G2.transition_add(G2_q3, G2_q1, G2_e_c)

    G2.transition_add(G2_q3, G2_q3, G2_e_a)

    return G1, G2

G1, G2 = create_automata()

print(G1.isomorphic_check(G2, verbose=True) == True and 'Pass' or 'Fail')

G2a = G2.clone()
G2a_q4 = G2a.state_add()
print(G1.isomorphic_check(G2a) == False and 'Pass' or 'Fail')
