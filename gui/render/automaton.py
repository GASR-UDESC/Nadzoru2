import cairo
import math

from machine.automata import Automaton


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_angle(cls, deg_angle):
        angle = math.pi * deg_angle / 180.0
        return cls(math.cos(angle), math.sin(angle))

    @classmethod
    def from_rad_angle(cls, angle):
        return cls(math.cos(angle), math.sin(angle))

    def __str__(self):
        return "({:.1f},{:.1f})".format(self.x, self.y)

    def __add__(self, other):
        return Point2D(self.x + other.x, self.y +  other.y)

    def __radd__(self, value):  # when this object is on the right side
        return self.__add__(value)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y

    def __sub__(self, other):
        return Point2D(self.x - other.x, self.y - other.y)

    def __rsub__(self, value):
        return self.__sub__(value)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, value):
        return Point2D(self.x * value, self.y * value)

    def __rmul__(self, value):
        return self.__mul__(value)

    def __imul__(self, value):
        self.x *= value
        self.y *= value
        return self

    def __truediv__(self, value):
        return Point2D(self.x / value, self.y / value)

    def __rtruediv__(self, value):
        return self.__truediv__(value)

    def __itruediv__(self, value):
        self.x /= value
        self.y /= value
        return self

    def mid_point(self, other):
        return (self - other)/2 + other

    def orthogonal_cw(self):
        return Point2D(self.y, -self.x)

    def orthogonal_ccw(self):
        return Point2D(-self.y, self.x)

    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def length(self): # vector norm or magnitude
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        return self / self.length()

    def set_length(self, value):
        return (self * value) / self.length()

    def rm_length(self, value):
        """if value is too large it will also swap direction. Take care in case length and value are close."""
        return self.set_length(self.length() - value)

    def add_length(self, value):
        return self.set_length(self.length() + value)

    def angle(self, origin, r=None):
        """Get the angle self is based on the origin 'origin'.
        Cairo angles increase cw (as positive y is downwards.
        a = arccos((x0*x1 + y0*y1) / (sqrt(x0**2 + y0**2) * sqrt(x1**2 + y1**2)))
        Note that we want the angle to the vector (x1, y1) =  (1,0), so
        a = acos(x0 / (sqrt(x0**2 + y0**2) * sqrt(1**2 + 0)
        a = acos(x0 / sqrt(x0**2 + y0**2) = acos(x0 / r) where r is the distance
        """
        if r is None:
            r = self.distance(origin)
        x0 = self.x - origin.x
        if self.y > origin.y:
            return math.acos(x0 / r)
        else:
            return 2*math.pi - math.acos(x0 / r)

class AutomatonRender:
    MIN_RADIUS = 32
    DOUBLE_RADIUS_GAP = 4
    TEXT_RADIUS_GAP = 4
    FONT_SIZE = 24
    TRANSITION_TEXT_SPACE = 12
    ARROW_LENGTH = 20
    ARROW_MID_HEIGHT = 5

    def __init__(self):
        pass

    def _draw_point(self, cr, V, r=0, g=0, b=0):
        cr.set_source_rgb(r, g, b)
        cr.arc(V.x, V.y, 2, 0, 2 * math.pi)
        cr.stroke()

    def write_text(self, cr, x, y, text, **kwargs):
        cr.select_font_face("sans", cairo.FONT_SLANT_OBLIQUE)
        cr.set_font_size(self.FONT_SIZE)
        xbearing, ybearing, width, height, xadvance, yadvace = cr.text_extents(text)
        cr.move_to(x - xbearing - width/2, y - ybearing - height/2)
        cr.set_source_rgb(0, 0, 0)
        cr.show_text(text)
        cr.stroke()
        min_radius = math.sqrt((width/2)**2 + (height/2)**2)
        return min_radius + self.DOUBLE_RADIUS_GAP + self.TEXT_RADIUS_GAP

    def draw_arrow(self, cr, Vs, Ve):
        Vbase = (Vs - Ve).normalize()
        V1 = Ve + Vbase.orthogonal_cw() * self.ARROW_MID_HEIGHT
        V2 = Ve + Vbase.orthogonal_ccw() * self.ARROW_MID_HEIGHT
        cr.set_source_rgb(0, 0, 0)

        cr.move_to(Vs.x, Vs.y)
        cr.line_to(V1.x, V1.y)
        cr.line_to(V2.x, V2.y)
        cr.line_to(Vs.x, Vs.y)
        # cr.stroke()
        cr.fill()

    def get_transition_layout(self, transition):
        # TODO a more complex way of getting different layouts (controllable vs uncontrollable, ...)
        # but it is at least one layout for each pair of states
        return transition.from_state.transition_layouts[transition.to_state]

    def draw_transition(self, cr, transition, states_radius, factor=1.0, ccw=True):
        # radius of each state: 's'tart and 'e'nd states
        rs = states_radius[transition.from_state]
        re = states_radius[transition.to_state]
        layout = self.get_transition_layout(transition)

        # centre of each state
        Vs = Point2D(transition.from_state.x, transition.from_state.y) # start state
        Ve = Point2D(transition.to_state.x, transition.to_state.y)     # end state
        Vm = Ve.mid_point(Vs)  # middle point between states

        dist = Vs.distance(Ve)
        if dist < 1.0:
            """
            Avoid zero length when two states are on top of each other.
            It's also used for self loops.
            It's a unit vector based on the transition render_angle
            """
            a = layout.render_angle + 180  # we need the vetor pointing to the opposite direction we want as the rm_length will invert for small lengths
            while a > 360:
                a = a - 360
            V2 = Point2D.from_angle(a)
            V2.y = -V2.y # cairo works with Y axis pointing down
            V3 = Point2D(-V2.x, -V2.y)
        else:
            V1 = Vm - Vs  # vector from start state centre to middle point
            if ccw is True:
                V2 = V1.orthogonal_ccw() # vector between Vm and Vc
                V3 = V1.orthogonal_cw().normalize() # vector to the text direction
            else:
                V2 = V1.orthogonal_cw()
                V3 = V1.orthogonal_ccw().normalize()

        f = (factor * layout.render_factor)
        # TODO improve the impact of factor (f) in the rm_length
        if f >= 1.0:
            V2 = V2.rm_length((rs+re)/2)
            V2 = V2 * f
        else:
            V2 = V2 * f
            V2 = V2.rm_length((rs+re)/2)
        Vc = Vm + V2                        # Vc: centre of the transition arc

        # draw the middle point (red) and the centre of the transition's arc for debug
        # self._draw_point(cr, Vm, r=1)
        # self._draw_point(cr, Vc, b=1)

        r = Vs.distance(Vc)                 # radius of the transition arc

        Vtext = Vc + V3.set_length(r + self.TRANSITION_TEXT_SPACE)
        self.write_text(cr, Vtext.x, Vtext.y, transition.event.name)

        # start and end angles of the transition's arc. Initially from centre of start state to centre of end state
        Acs = Vs.angle(Vc, r) # angle from (1, 0) to the point Vs using Vc as the origin
        Ace = Ve.angle(Vc, r) # angle from (1, 0) to the point Ve using Vc as the origin
        Ads = 2 * math.asin(rs/(2*r))  # angle to add/subtract from Acs. Considering the radious of the state's circle as the chord of the transition arc ...
        Ade = 2 * math.asin(re/(2*r))  # angle to add/subtract from Ace. ... this gives the [small] piece of arc that needs to be removed, from center of the state to its border.
        Aae = 2 * math.asin(self.ARROW_LENGTH/(2*r)) # angle to add/subtract for the arrow end point

        cr.set_source_rgb(0,0,1)
        if ccw is True:
            cr.arc(Vc.x, Vc.y, r, Acs + Ads, Ace - Ade - Aae)
            Varrow = Vc + Point2D.from_rad_angle(Ace - Ade).set_length(r)
            Varrowend = Vc + Point2D.from_rad_angle(Ace - Ade - Aae).set_length(r)
        else:
            cr.arc(Vc.x, Vc.y, r, Ace + Ade + Aae, Acs - Ads)
            Varrow = Vc + Point2D.from_rad_angle(Ace + Ade).set_length(r)
            Varrowend = Vc + Point2D.from_rad_angle(Ace + Ade + Aae).set_length(r)
        cr.stroke()

        self.draw_arrow(cr, Varrow, Varrowend)

        # TODO: how to deal with multiple transitions from state pair of states?
        #       we must draw the transition once and concatenate the text
        #       and we want different colours for different type (e.g. controllable, observable)
        #       ... some sort of configurable colour theme to apply
        #       We also want to set whether draw different transitions for different
        #       ... types of events (e.g. with a cross stroke for controlabble events
        #       ... or group them all together.
        #       Shall remove transition config render_angle and render_factor as we may want to join them all
        #       ... in a single arrow and concatenate the text

        event = transition.event
        if event.controllable:
            cr.set_source_rgb(0, 0, 0)
        else:
            cr.set_source_rgb(1, 0, 0)

    def draw(self, cr, automaton):
        # draw states
        state_radius = dict()
        for state in automaton.states:
            # min_radius = self.write_text(cr, state.x, state.y, state.name)
            radius = self.write_text(cr, state.x, state.y, state.name)
            state_radius[state] = radius
            cr.set_source_rgb(0, 0, 0)
            cr.arc(state.x, state.y, radius, 0, 2 * math.pi)
            cr.stroke()
            if state.marked:
                cr.arc(state.x, state.y, radius - self.DOUBLE_RADIUS_GAP, 0, 2 * math.pi)
                cr.stroke()

        # draw transitions
        for state in automaton.states:
            for transition in state.out_transitions:
                self.draw_transition(cr, transition, state_radius, ccw=True, factor=1.5)



