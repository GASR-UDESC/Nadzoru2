from machine.automaton import Event, State, Transition, Automaton


class ProbabilisticTransition:
    def __init__(self, *args, probability=1.0, **kwargs):
        self.probability = probability
        super().__init__(*args, **kwargs)

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._probability = value
    
    def probabilistic_str(self):
        return str(self) + ": ({probability})".format(probability=self.probability)


class ProbabilisticAutomaton:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def probabilitic_synchronization(self, *args):
        pass

Transition.plugin_prepend(ProbabilisticTransition)
Automaton.plugin_prepend(ProbabilisticAutomaton)
    



