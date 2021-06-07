#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins

from machine.automaton import Automaton
g = Automaton()

Q0 = g.state_add('Q0', marked = False, initial=True)
Q1 = g.state_add('Q1', marked = False, initial=False)
Q2 = g.state_add('Q2', marked = True, initial=False)
Q3 = g.state_add('Q3', marked = False, initial=False)
Q4 = g.state_add('Q4', marked = True, initial=False)

e0 = g.event_add('e0', True, True)
e1 = g.event_add('e1', True, True)

t1 = g.transition_add(Q0, Q1, e0)
t2 = g.transition_add(Q0, Q3, e1)
t3 = g.transition_add(Q1, Q1, e0)
t4 = g.transition_add(Q1, Q2, e1)
t5 = g.transition_add(Q3, Q3, e0)
t6 = g.transition_add(Q3, Q4, e1)
t7 = g.transition_add(Q4, Q2, e1)
t8 = g.transition_add(Q4, Q1, e0)
t9 = g.transition_add(Q2, Q4, e1)
t10 = g.transition_add(Q2, Q3, e0)

print(g)
y = g.minimize()
print(y)
'''
S = g.state_add('S', marked = False, initial = True)
A = g.state_add('A', marked = False)
B = g.state_add('B', marked = True)

a = g.event_add('a', True, True)
b = g.event_add('b', True, True)

t1 = g.transition_add(S, A, a)
t2 = g.transition_add(A, A, a)
t3 = g.transition_add(A, B, a)
t4 = g.transition_add(B, A, b)
t5 = g.transition_add(B, B, b)
t6 = g.transition_add(S, B, b)


print(g)
y = g.minimize()
print(y)

########
s1 = g.state_add('1', marked = False, initial = True)
s2 = g.state_add('2', marked = True)
s3 = g.state_add('3', marked = False)
s4 = g.state_add('4', marked = False)

a = g.event_add('a', True, True)
b = g.event_add('b', True, True)
c = g.event_add('c', True, True)

t1 = g.transition_add(s1, s2, a)
t2 = g.transition_add(s1, s3, a)
t5 = g.transition_add(s2, s4, b)
t3 = g.transition_add(s3, s3, c)
t4 = g.transition_add(s3, s2, b)
t6 = g.transition_add(s4, s4, b)

print(g)
y = g.determinize()
print(y)

########
a = g.event_add('a', True, True)
e = g.event_add('e', True, True)
c = g.event_add('c', True, True)
x = g.event_add('g', True, True)
h = g.event_add('h', True, True)
d = g.event_add('d', True, True)

s1 = g.state_add('1', marked=True, initial=True)
s2 = g.state_add('2', marked=True)
s3 = g.state_add('3', marked=True)
s4 = g.state_add('4', marked=True)
s5 = g.state_add('5', marked=False)
s6 = g.state_add('6', marked=False)
s7 = g.state_add('7', marked=False)
s8 = g.state_add('8', marked=True)
s9 = g.state_add('9', marked=False)
s10 = g.state_add('10', marked=True)
s11 = g.state_add('11', marked=True)

t1 = g.transition_add(s1, s2, a)
t2 = g.transition_add(s1, s8, d)
#t3 = g.transition_add(s2, s3, e)
t4 = g.transition_add(s2, s4, x)
t5 = g.transition_add(s3, s5, c)
t6 = g.transition_add(s4, s7, h)
#t7 = g.transition_add(s5, s6, x)
t8 = g.transition_add(s6, s6, x)
t9 = g.transition_add(s7, s7, h)
t10 = g.transition_add(s8, s9, c)
t11 = g.transition_add(s8, s11, a)
t12 = g.transition_add(s11, s11, a)
#t13 = g.transition_add(s9, s10, x)
t14 = g.transition_add(s10, s10, x)

y = g.accessible()
w = g.coaccessible()
#print(g)
#print('----------------')
print(y)
print(w)
#print('----------------')
#print('g', g.is_accessible())
#print('y', y.is_accessible())

####################
g1 = Automaton()
E = Automaton()

ev1 = g1.event_add('a1', True, True)
ev2 = g1.event_add('b1', False, True)
ev3 = g1.event_add('a2', True, True)
ev4 = g1.event_add('b2', False, True)

s0 = g1.state_add('0', marked=True, initial=True)
s1 = g1.state_add('1', marked=False)
s2 = g1.state_add('2', marked=False)
s3 = g1.state_add('3', marked=False)
s4 = g1.state_add('4', marked=False)
s5 = g1.state_add('5', marked=False)
s6 = g1.state_add('6', marked=False)
s7 = g1.state_add('7', marked=False)

t1 = g1.transition_add(s0, s1, ev1)
t2 = g1.transition_add(s1, s2, ev2)
t3 = g1.transition_add(s2, s3, ev3)
t4 = g1.transition_add(s2, s7, ev1)
t5 = g1.transition_add(s3, s4, ev1)
t6 = g1.transition_add(s3, s0, ev4)
t7 = g1.transition_add(s4, s5, ev2)
t8 = g1.transition_add(s4, s1, ev4)
t9 = g1.transition_add(s5, s6, ev1)
t10 = g1.transition_add(s5, s2, ev4)
t11 = g1.transition_add(s6, s7, ev4)
t12 = g1.transition_add(s7, s4, ev3)

ev5 = E.event_add('a1', True, True)
ev6 = E.event_add('b1', False, True)
ev7 = E.event_add('a2', True, True)
ev8 = E.event_add('b2', False, True)

sg0 = E.state_add('0', marked=True, initial=True)
sg1 = E.state_add('1', marked=False)
sg2 = E.state_add('2', marked=False)
sg3 = E.state_add('3', marked=False)

tg1 = E.transition_add(sg0, sg1, ev5)
tg2 = E.transition_add(sg0, sg2, ev7)
tg3 = E.transition_add(sg1, sg0, ev6)
tg4 = E.transition_add(sg1, sg3, ev7)
tg5 = E.transition_add(sg2, sg1, ev8)
tg6 = E.transition_add(sg2, sg3, ev5)
tg7 = E.transition_add(sg3, sg2, ev6)
tg8 = E.transition_add(sg3, sg1, ev8)


R = E.sup_c(g1)
print(R)
##
g1 = Automaton()
g2 = Automaton()

ev1 = g1.event_add('a', True, True)
ev2 = g1.event_add('b', True, True)

s1 = g1.state_add('0', marked=True, initial=True)
s2 = g1.state_add('1', marked=False)
s3 = g1.state_add('2', marked=False)

t1 = g1.transition_add(s1, s2, ev1)
t2 = g1.transition_add(s2, s3, ev2)
t3 = g1.transition_add(s3, s1, ev2)

ev3 = g2.event_add('b', True, True)
ev4 = g2.event_add('g', True, True)

s4 = g2.state_add('0', marked=True, initial=True)
s5 = g2.state_add('1', marked=False)

t4 = g2.transition_add(s4, s5, ev3)
t5 = g2.transition_add(s5, s4, ev4)

print(g1.accessible())

#
sensor = Automaton()
chave = Automaton()
espec = Automaton()

s1_on = sensor.event_add('s1_on', False, True)
s1_off = sensor.event_add('s1_off', False, True)

chave_on = chave.event_add('chave_on', True, True)
chave_off = chave.event_add('chave_off', True, True)

sensor1 = sensor.state_add('s1', marked=True, initial=True)
sensor2 = sensor.state_add('s2', marked = False)

chave1 = chave.state_add('c1', marked=True, initial=True)
chave2 = chave.state_add('c2', marked=True)

ts1 = sensor.transition_add(sensor1, sensor2, s1_on, probability=0.2)
ts2 = sensor.transition_add(sensor2, sensor1, s1_off)

tc1 = chave.transition_add(chave1, chave2, chave_on)
tc2 = chave.transition_add(chave2, chave1, chave_off)

ev1 = espec.event_add('chave_off', True, True)
ev2 = espec.event_add('s1_on', False, True)
ev3 = espec.event_add('chave_on', True, True)
ev4 = espec.event_add('s1_off', False, True)

espec1 = espec.state_add('e1', marked=True, initial=True)
espec2 = espec.state_add('e2', marked=False)

t1 = espec.transition_add(espec1, espec1, ev1)
t2 = espec.transition_add(espec1, espec2, ev2)
t3 = espec.transition_add(espec2, espec2, ev3)
t4 = espec.transition_add(espec2, espec2, ev1)
t5 = espec.transition_add(espec2, espec1, ev4)

print(sensor)
print("-------------")
print(chave)
print("-------------")
print(espec)
print("-------------")
print("-------------")

# print(sensor.synchronization(chave, espec))
print(sensor.synchronization2(chave, espec))

'''
