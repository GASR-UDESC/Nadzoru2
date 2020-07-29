import time
# import sys
from machine import automata
from machine import operations

# import psutil

#######################################################################################################################
# Cluster Tool Example
#######################################################################################################################

#######################################################################################################################
# Plants
#######################################################################################################################


""" References to this example:

    Su, R., van Schuppen, J., Rooda, J., 2012. The synthesis of time optimal supervisors by using heaps-of-pieces. IEEE
Transactions on Automatic Control 57 (1), 105–118.

    Lucas V.R. Alves, Lucas R.R. Martins, Patrícia N. Pena. UltraDES - A Library for Modeling, Analysis and Control of 
Discrete Event Systems**This work was supported by Capes - Brazil, CNPq and FAPEMIG., IFAC-PapersOnLine, Volume 50, 
Issue 1, 2017.
"""


s = list()

for n in range(4):

    if not n:
        s.append(automata.State(str(n), True))
    else:
        s.append(automata.State(str(n)))

clusters = 5

# Robots Plants

alphabet = dict()
alphabet_uncontrollable = dict()

n_automata = clusters
robot_transitions = dict()
robot_initial_state = list()
robot = list()
I_Be_C = dict()
F_Be_C = dict()
I_C_Be = dict()
F_C_Be = dict()
I_C_Bd = dict()
F_C_Bd = dict()
I_Bd_Be = dict()
F_Bd_Be = dict()
for i in range(n_automata):
    I_Be_C[i] = automata.Event('I_Be_C' + str(i), True)
    F_Be_C[i] = automata.Event('F_Be_C' + str(i))
    I_C_Be[i] = automata.Event('I_C_Be' + str(i), True)
    F_C_Be[i] = automata.Event('F_C_Be' + str(i))
    I_C_Bd[i] = automata.Event('I_C_Bd' + str(i), True)
    F_C_Bd[i] = automata.Event('F_C_Bd' + str(i))
    I_Bd_Be[i] = automata.Event('I_Bd_Be' + str(i), True)
    F_Bd_Be[i] = automata.Event('F_Bd_Be' + str(i))
    if i == n_automata-1:  # last robot
        alphabet[i] = {0: I_Be_C[i], 1: F_Be_C[i], 2: I_C_Be[i], 3: F_C_Be[i]}
        robot_transitions[i] = dict()
        robot_transitions[i] = {s[0]: {alphabet[i][0]: s[1], alphabet[i][2]: s[2]},
                                s[1]: {alphabet[i][1]: s[0]},
                                s[2]: {alphabet[i][3]: s[0]}}
        robot_initial_state.insert(i, s[0])
    else:
        alphabet[i] = {0: I_Be_C[i], 1: F_Be_C[i], 2: I_C_Bd[i], 3: F_C_Bd[i],
                       4: I_Bd_Be[i], 5: F_Bd_Be[i]}
        robot_transitions[i] = dict()
        robot_transitions[i] = {s[0]: {alphabet[i][0]: s[1], alphabet[i][2]: s[2], alphabet[i][4]: s[3]},
                                s[1]: {alphabet[i][1]: s[0]},
                                s[2]: {alphabet[i][3]: s[0]},
                                s[3]: {alphabet[i][5]: s[0]}}
        robot_initial_state.insert(i, s[0])

    robot.insert(i, automata.Automaton(robot_transitions[i], robot_initial_state[i]))

# "Processing Chambers" Plants

alphabet2 = dict()
alphabet2_uncontrollable = dict()

n_automata = clusters

chamber_transitions = dict()
chamber_initial_state = list()
chamber = list()
I_C = dict()
F_C = dict()
for i in range(n_automata):
    I_C[i] = automata.Event('I_C', True)
    F_C[i] = automata.Event('F_C')
    alphabet2[i] = {0: I_C[i], 1: F_C[i]}
    chamber_transitions[i] = {s[0]: {alphabet2[i][0]: s[1]},
                              s[1]: {alphabet2[i][1]: s[0]}}
    chamber_initial_state.insert(i, s[0])
    chamber.insert(i, automata.Automaton(chamber_transitions[i], chamber_initial_state[i]))


########################################################################################################################
# Specifications
########################################################################################################################

# Robot & Chamber
alphabet3 = dict()
alphabet3_uncontrollable = dict()

n_automata = clusters

erc_transitions = dict()
erc_initial_state = list()
erc = list()
for i in range(n_automata):
    if i == n_automata-1:
        alphabet3[i] = {0: I_C_Be[i], 1: F_Be_C[i], 2: I_C[i], 3: F_C[i]}
        erc_transitions[i] = {s[0]: {alphabet3[i][1]: s[1], alphabet3[i][3]: s[2]},
                              s[1]: {alphabet3[i][2]: s[0]},
                              s[2]: {alphabet3[i][0]: s[0]}}
        erc_initial_state.insert(i, s[0])
    else:
        alphabet3[i] = {0: I_C_Bd[i], 1: F_Be_C[i], 2: I_C[i], 3: F_C[i]}
        erc_transitions[i] = {s[0]: {alphabet3[i][1]: s[1], alphabet3[i][3]: s[2]},
                              s[1]: {alphabet3[i][2]: s[0]},
                              s[2]: {alphabet3[i][0]: s[0]}}
        erc_initial_state.insert(i, s[0])
    erc.insert(i, automata.Automaton(erc_transitions[i], erc_initial_state[i]))


# Robot i & Robot i + 1

alphabet4 = dict()
alphabet4_uncontrollable = dict()

n_automata = clusters-1

err_transitions = dict()
err_initial_state = list()
err = list()

for i in range(n_automata):
    if i == n_automata-1:
        alphabet4[i] = {0: I_Be_C[i+1], 1: F_C_Bd[i], 2: I_Bd_Be[i], 3: F_C_Be[i+1]}
        err_transitions[i] = {s[0]: {alphabet4[i][1]: s[1], alphabet4[i][3]: s[2]},
                              s[1]: {alphabet4[i][0]: s[0]},
                              s[2]: {alphabet4[i][2]: s[0]}}
        err_initial_state.insert(i, s[0])
    else:
        alphabet4[i] = {0: I_Be_C[i+1], 1: F_C_Bd[i], 2: I_Bd_Be[i], 3: F_Bd_Be[i+1]}
        err_transitions[i] = {s[0]: {alphabet4[i][1]: s[1], alphabet4[i][3]: s[2]},
                              s[1]: {alphabet4[i][0]: s[0]},
                              s[2]: {alphabet4[i][2]: s[0]}}
        err_initial_state.insert(i, s[0])
    err.insert(i, automata.Automaton(err_transitions[i], err_initial_state[i]))


tic = time.clock()

g = operations.sync(robot[0], robot[1])

for automaton in robot[2:]:
    g = operations.sync(g, automaton)

for automaton in chamber:
    g = operations.sync(g, automaton)

toc = time.clock()

print("Tempo sync G: %s" % (toc - tic))

# print("Sync 1", g.transitions)


print("G states number:", len(g.states_set()))
print("G events number:", len(g.events_set()))
print("G transitions number:", g.transitions_number())


e = operations.sync(erc[0], erc[1])

for automaton in erc[2:]:
    e = operations.sync(e, automaton)

for automaton in err:
    e = operations.sync(e, automaton)


print("E states number:", len(e.states_set()))
print("E events number:", len(e.events_set()))
print("E transitions number:", e.transitions_number())


########################################################################################################################
# Using SupC
########################################################################################################################

# print("starting K3")
#
# tic = time.clock()
#
# k = operations.sync(e, g)
#
# toc = time.clock()
#
# print("Tempo: %s" % (toc - tic))
# # print("K3:", k.transitions)
# print("K3 states number:", len(k.states_set()))
# print("K3 events number:", len(k.events_set()))
# print("K3 transitions number:", k.transitions_number())
#
#
# print("starting S")
#
# tic = time.clock()
#
# s = operations.supc(k, g)
#
# toc = time.clock()
#
# print("Tempo: %s" % (toc - tic))
#
# # print("S", s.transitions)
# print("S states number:", len(s.states_set()))
# print("S transitions number:", s.transitions_number())

########################################################################################################################
# Using SupC 2
########################################################################################################################

print("starting supc 2")

tic = time.clock()

s2 = operations.supc2(e, g)

toc = time.clock()

print("Time of computation: %s" % (toc - tic))
print("S2 states number:", len(s2.states_set()))
print("S2 transitions number:", s2.transitions_number())


########################################################################################################################
# Using SupC 3
########################################################################################################################

# print("starting supc 3")
#
# G_list = list()
# for g_i in robot:
#     G_list.append(g_i)
# for g_i in chamber:
#     G_list.append(g_i)
#
# E_list = list()
# for e_i in erc:
#     E_list.append(e_i)
# for e_i in err:
#     E_list.append(e_i)
#
#
# tic = time.clock()
#
# s3 = operations.supc3(E_list, G_list)
#
# toc = time.clock()
#
# print("Size of S:", sys.getsizeof(s3))
#
# print("Tempo: %s" % (toc - tic))
# print("S3 states number:", len(s3.states_set()))
# print("S3 transitions number:", s3.transitions_number())
