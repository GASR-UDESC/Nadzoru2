#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins

from machine.automaton import Automaton

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

print(g1.synchronization(g2))
'''

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


