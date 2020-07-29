from machine import automata

###############################################################################
# AUTOMATA OPERATIONS
###############################################################################


###############################################################################
# Composition
###############################################################################

def sync(g1, g2):
    """ This function returns the accessible part of the synchronous composition. Instead of calculating all composed
    states and then calculate the accessible part, we only add accessible states to the output."""

    st_out = {}

    states_to_be_visited_in_g1 = list()
    states_to_be_visited_in_g2 = list()
    states_to_be_visited_in_g1.append(g1.initial_state)
    states_to_be_visited_in_g2.append(g2.initial_state)
    s1 = states_to_be_visited_in_g1.pop()
    s2 = states_to_be_visited_in_g2.pop()

    state_flag = dict()
    current_state = automata.State(s1.name + '|' + s2.name, s1.mark and s2.mark)
    state_flag[s1.name + '|' + s2.name] = False

    state_out_dict = dict()
    state_out_dict[s1.name + '|' + s2.name] = current_state

    out_initial_state = current_state

    common_events = g1.events_set().intersection(g2.events_set())  # set of events which are in both alphabets
    alphabet = set(g1.events_set())
    alphabet.update(g2.events_set())

    for ev in alphabet:
        if ev in common_events:
            ev.common = True
        else:
            ev.common = False

    while s1:

        st_out[current_state] = {}

        ev_exclusive_set_2 = set(g2.transitions[s2].keys()) - common_events

        for ev1 in g1.transitions[s1].keys():

            if not ev1.common:
                    if g1.transitions[s1][ev1].name + '|' + s2.name not in state_out_dict:
                        state_out_dict[g1.transitions[s1][ev1].name + '|' + s2.name] = \
                            automata.State(
                                g1.transitions[s1][ev1].name + '|' + s2.name,
                                g1.transitions[s1][ev1].mark and s2.mark)
                        states_to_be_visited_in_g1.append(g1.transitions[s1][ev1])
                        states_to_be_visited_in_g2.append(s2)
                    st_out[current_state][ev1] = state_out_dict[g1.transitions[s1][ev1].name + '|' + s2.name]

            elif ev1 in g2.transitions[s2].keys():
                if g1.transitions[s1][ev1].name + '|' + g2.transitions[s2][ev1].name not in state_out_dict:
                    state_out_dict[g1.transitions[s1][ev1].name + '|' + g2.transitions[s2][ev1].name] = \
                        automata.State(g1.transitions[s1][ev1].name + '|' + g2.transitions[s2][ev1].name,
                                       g1.transitions[s1][ev1].mark and g2.transitions[s2][ev1].mark)
                    states_to_be_visited_in_g1.append(g1.transitions[s1][ev1])
                    states_to_be_visited_in_g2.append(g2.transitions[s2][ev1])
                st_out[current_state][ev1] = state_out_dict[g1.transitions[s1][ev1].name + '|' +
                                                            g2.transitions[s2][ev1].name]

        for ev2 in ev_exclusive_set_2:
            if s1.name + '|' + g2.transitions[s2][ev2].name not in state_out_dict:
                state_out_dict[s1.name + '|' + g2.transitions[s2][ev2].name] = \
                    automata.State(
                        s1.name + '|' + g2.transitions[s2][ev2].name,
                        s1.mark and g2.transitions[s2][ev2].mark)
                states_to_be_visited_in_g1.append(s1)
                states_to_be_visited_in_g2.append(g2.transitions[s2][ev2])
            st_out[current_state][ev2] = state_out_dict[s1.name + '|' + g2.transitions[s2][ev2].name]

        try:
            s1 = states_to_be_visited_in_g1.pop()
            s2 = states_to_be_visited_in_g2.pop()
            current_state = state_out_dict[s1.name + '|' + s2.name]
        except IndexError:
            s1 = None
            s2 = None

    out = automata.Automaton(st_out, out_initial_state)

    return out


###############################################################################
# Accessible
###############################################################################

def accessible(g_to_be_accessible):
    """ Return an automaton in which all states are reachable from the initial state."""

    non_accessible_states = g_to_be_accessible.states_set() - g_to_be_accessible.initial_state
    states_to_be_visited = g_to_be_accessible.initial_state.copy()
    visiting_state = states_to_be_visited.pop()

    for s in g_to_be_accessible.transitions.keys():
        s.visited = False

    while visiting_state:
        for state in g_to_be_accessible.transitions[visiting_state].values():
            non_accessible_states.discard(state)

            if not state.visited:

                state.visited = True
                states_to_be_visited.add(state)

        try:
            visiting_state = states_to_be_visited.pop()
        except KeyError:
            visiting_state = None

    g_to_be_accessible.remove_states(non_accessible_states)

    return


###############################################################################
# Coaccessible
###############################################################################

def coaccessible(g_to_be_coaccessible):
    """ Remove states which, does not have any string which could reach any marked state"""

    states_to_be_visited = set()
    non_coaccessible_states = g_to_be_coaccessible.states_set()
    origin_states_of = dict()
    origin_states_of[g_to_be_coaccessible.initial_state] = []

    # In these two following "for" loops, we calculate a "inversely" oriented automata
    # Instead of addressing the destination states, we address the "origin states" of all states.
    # Though we can calculate the coaccessible part similarly as the accessible, starting from marked states instead of
    # the initial state.

    for s in g_to_be_coaccessible.transitions.keys():
        s.coaccessible = s.mark
        origin_states_of[s] = []

    for s in g_to_be_coaccessible.transitions.keys():
        if s.coaccessible:
            non_coaccessible_states.discard(s)
        else:
            for s2 in g_to_be_coaccessible.transitions[s].values():
                if s2 != s:
                    if s2.coaccessible:
                        states_to_be_visited.add(s)
                        states_to_be_visited.discard(s2)
                        s.coaccessible = True
                    else:
                        origin_states_of[s2].append(s)

    non_coaccessible_states -= states_to_be_visited
    visiting_state = states_to_be_visited.pop()

    while visiting_state:

        for state_of_origin in origin_states_of[visiting_state]:
            if not state_of_origin.coaccessible:
                states_to_be_visited.add(state_of_origin)
                state_of_origin.coaccessible = True
                non_coaccessible_states.discard(state_of_origin)

        try:
            visiting_state = states_to_be_visited.pop()
        except KeyError:
            visiting_state = None

    g_to_be_coaccessible.remove_states(non_coaccessible_states)

    return


#######################################################################################################################
# TRIM
#######################################################################################################################

def trim(to_be_trim):
    """ This function is equivalent to execute the accessible and the coaccessible function, however, instead of
    calling them, these functions were grouped in order to reach better computation time. To know more details of the
    implementation, go to the accessible or coaccessible functions."""
    ###################################################################################################################
    # ACCESSIBLE
    ###################################################################################################################

    # variable of coaccessible function (used later)
    origin_states_of = dict()
    origin_states_of[to_be_trim.initial_state] = []
    states_to_be_visited_co = set()
    non_coaccessible_states = to_be_trim.states_set()

    # variable of accessible function
    non_accessible_states = to_be_trim.states_set()
    non_accessible_states.discard(to_be_trim.initial_state)
    states_to_be_visited = set()
    visiting_state = to_be_trim.initial_state

    dict_state_flag = dict()

    for s in to_be_trim.transitions.keys():
        dict_state_flag[s] = False
        s.coaccessible = s.mark
        origin_states_of[s] = []
        if s.mark:
            non_coaccessible_states.discard(s)

    while visiting_state:
        for state in to_be_trim.transitions[visiting_state].values():
            non_accessible_states.discard(state)

            if not dict_state_flag[state]:
                dict_state_flag[state] = True
                states_to_be_visited.add(state)

            # coaccessible code part:
            origin_states_of[state].append(visiting_state)
            if state.coaccessible:
                visiting_state.coaccessible = True
                states_to_be_visited_co.add(visiting_state)
                # non_coaccessible_states.discard(visiting_state)

        try:
            visiting_state = states_to_be_visited.pop()
        except KeyError:
            visiting_state = 0

    ####################################################################################################################
    # COACCESIBLE
    ####################################################################################################################

    non_coaccessible_states -= states_to_be_visited_co

    if states_to_be_visited_co:
        visiting_state = states_to_be_visited_co.pop()

    while visiting_state:

        for state_of_origin in origin_states_of[visiting_state]:
            if not state_of_origin.coaccessible:

                states_to_be_visited_co.add(state_of_origin)
                state_of_origin.coaccessible = True
                non_coaccessible_states.discard(state_of_origin)

        try:
            visiting_state = states_to_be_visited_co.pop()
        except KeyError:
            visiting_state = None

    non_coaccessible_states.update(non_accessible_states)
    to_be_trim.remove_states(non_coaccessible_states)

    return


###############################################################################
# SupC
###############################################################################


def supc(k, g):
    """ This function is based on the classical implementation of the SupC algorithm"""

    breaking_bad = round(0.01 * len(k.transitions.keys()) + 0.6)  # This is a variable to break the loop to remove bad
    # states, as it enhance the performance of the algorithm... basically, you don´t need to run through all states
    # to delete some of them... and by deleting and trimming when you reach a significant amount of bad states (1%),
    # you reduce the number of states to be visited significantly. This is a kind of minimization problem where there is
    # a optimum amount of bad states to "break" the loop. However, I did some runs and roughly determined 1% of the
    # states of K.

    sup = automata.Automaton(k.transitions, k.initial_state)
    flag_bad_state = True
    set_bad_state = set()
    n_bad_states_in_sup = 0

    while flag_bad_state:
        flag_bad_state = False
        states_to_be_visited_in_sup = list()
        states_to_be_visited_in_sup.append(sup.initial_state)
        states_to_be_visited_in_g = list()
        states_to_be_visited_in_g.append(g.initial_state)
        flag_end = True
        visiting_state_in_sup = states_to_be_visited_in_sup.pop()
        visiting_state_in_g = states_to_be_visited_in_g.pop()

        visited_states_set = set()

        while flag_end:

            for ev in g.transitions[visiting_state_in_g].keys():

                if ev in sup.transitions[visiting_state_in_sup].keys():
                    nxt_state = sup.transitions[visiting_state_in_sup][ev]
                    if nxt_state not in visited_states_set:
                        visited_states_set.add(nxt_state)
                        states_to_be_visited_in_sup.append(nxt_state)
                        states_to_be_visited_in_g.append(g.transitions[visiting_state_in_g][ev])
                else:
                    if not ev.ctrl and visiting_state_in_sup not in set_bad_state:

                        n_bad_states_in_sup += 1
                        set_bad_state.add(visiting_state_in_sup)
                        flag_bad_state = True
                        if n_bad_states_in_sup == breaking_bad:
                            break

            if n_bad_states_in_sup == breaking_bad:
                n_bad_states_in_sup = 0
                break

            try:
                visiting_state_in_sup = states_to_be_visited_in_sup.pop()
                visiting_state_in_g = states_to_be_visited_in_g.pop()
            except IndexError:
                flag_end = False

        if flag_bad_state:
            sup.remove_states(set_bad_state)  # remove bad states and all transitions to it
            set_bad_state = set()
            trim(sup)

    return sup


def supc2(g2, g1):
    """ This function is the faster calculation of the supervisor we got. The parameters are SPEC_global and G_global.
    The key to its performance is to identify bad states even before than creating them. So, instead of calculating the
    all K and then search a bad state and exclude it and trim (and do it again, and again)... We identify bad states
    in the process of calculating the composition of E_global and G_global and do not create them. Also, the loops run
    through accessible states only, so we do not calculate trim, we only calculate coaccessible states at last."""

    st_out = {}  # dictionary for transitions of the supervisor

    # g1 = GLOBAL PLANT
    # g2 = GLOBAL SPEC

    states_to_be_visited_in_g1 = list()
    states_to_be_visited_in_g2 = list()

    s1 = g1.initial_state
    s2 = g2.initial_state

    current_state_out = automata.State(s1.name + '|' + s2.name, s1.mark and s2.mark)

    state_out_dict = dict()
    state_out_dict[s1.name + '|' + s2.name] = current_state_out

    out_initial_state = current_state_out

    common_events = g1.events_set().intersection(g2.events_set())

    alphabet = set(g1.events_set())
    print(alphabet)
    alphabet.update(g2.events_set())

    for ev in alphabet:
        if ev in common_events:
            ev.common = True
        else:
            ev.common = False

    while s1:  # The while is used instead of the for loop. The reason is that we only visit accessible states,
            # so, along the algorithm, we determine the next accessible states do be visited.

        st_out[current_state_out] = {}

        for current_ev in g1.transitions[s1].keys():

            if not current_ev.common:
                if g1.transitions[s1][current_ev].name + '|' + s2.name not in state_out_dict:
                    state_out_dict[g1.transitions[s1][current_ev].name + '|' + s2.name] = \
                        automata.State(
                            g1.transitions[s1][current_ev].name + '|' + s2.name,
                            g1.transitions[s1][current_ev].mark and s2.mark)
                    states_to_be_visited_in_g1.append(g1.transitions[s1][current_ev])
                    states_to_be_visited_in_g2.append(s2)
                st_out[current_state_out][current_ev] = state_out_dict[g1.transitions[s1][current_ev].name + '|' +
                                                                       s2.name]

            elif current_ev in g2.transitions[s2].keys():
                # check if destination state is bad state
                flag_bad_state = False
                for nxt_ev in g1.transitions[g1.transitions[s1][current_ev]].keys():
                    if not nxt_ev.ctrl and nxt_ev.common and nxt_ev not in \
                            g2.transitions[g2.transitions[s2][current_ev]].keys():

                        flag_bad_state = True
                        break
                if not flag_bad_state:  # if destination state is bad state, it is not included
                                        # in the output transitions
                    if g1.transitions[s1][current_ev].name + '|' + g2.transitions[s2][current_ev].name \
                       not in state_out_dict:
                        state_out_dict[g1.transitions[s1][current_ev].name + '|' + g2.transitions[s2][current_ev].name]\
                            = automata.State(g1.transitions[s1][current_ev].name + '|' +
                                             g2.transitions[s2][current_ev].name,
                                             g1.transitions[s1][current_ev].mark and
                                             g2.transitions[s2][current_ev].mark)
                        states_to_be_visited_in_g1.append(g1.transitions[s1][current_ev])
                        states_to_be_visited_in_g2.append(g2.transitions[s2][current_ev])
                    st_out[current_state_out][current_ev] = state_out_dict[g1.transitions[s1][current_ev].name + '|' +
                                                                           g2.transitions[s2][current_ev].name]

        try:
            s1 = states_to_be_visited_in_g1.pop()
            s2 = states_to_be_visited_in_g2.pop()
            current_state_out = state_out_dict[s1.name + '|' + s2.name]

        except IndexError:
            s1 = None
            s2 = None

    supervisor = automata.Automaton(st_out, out_initial_state)

    coaccessible(supervisor)  # the supervisor is already accessible, we only calculate coaccessible

    return supervisor


def supc3(g2, g1):
    """ This function is an alternative do supc2 where a list of SPEC_local, and a list of G_local are passed as
    parameters. Its performance can be enhanced."""

    st_out = {}

    # g1 = PLANT
    # g2 = SPEC

    states_to_be_visited_in_g1 = list()
    states_to_be_visited_in_g2 = list()
    g_initial_states_list = list()
    g_events_set = set()
    for g_i in g1:
        g_initial_states_list.append(g_i.initial_state)
        g_events_set.update(g_i.events_set())

    e_initial_states_list = list()
    e_events_set = set()
    events_in_more_than_one_spec = set()
    for spec_i in g2:
        e_initial_states_list.append(spec_i.initial_state)
        for event_i in spec_i.events_set():
            if event_i in e_events_set:
                events_in_more_than_one_spec.add(event_i)
        e_events_set.update(spec_i.events_set())

    states_to_be_visited_in_g1.append(g_initial_states_list)
    states_to_be_visited_in_g2.append(e_initial_states_list)
    s1 = states_to_be_visited_in_g1.pop()
    s2 = states_to_be_visited_in_g2.pop()

    state_name_string = str()
    state_mark = True

    for state_i in e_initial_states_list:
        state_name_string += '|' + state_i.name
        state_mark = state_mark and state_i.mark

    for state_i in g_initial_states_list:
        state_name_string += '|' + state_i.name
        state_mark = state_mark and state_i.mark

    current_state_out = automata.State(state_name_string, state_mark)

    state_out_dict = dict()
    state_out_dict[state_name_string] = current_state_out

    out_initial_state = current_state_out

    common_events = g_events_set.intersection(e_events_set)

    while s1:
        while s2:

            st_out[current_state_out] = {}

            active_events_g = set()
            active_events_spec = set()

            for g_i, s_i in zip(g1, s1):
                for event_g_i in g_i.transitions[s_i].keys():
                    active_events_g.add(event_g_i)

            for spec_i, s_i in zip(g2, s2):
                for event_e_i in spec_i.transitions[s_i].keys():
                    active_events_spec.add(event_e_i)

            for ev1 in active_events_g:

                if ev1 not in common_events:
                    state_name_string = str()
                    state_mark = True
                    for state_i in s2:
                        state_name_string += '|' + state_i.name
                        state_mark = state_mark and state_i.mark
                    for state_i, g_i in zip(s1, g1):

                        if ev1 in g_i.transitions[state_i].keys():
                            state_name_string += '|' + g_i.transitions[state_i][ev1].name
                            state_mark = state_mark and g_i.transitions[state_i][ev1].mark
                        else:
                            state_name_string += '|' + state_i.name
                            state_mark = state_mark and state_i.mark

                    if state_name_string not in state_out_dict:
                        state_out_dict[state_name_string] = automata.State(state_name_string, state_mark)
                        state_to_be_visited_gather_s1 = list()
                        for state_i, g_i in zip(s1, g1):
                                if ev1 in g_i.transitions[state_i].keys():
                                    state_to_be_visited_gather_s1.append(g_i.transitions[state_i][ev1])
                                else:
                                    state_to_be_visited_gather_s1.append(state_i)
                        states_to_be_visited_in_g1.append(state_to_be_visited_gather_s1)
                        states_to_be_visited_in_g2.append(s2)
                    st_out[current_state_out][ev1] = state_out_dict[state_name_string]

                elif ev1 in active_events_spec:
                    # check if destination state is bad state
                    flag_bad_state_one = False
                    next_active_events_g = set()
                    next_active_events_spec = set()
                    for spec_i, s_i in zip(g2, s2):
                        if ev1 in spec_i.transitions[s_i].keys():
                            next_active_events_spec.update(set(spec_i.transitions[spec_i.transitions[s_i][ev1]].keys()))
                        else:
                            next_active_events_spec.update(set(spec_i.transitions[s_i].keys()))
                    for g_i, s_i in zip(g1, s1):
                        if ev1 in g_i.transitions[s_i].keys():
                            next_active_events_g.update(set(g_i.transitions[g_i.transitions[s_i][ev1]].keys()))
                        else:
                            next_active_events_g.update(set(g_i.transitions[s_i].keys()))

                    next_active_events_g -= next_active_events_spec
                    for event_1 in next_active_events_g.intersection(common_events):
                        if not event_1.ctrl:

                            flag_bad_state_one = True
                            break
                    if not flag_bad_state_one:
                        state_name_string = str()
                        state_mark = True
                        for state_i, spec_i in zip(s2, g2):
                            if ev1 in spec_i.transitions[state_i].keys():
                                state_name_string += '|' + spec_i.transitions[state_i][ev1].name
                                state_mark = state_mark and spec_i.transitions[state_i][ev1].mark
                            else:
                                state_name_string += '|' + state_i.name
                                state_mark = state_mark and state_i.mark
                        for state_i, g_i in zip(s1, g1):
                            if ev1 in g_i.transitions[state_i].keys():
                                state_name_string += '|' + g_i.transitions[state_i][ev1].name
                                state_mark = state_mark and g_i.transitions[state_i][ev1].mark
                            else:
                                state_name_string += '|' + state_i.name
                                state_mark = state_mark and state_i.mark
                        if state_name_string not in state_out_dict:
                            state_out_dict[state_name_string] = \
                                automata.State(state_name_string, state_mark)
                            state_to_be_visited_gather_s1 = list()
                            state_to_be_visited_gather_s2 = list()
                            for state_i, spec_i in zip(s2, g2):
                                if ev1 in spec_i.transitions[state_i].keys():
                                    state_to_be_visited_gather_s2.append(spec_i.transitions[state_i][ev1])
                                else:
                                    state_to_be_visited_gather_s2.append(state_i)
                            for state_i, g_i in zip(s1, g1):
                                if ev1 in g_i.transitions[state_i].keys():
                                    state_to_be_visited_gather_s1.append(g_i.transitions[state_i][ev1])
                                else:
                                    state_to_be_visited_gather_s1.append(state_i)

                            states_to_be_visited_in_g1.append(state_to_be_visited_gather_s1)
                            states_to_be_visited_in_g2.append(state_to_be_visited_gather_s2)

                        st_out[current_state_out][ev1] = state_out_dict[state_name_string]

            try:
                s1 = states_to_be_visited_in_g1.pop()
                s2 = states_to_be_visited_in_g2.pop()

                state_name_string = str()
                for state_i in s2:
                    state_name_string += '|' + state_i.name

                for state_i in s1:
                    state_name_string += '|' + state_i.name

                current_state_out = state_out_dict[state_name_string]

            except IndexError:
                s1 = None
                s2 = None

    sup = automata.Automaton(st_out, out_initial_state)
    coaccessible(sup)

    return sup
