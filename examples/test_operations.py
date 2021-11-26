#!/usr/bin/python

import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

import pluggins
from machine.automaton import Automaton

def test_isomorphic_check():
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

    print(G1.isomorphic_check(G2, verbose=True) == True and 'Pass' or 'Fail')

    G2a = G2.clone()
    G2a_q4 = G2a.state_add()
    print(G1.isomorphic_check(G2a) == False and 'Pass' or 'Fail')

def test_supervisor_reduction():
    """Execute from same dir as main.py"""

    gpath = 'examples/reduction/Unreliable Machine - NOK/P'  # Plant
    spath = 'examples/reduction/Unreliable Machine - NOK/SUP' # Supervisor
    ncpath = 'examples/reduction/Unreliable Machine - NOK/NCONT'  # Uncontrolable events
    G = Automaton()
    G.grail_import(gpath, ncpath)
    S = Automaton()
    S.grail_import(spath, ncpath)

    print('S', len(S.states))
    print('G', len(G.states))

    S.minimize()
    print('min(S)', len(S.states))
    #~ G.minimize()  # stucking here!
    #~ print('min(G)', len(G.states))
    S.state_rename_sequential()

    Sr = S.supervisor_reduction(G, 'a')
    Sr.state_rename_sequential()

    Sr_G = Sr.synchronization(G)
    Sr_G.minimize()
    Sr_G.state_rename_sequential()

    print(S.isomorphic_check(Sr_G, verbose=True))

    #~ print('min(S):\n', S)

    #~ print('min(S2):\n', S2)
    from gui import Application, AutomatonEditor

    def startup(self):
        V = 140
        for nm, A in [('min(S)', S), ('min(Sr_G)', Sr_G), ('Sr', Sr), ('G', G)]:
            x, y = V, V
            for state in A.states:
                state.x = x
                state.y = y
                x = x + V
                if x > (9*V):
                    x = V
                    y = y + V
            editor = AutomatonEditor(A, self)
            self.window.add_tab(editor, nm)
            editor.connect('nadzoru-editor-change', self.on_editor_change)

    application = Application(startup_callback=startup)
    application.run(sys.argv)


test_supervisor_reduction()
