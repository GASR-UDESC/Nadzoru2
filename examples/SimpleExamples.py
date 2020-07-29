from machine import automata
from machine import operations

########################################################################################################################
# Composition example
########################################################################################################################

# Creating states

s0 = automata.State('0', True)
s1 = automata.State('1')

# Creating events

a = automata.Event('a', True)
b = automata.Event('b')
c = automata.Event('c', True)
d = automata.Event('d')


transitions_1 = {s0: {a: s1, b: s0}, s1: {b: s0}}
transitions_2 = {s0: {c: s1}, s1: {d: s0}}

G1 = automata.Automaton(transitions_1, s0)
G2 = automata.Automaton(transitions_2, s0)


print("G1 states list:", G1.states_set())
print("G1 events list:", G1.events_set())


G = operations.sync(G1, G2)

print("G states list:", G.states_set())
print("G events list:", G.events_set())
print("G transitions:", G.transitions)


########################################################################################################################
# Coaccessible example
########################################################################################################################

# Creating more states
s2 = automata.State('2')
s3 = automata.State('3')
s4 = automata.State('4', True)
s5 = automata.State('5')
s6 = automata.State('6')
s7 = automata.State('7')


transitions_3 = {s0: {c: s1, b: s7, a: s2, d: s6},
                 s1: {},
                 s2: {c: s3, d: s4},
                 s3: {},
                 s4: {},
                 s5: {},
                 s6: {a: s5},
                 s7: {}}

G3 = automata.Automaton(transitions_3, s0)

print("G3 transitions:")
print(G3.transitions)

operations.coaccessible(G3)

print("G3 coaccessible transitions:")
print(G3.transitions)
