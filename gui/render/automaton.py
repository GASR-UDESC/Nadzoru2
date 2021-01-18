import cairo
import math


from machine.automata import Automaton


class AutomatonRender:
    def __init__(self):
        pass

    def draw(self, cr, automaton):
        # draw states
        for state in automaton.states:
            radius = 32
            cr.set_source_rgb(0, 0, 0)
            cr.arc(state.x, state.y, radius, 0, 2 * math.pi)
            cr.stroke()

