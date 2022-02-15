#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins

from machine.automaton import Automaton
import time

G = Automaton()
S = Automaton()
gpath = r"./reduction/Unreliable Machine - NOK/P"
spath = r"./reduction/Unreliable Machine - NOK/SUP"
ncpath = r"./reduction/Unreliable Machine - NOK/NCONT"
G = G.grail_import(gpath, ncpath)
S = S.grail_import(spath, ncpath)


G = Automaton()

########## EX 4 ###########
g1 = G.state_add('1', marked=False, initial=True)
g2 = G.state_add('2', False)
g3 = G.state_add('3', False)
g4 = G.state_add('4', False)
g5 = G.state_add('5', False)
g6 = G.state_add('6', False)
g7 = G.state_add('7', False)
g8 = G.state_add('8', False)
g9 = G.state_add('9', False)
g10 = G.state_add('10', False)
g11 = G.state_add('11', False)
g12 = G.state_add('12', False)
g13 = G.state_add('13', False)
g14 = G.state_add('14', False)
g15 = G.state_add('15', False)
g16 = G.state_add('16', False)

ga = G.event_add('a', False, True)
gb = G.event_add('b', False, True)
gc = G.event_add('c', False, True)
gd = G.event_add('d', False, True)
ge = G.event_add('e', False, True)
gf = G.event_add('f', False, False)
gg = G.event_add('g', True, True)

G.transition_add(g1, g2, ga)
G.transition_add(g2, g3, gb)
G.transition_add(g3, g4, gd)
G.transition_add(g4, g1, ge)
G.transition_add(g3, g5, gc)
G.transition_add(g5, g6, gf)
G.transition_add(g6, g7, gd)
G.transition_add(g7, g8, gg)
G.transition_add(g8, g8, ge)
G.transition_add(g6, g9, ge)
G.transition_add(g9, g10, ga)
G.transition_add(g10, g10, gb)
G.transition_add(g7, g9, ge)
G.transition_add(g5, g11, ge)
G.transition_add(g11, g12, ga)
G.transition_add(g12, g12, gb)
G.transition_add(g4, g13, gg)
G.transition_add(g13, g13, gb)
G.transition_add(g13, g14, gf)
G.transition_add(g14, g14, gb)
G.transition_add(g14, g15, ge)
G.transition_add(g15, g14, ga)
G.transition_add(g15, g16, gg)
G.transition_add(g16, g16, ga)

fault_events = list()
fault_events.append(gf)

print(G.synchronization(G.labeller(fault_events)).observer())

########## EX 4 ###########
#g1 = G.state_add('1', marked=False, initial=True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', False)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)
#g8 = G.state_add('8', False)

#ga = G.event_add('a', False, True)
#gb = G.event_add('b', False, True)
#gc1 = G.event_add('c1', True, True)
#gc2 = G.event_add('c2', True, True)
#ge = G.event_add('e', False, True)
#gf = G.event_add('f', False, False)
#gg = G.event_add('g', False, True)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g1, gb)
#G.transition_add(g2, g3, ge)
#G.transition_add(g3, g4, gc1)
#G.transition_add(g1, g7, gg)
#G.transition_add(g7, g1, ge)
#G.transition_add(g7, g8, gb)
#G.transition_add(g8, g4, gc2)
#G.transition_add(g4, g5, gf)
#G.transition_add(g5, g6, gg)
#G.transition_add(g6, g6, ge)

#fault_events = list()
#fault_events.append(gf)

#print(G.synchronization(G.labeller(fault_events)).observer())

########## EX 3 ###########
#g1 = G.state_add('1', marked=False, initial=True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', False)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)
#g8 = G.state_add('8', False)
#g9 = G.state_add('9', False)

#ga = G.event_add('a', False, True)
#gb = G.event_add('b', False, True)
#gc = G.event_add('c', True, True)
#gd = G.event_add('d', False, True)
#gd1 = G.event_add('d1', False, True)
#gd2 = G.event_add('d2', False, True)
#ge = G.event_add('e', False, True)
#gf = G.event_add('f', False, False)
#gg = G.event_add('g', False, True)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g3, gb)
#G.transition_add(g3, g1, gd)
#G.transition_add(g2, g4, ge)
#G.transition_add(g4, g5, gc)
#G.transition_add(g5, g6, gf)
#G.transition_add(g6, g7, gd1)
#G.transition_add(g6, g9, gd2)
#G.transition_add(g9, g7, gc)
#G.transition_add(g7, g8, gg)
#G.transition_add(g8, g8, ge)

#fault_events = list()
#fault_events.append(gf)

#print(G.synchronization(G.labeller(fault_events)).observer())

########## EX 2 ###########
#g1 = G.state_add('1', marked=False, initial=True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', False)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)
#g8 = G.state_add('8', False)
#g9 = G.state_add('9', False)
#g10 = G.state_add('10', False)
#g11 = G.state_add('11', False)
#g12 = G.state_add('12', False)

#ga = G.event_add('a', False, True)
#gb = G.event_add('b', False, True)
#gc = G.event_add('c', True, True)
#gd = G.event_add('d', False, True)
#ge = G.event_add('e', False, True)
#gf = G.event_add('f', False, False)
#gg = G.event_add('g', True, True)
#guo = G.event_add('uo', False, False)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g1, gb)
#G.transition_add(g2, g3, ge)
#G.transition_add(g3, g4, gc)
#G.transition_add(g1, g9, gg)
#G.transition_add(g9, g10, gb)
#G.transition_add(g10, g4, guo)
#G.transition_add(g4, g5, ge)
#G.transition_add(g10, g11, ge)
#G.transition_add(g11, g12, gg)
#G.transition_add(g12, g12, gb)
#G.transition_add(g5, g6, gf)
#G.transition_add(g6, g7, gd)
#G.transition_add(g7, g8, gg)
#G.transition_add(g8, g8, ge)

#fault_events = list()
#fault_events.append(gf)

#print(G.synchronization(G.labeller(fault_events)).observer())

########## EX 1 ###########
#g1 = G.state_add('1', marked=False, initial=True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', False)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)
#g8 = G.state_add('8', False)
#g9 = G.state_add('9', False)
#g10 = G.state_add('10', False)
#g11 = G.state_add('11', False)
#g12 = G.state_add('12', False)

#ga = G.event_add('a', False, True)
#gb = G.event_add('b', False, True)
#gc = G.event_add('c', True, True)
#gd = G.event_add('d', False, True)
#ge = G.event_add('e', False, True)
#gf = G.event_add('f', False, False)
#gg = G.event_add('g', True, True)
#guo = G.event_add('uo', False, False)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g1, gb)
#G.transition_add(g2, g3, ge)
#G.transition_add(g3, g4, gc)
#G.transition_add(g1, g8, gg)
#G.transition_add(g8, g9, gb)
#G.transition_add(g9, g4, ge)
#G.transition_add(g4, g5, gf)
#G.transition_add(g5, g6, gd)
#G.transition_add(g6, g7, gg)
#G.transition_add(g7, g7, ge)
#G.transition_add(g9, g10, guo)
#G.transition_add(g10, g11, ge)
#G.transition_add(g11, g12, gg)
#G.transition_add(g12, g12, gb)

#fault_events = list()
#fault_events.append(gf)

#print(G.synchronization(G.labeller(fault_events)).observer())

## TESTE 5 ROTULADOR + OBSERVADOR + DIAGNOSTICADOR
#g1 = G.state_add('1', marked=False, initial=True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', False)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)
#g8 = G.state_add('8', False)
#g9 = G.state_add('9', False)

#ga = G.event_add('a', False, True)
#gb = G.event_add('b', False, True)
#gc = G.event_add('c', True, True)
#gd = G.event_add('d', False, True)
#ge = G.event_add('e', False, True)
#gf = G.event_add('f', False, False)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g7, ge)
#G.transition_add(g7, g6, ga)
#G.transition_add(g6, g1, ge)
#G.transition_add(g2, g3, gb)
#G.transition_add(g3, g2, gc)
#G.transition_add(g3, g4, gf)
#G.transition_add(g7, g8, gf)
#G.transition_add(g4, g5, gc)
#G.transition_add(g5, g4, gb)
#G.transition_add(g8, g9, gd)
#G.transition_add(g9, g9, ge)

#fault_events = list()
#fault_events.append(gf)

#print(G.labeller(fault_events).observer())
## TESTE 4 ROTULADOR + OBSERVADOR + DIAGNOSTICADOR
#g1 = G.state_add('1', marked=False, initial=True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', False)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)
#g8 = G.state_add('8', False)
#g9 = G.state_add('9', False)

#ga = G.event_add('a', False, True)
#gb = G.event_add('b', False, True)
#gc = G.event_add('c', True, True)
#gd = G.event_add('d', False, True)
#gd1 = G.event_add('d1', False, True)
#gd2 = G.event_add('d2', False, True)
#ge = G.event_add('e', False, True)
#gf = G.event_add('f', False, False)
#gg = G.event_add('g', False, True)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g3, gb)
#G.transition_add(g3, g1, gd)
#G.transition_add(g2, g4, ge)
#G.transition_add(g4, g5, gc)
#G.transition_add(g5, g6, gf)
#G.transition_add(g6, g7, gd1)
#G.transition_add(g6, g9, gd2)
#G.transition_add(g9, g7, gc)
#G.transition_add(g7, g8, gg)
#G.transition_add(g8, g8, ge)

#fault_events = list()
#fault_events.append(gf)

#print(G.labeller(fault_events).observer())
## TESTE 3 ROTULADOR + OBSERVADOR + DIAGNOSTICADOR
#g1 = G.state_add('1', marked = True, initial = True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', True)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)

#ga = G.event_add('a', True, True)
#gb = G.event_add('b', True, True)
#go = G.event_add('o', False, False)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g1, gb)
#G.transition_add(g1, g3, go)
#G.transition_add(g3, g4, ga)
#G.transition_add(g4, g3, gb)
#G.transition_add(g4, g4, ga)
#G.transition_add(g4, g5, go)
#G.transition_add(g5, g5, ga)

#fault_events = list()
#fault_events.append(go)

#print(G.labeller(fault_events).observer())
## TESTE 2 ROTULADOR + OBSERVADOR + DIAGNOSTICADOR
#g1 = G.state_add('1', marked = True, initial = True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', True)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)

#ga = G.event_add('a', True, True)
#gb = G.event_add('b', True, True)
#gc = G.event_add('c', True, True)
#gd = G.event_add('d', True, True)
#ge = G.event_add('e', True, True)
#gh = G.event_add('h', True, True)
#gf = G.event_add('f', False, False)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g3, gf)
#G.transition_add(g2, g6, gb)
#G.transition_add(g3, g4, gb)
#G.transition_add(g6, g7, gc)
#G.transition_add(g4, g5, gd)
#G.transition_add(g5, g5, ge)
#G.transition_add(g7, g7, gh)

#fault_events = list()
#fault_events.append(gf)

#print(G.labeller(fault_events).observer())
## TESTE 1 ROTULADOR + OBSERVADOR + DIAGNOSTICADOR
#g1 = G.state_add('1', marked = True, initial = True)
#g2 = G.state_add('2', False)
#g3 = G.state_add('3', True)
#g4 = G.state_add('4', False)
#g5 = G.state_add('5', False)
#g6 = G.state_add('6', False)
#g7 = G.state_add('7', False)

#ga = G.event_add('a', True, True)
#gb = G.event_add('b', True, True)
#gc = G.event_add('c', True, True)
#gh = G.event_add('h', True, True)
#gf = G.event_add('f', False, False)

#G.transition_add(g1, g2, ga)
#G.transition_add(g2, g3, gf)
#G.transition_add(g2, g6, gb)
#G.transition_add(g3, g4, gb)
#G.transition_add(g6, g7, gc)
#G.transition_add(g4, g5, gc)
#G.transition_add(g5, g5, gh)
#G.transition_add(g7, g7, gh)

#fault_events = list()
#fault_events.append(gf)

#print(G.labeller(fault_events).observer())

#######################


'''
#PAG 115 FIG 5.4 (5.1.4)
G = Automaton()
S = Automaton()
Sr = Automaton()

g0 = G.state_add('0', marked = True, initial = True)
g1 = G.state_add('1', False)
g2 = G.state_add('2', True)
g3 = G.state_add('3', False)
g4 = G.state_add('4', False)

ga = G.event_add('a', True, True)
gb = G.event_add('b', True, True)
gc = G.event_add('c', True, True)

G.transition_add(g0, g1, ga)
G.transition_add(g1, g2, gb)
G.transition_add(g2, g3, gb)
G.transition_add(g3, g0, gc)
G.transition_add(g2, g4, ga)
G.transition_add(g4, g2, gc)
G.transition_add(g4, g4, gb)

s0 = S.state_add('0', marked = False, initial = True)
s1 = S.state_add('1', True)
s2 = S.state_add('2', True)
s3 = S.state_add('3', False)
s4 = S.state_add('4', False)

sa = S.event_add('a', True,True)
sb = S.event_add('b', True, True)
sc = S.event_add('c', True, True)

S.transition_add(s0, s1, sa)
S.transition_add(s1, s2, sb)
S.transition_add(s2, s3, sb)
S.transition_add(s3, s0, sc)
S.transition_add(s2, s4, sa)
S.transition_add(s4, s2, sc)
S.transition_add(s4, s4, sb)

print(time.time())
Sr = S.supervisor_reduction(G, 'a')
print(time.time())
print(Sr)

#PAG 79 FIG 3.12 - PAG 144 FIG 5.3
G = Automaton()
S = Automaton()
Sr = Automaton()

g0 = G.state_add('0', marked = True, initial = True)
g1 = G.state_add('1', False)
g2 = G.state_add('2', False)
g3 = G.state_add('3', False)
g4 = G.state_add('4', False)
g5 = G.state_add('5', False)

ga = G.event_add('a', True, True)
gb = G.event_add('b', True, True)
gc = G.event_add('c', False, True)
gd = G.event_add('d', False, True)

G.transition_add(g0, g1, ga)
G.transition_add(g0, g2, gb)
G.transition_add(g1, g3, gb)
G.transition_add(g1, g4, ga)
G.transition_add(g2, g5, ga)
G.transition_add(g2, g4, gb)
G.transition_add(g3, g4, gc)
G.transition_add(g5, g4, gc)
G.transition_add(g4, g0, gd)

s0 = S.state_add('0', marked = True, initial = True)
s1 = S.state_add('1', True)
s2 = S.state_add('2', True)
s3 = S.state_add('3', True)

sa = S.event_add('a', True,True)
sb = S.event_add('b', True, True)
sc = S.event_add('c', False, True)
sd = S.event_add('d', False, True)


S.transition_add(s0, s1, sa)
S.transition_add(s0, s2, sb)
S.transition_add(s1, s3, sa)
S.transition_add(s2, s3, sb)
S.transition_add(s3, s0, sd)

print(time.time())
Sr = S.supervisor_reduction(G, 'a')
print(time.time())
print(Sr)

#PAG 113 FIG 5.2 (5.1.2a)

G = Automaton()
S = Automaton()

g0 = G.state_add('0', marked = True, initial = True)
g1 = G.state_add('1', False)
g2 = G.state_add('2', False)
g3 = G.state_add('3', False)
g4 = G.state_add('4', False)

ga = G.event_add('a', False, True)
gb = G.event_add('b', False, True)
gc = G.event_add('c', False, True)
gd = G.event_add('d', True, True)

G.transition_add(g0, g1, gb)
G.transition_add(g0, g3, ga)
G.transition_add(g0, g4, gc)
G.transition_add(g1, g2, gb)
G.transition_add(g2, g0, ga)
G.transition_add(g3, g2, ga)
G.transition_add(g3, g0, gd)
G.transition_add(g4, g0, ga)
G.transition_add(g4, g3, gd)


s0 = S.state_add('0', marked = True, initial = True)
s1 = S.state_add('1', True)
s2 = S.state_add('2', True)
s3 = S.state_add('3', True)
s4 = S.state_add('4', True)

sa = S.event_add('a', False,True)
sb = S.event_add('b', False, True)
sc = S.event_add('c', False, True)
sd = S.event_add('d', True, True)

S.transition_add(s0, s1, sb)
S.transition_add(s0, s4, sa)
S.transition_add(s0, s3, sc)
S.transition_add(s1, s2, sb)
S.transition_add(s2, s0, sa)
S.transition_add(s3, s0, sa)
S.transition_add(s4, s0, sd)
S.transition_add(s4, s2, sa)

print(time.time())
S.supervisor_reduction(G, 'a')
print(time.time())

#PAG 113 FIG 5.1 (5.1.1)

G = Automaton()
S = Automaton()

g0 = G.state_add('0', marked = True, initial = True)
g1 = G.state_add('1', False)
g2 = G.state_add('2', False)

ga = G.event_add('a', False, True)
gb = G.event_add('b', False, True)
gc = G.event_add('c', False, True)
gd = G.event_add('d', True, True)

G.transition_add(g0, g0, ga)
G.transition_add(g0, g1, gc)
G.transition_add(g1, g0, gb)
G.transition_add(g1, g1, gd)
G.transition_add(g1, g2, ga)
G.transition_add(g2, g0, gc)
G.transition_add(g2, g2, gb)
G.transition_add(g2, g2, gd)


s0 = S.state_add('0', marked = True, initial = True)
s1 = S.state_add('1', True)
s2 = S.state_add('2', True)

sa = S.event_add('a', False,True)
sb = S.event_add('b', False, True)
sc = S.event_add('c', False, True)
sd = S.event_add('d', True, True)

S.transition_add(s0, s0, sa)
S.transition_add(s0, s1, sc)
S.transition_add(s1, s1, sd)
S.transition_add(s1, s0, sb)
S.transition_add(s1, s2, sa)
S.transition_add(s2, s2, sb)
S.transition_add(s2, s0, sc)

print(time.time())
S.supervisor_reduction(G, 'a')
print(time.time())

#PAG 113 FIG 5.2 (5.1.2a)

G = Automaton()
S = Automaton()

g0 = G.state_add('0', marked = True, initial = True)
g1 = G.state_add('1', False)
g2 = G.state_add('2', False)
g3 = G.state_add('3', False)
g4 = G.state_add('4', False)

ga = G.event_add('a', False, True)
gb = G.event_add('b', False, True)
gc = G.event_add('c', False, True)
gd = G.event_add('d', True, True)

G.transition_add(g0, g1, gb)
G.transition_add(g0, g3, ga)
G.transition_add(g0, g4, gc)
G.transition_add(g1, g2, gb)
G.transition_add(g2, g0, ga)
G.transition_add(g3, g2, ga)
G.transition_add(g3, g0, gd)
G.transition_add(g4, g0, ga)
G.transition_add(g4, g3, gd)


s0 = S.state_add('0', marked = True, initial = True)
s1 = S.state_add('1', True)
s2 = S.state_add('2', True)
s3 = S.state_add('3', True)

sa = S.event_add('a', False,True)
sb = S.event_add('b', False, True)
sc = S.event_add('c', False, True)
sd = S.event_add('d', True, True)

S.transition_add(s0, s1, sb)
S.transition_add(s0, s3, sa)
S.transition_add(s0, s2, sc)
S.transition_add(s1, s2, sb)
S.transition_add(s2, s0, sa)
S.transition_add(s3, s0, sd)
S.transition_add(s3, s2, sa)

print(time.time())
S.supervisor_reduction(G, 'a')
print(time.time())


######
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

R.supervisor_reduction(g1, 'a')


##second test minimize
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


q0 = g.state_add('q0', x=50, y=150, marked=False, initial=True)
q1 = g.state_add('q1', x=250, y=150, marked=False)
q12 = g.state_add('q12', x=450, y=150, marked=False)
q13 = g.state_add('q13', x=250, y=400, marked=False)
q2 = g.state_add('q2', x=450, y=400, marked=False)
q123 = g.state_add('q123', x=650, y=150, marked=True)

a = g.event_add('a', True, True)
b = g.event_add('b', False, True)
c = g.event_add('c', True, False)


g.transition_add(q0, q0, c)
g.transition_add(q0, q0, b)
g.transition_add(q0, q1, a)
g.transition_add(q1, q12, b)
g.transition_add(q1, q13, c)
g.transition_add(q1, q1, a)
g.transition_add(q12, q1, a)
g.transition_add(q12, q2, b)
g.transition_add(q12, q123, c)
g.transition_add(q123, q1, a)
g.transition_add(q123, q2, b)
g.transition_add(q123, q13, c)
g.transition_add(q13, q1, a)
g.transition_add(q13, q2, b)
g.transition_add(q13, q13, c)
g.transition_add(q2, q2, b)
g.transition_add(q2, q1, a)
g.transition_add(q2, q13, c)

print(g)
y = g.minimize()
print(y)

#first test minimize
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
##################

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
