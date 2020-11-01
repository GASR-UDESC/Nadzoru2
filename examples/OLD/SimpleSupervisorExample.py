from machine import automata
from machine import operations

########################################################################################################################
# Simple Supervisor Example - Conveyor & Sensor
########################################################################################################################

# Creating states

s0 = automata.State('0', True)
s1 = automata.State('1')

# Creating events

s_on = automata.Event('s_on')
s_off = automata.Event('s_off')
e_on = automata.Event('c', True)
e_off = automata.Event('d', True)

sensor_transitions = {s0: {s_on: s1}, s1: {s_off: s0}}
conveyor_transitions = {s0: {e_on: s1}, s1: {e_off: s0}}

G1 = automata.Automaton(sensor_transitions, s0)
G2 = automata.Automaton(conveyor_transitions, s0)


specifications_transitions = {s0: {s_on: s1, e_off: s0}, s1: {s_off: s0, e_on: s1}}

E = automata.Automaton(specifications_transitions, s0)

print("G1 states list:", G1.states_set())

print("G1 events list:", G1.events_set())


G = operations.sync(G1, G2)
K = operations.sync(E, G)

print("K:")
print(K.transitions)


S = operations.supc(K, G)

print("Supervisor:")
print(S.transitions)
