import random

from machine.automaton import Event, State, Transition, Automaton


class AGGeneAutomaton(Automaton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_pool = list()  #  Events that may be used by the Gene

    def mutate(self, prob):
        pass

    def crossover(self, other):
        pass

class AGGenomeAutomaton:
    def __init__(self, plant_automata, min_genes=1, max_genes=3, max_states=3, transition_ratio=0.5):
        self.genes = list()
        num_genes = random.randint(min_genes, max_genes)
        for i in range(0, num_genes):
            gene = AGGeneAutomaton()

            # pick a number of donating plant automata and copy their events to the
            # gene's event_pool
            random.shuffle(plant_automata)
            donating_automata = random.randint(1, len(plant_automata))
            for j in range(0, donating_automata):
                for event in plant_automata[j].events:
                    gene.event_pool.append(event.clone())

            # create a 'random' specification using the event_pool

            # States:
            num_states = random.randint(2, max_states)
            for j in range(0, num_states):
                gene.state_add(marked=True, initial=(j == 0))

            # Transitions:
            # Max transitions if non-deterministic: are S*S*E --> S*E self-loops + S*(S-1)*E all-with-all
            # Max transitions if deterministic: S*E
            for event in gene.event_pool:
                first = True
                for src_state in gene.states:
                    if random.uniform(0, 1.0) < transition_ratio:
                        if first:
                            first = False
                            event = gene.event_add_copy(event)  # Changing iterator
                            trg_state = random.choice(list(gene.states))  # TODO, create list once
                            gene.transition_add(src_state, trg_state, event)
            gene.trim(True)
            self.genes.append(gene)

    def __str__(self):
        s = list()
        for gene in self.genes:
            s.append(str(gene))
        return "\n________________\n".join(s)


    def mutate(self, prob):
        for gene in self.genes:
            gene.mutate(prob)

    def crossover(self, other, prob):
        pass

class GAPopulation:
    def __init__(self, plant_automata, pop=4, *args, **kwargs):
        self.individuals = [AGGenomeAutomaton(plant_automata, *args, **kwargs) for i in range(0, pop)]

    def __str__(self):
        s = list()
        for ind in self.individuals:
            s.append(str(ind))
        return "\n=====================\n".join(s)


class GABase:
    def __init__(self, plant_automata, *args, **kwargs):
        self.plant_automata = list(plant_automata)  # Clone the list
        self.kwargs = kwargs
        self.args = args

    def initialize(self):
        self.population = GAPopulation(self.plant_automata, *self.args, **self.kwargs)

    def done(self):
        pass

    def step(self):
        pass

    def evolve():
        self.initialize()
        while self.done() == False:
            self.step()


# Test
g1 = Automaton()
a1 = g1.event_add('a1', controllable=True, observable=True)
b1 = g1.event_add('b1', controllable=False, observable=True)
s1 = g1.state_add(marked=True, initial=True)
s2 = g1.state_add(marked=False)
g1.transition_add(s1, s2, a1)
g1.transition_add(s2, s1, b1)

g2 = Automaton()
a2 = g2.event_add('a2', controllable=True, observable=True)
b2 = g2.event_add('b2', controllable=False, observable=True)
s1 = g2.state_add(marked=True, initial=True)
s2 = g2.state_add(marked=False)
g2.transition_add(s1, s2, a2)
g2.transition_add(s2, s1, b2)

g3 = Automaton()
a3 = g3.event_add('a3', controllable=True, observable=True)
b3 = g3.event_add('b3', controllable=False, observable=True)
c3 = g3.event_add('c3', controllable=False, observable=True)
s1 = g3.state_add(marked=True, initial=True)
s2 = g3.state_add(marked=False)
s3 = g3.state_add(marked=False)
g3.transition_add(s1, s2, a3)
g3.transition_add(s2, s1, b3)
g3.transition_add(s1, s3, c3)
g3.transition_add(s3, s2, c3)

ga = GABase([g1, g2, g3])
ga.initialize()
#~ print(ga.population)

print("END")

