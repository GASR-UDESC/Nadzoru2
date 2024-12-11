import random

from machine.automaton import Event, State, Transition, Automaton

g1 = Automaton()
a1 = g1.event_add('a1', controllable=True, observable=True)
b1 = g1.event_add('b1', controllable=False, observable=True)
s1 = g1.state_add(marked=True, initial=True)
s2 = g1.state_add(marked=False)
g1.transition_add(s1, s2, a1)
g1.transition_add(s2, s1, b1)

g2 = Automaton()
a2 = g1.event_add('a2', controllable=True, observable=True)
b2 = g1.event_add('b2', controllable=False, observable=True)
s1 = g1.state_add(marked=True, initial=True)
s2 = g1.state_add(marked=False)
g2.transition_add(s1, s2, a2)
g2.transition_add(s2, s1, b2)

# ------------------------------------------------------------------------------

def AG(G, E_fix=None, max_esp=1, pop_size=100):
    if E_fix is None:
        E_fix = list()

    qtd_G = len(G)

    def mutation_v0(G):
        return G

    def crossover_sync(G1, G2):
        return Automaton.synchronization(G1, G2)


    # Initial Population
    def initial_pop():
        pop = list()
        for _ in range(pop_size):
            num_esp = random.randint(1, max_esp)
            genome = list()
            for __ in range(num_esp):
                random.shuffle(G)
                qtd = random.randint(1, qtd_G)

                if qtd == 1:
                    gene = G[0].clone()
                else:
                    gene = Automaton.synchronization(*G[:qtd])
                #~ gene = mutation_v0(gene)
                genome.append(gene)
            pop.append(genome)
        return pop

    def fitness(G):
        pass

    def evolve():
        pass








