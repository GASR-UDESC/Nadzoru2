from machine.automata import Event, State, Transition, Automaton

class ProbabilisticTransition:
    def __init__(self, *args, probability=1.0, **kwargs):
        self.probability = probability

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._probability = value
    
    def probabilistic_str(self):
        return str(self) + ": ({probability})".format(probability=self.probability)
            
    
Transition.plugin_prepend(ProbabilisticTransition)
    



