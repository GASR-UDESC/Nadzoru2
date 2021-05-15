#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins

from machine.automaton import Automaton
g = Automaton()

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

#print(g)
#print('----------------')
print(y)
#print('----------------')
#print('g', g.is_accessible())
#print('y', y.is_accessible())

'''
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
