import cairo
import math

from machine.automata import Automaton


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        return self / self.lenght()

    def set_length(self, value):
        return (self * value) / self.length()

    def rm_length(self, value):
        """if value is too large it will also swap direction. Take care in case length and value are close."""
        return self.set_length(self.length() - value)

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

    def draw_transition_self(self, cr, transition, states_radius, factor=1.0, ccw=True):
        pass


    def draw_transition_arc(self, cr, transition, states_radius, factor=1.0, ccw=True):
        # radius of each state: 's'tart and 'e'nd states
        rs = states_radius[transition.from_state]
        re = states_radius[transition.to_state]
        # centre of each state
        Vs = Point2D(transition.from_state.x, transition.from_state.y) # start state
        Ve = Point2D(transition.to_state.x, transition.to_state.y)     # end state
        dist = Vs.distance(Ve)

        near = False
        if dist <= 4:
            return # TODO call the selfloop version
        elif dist < (rs + re):
            near = True

        Vm = Ve.mid_point(Vs)               # middle point between states
        V1 = Vm - Vs                        # vector
        # if (near is False and ccw is True) or (near is True and ccw is False):
        #    """When 'near' is set the start/end angle values swap which one is greater, so we can just swap the side
        #    of the arc's centre without changing the order of start/end angles arguments entered into cr.arc call."""
            # V2 = V1.orthogonal_ccw() * factor # - V1.orthogonal_ccw() # vector between Vm and Vc
        if ccw is True:
            V2 = V1.orthogonal_ccw() * factor
        else:
            V2 = V1.orthogonal_cw() * factor  # - V1.orthogonal_cw() # vector between Vm and Vc
        V2 = V2.rm_length((rs+re)/2)
        Vc = Vm + V2                        # Vc: centre of the transition arc
        r = Vs.distance(Vc)                 # radius of the transition arc

        self._draw_point(cr, Vm, r=1)
        self._draw_point(cr, Vc, b=1)

        Acs = Vs.angle(Vc, r) # angle from (1, 0) to the point Vs using Vc as the origin
        Ace = Ve.angle(Vc, r) # angle from (1, 0) to the point Ve using Vc as the origin
        Ads = 2 * math.asin(rs/(2*r))  # angle to add/subtract from Acs. Considering the radious of the state's circle as the chord of the transition arc ...
        Ade = 2 * math.asin(re/(2*r))  # angle to add/subtract from Ace. ... this gives the [small] piece of arc that needs to be removed, from center of the state to its border.
        # print(180*Acs/math.pi, 180*Ace/math.pi, "-/+", 180*Ads/math.pi, 180*Ade/math.pi, "=", 180*(Acs+Ads)/math.pi, 180*(Ace - Ade)/math.pi)

        cr.set_source_rgb(0,0,1)
        if ccw is True:
            cr.arc(Vc.x, Vc.y, r, Acs + Ads, Ace - Ade)
        else:
            cr.arc(Vc.x, Vc.y, r, Ace + Ade, Acs - Ads)
        cr.stroke()

        if r < 1:
            """Too close to draw"""
            return

        event = transition.event
        if event.controllable:
            cr.set_source_rgb(0, 0, 0)
        else:
            cr.set_source_rgb(1, 0, 0)

    def draw_transition(self, cr, transition, *args, **kwargs):
        if transition.from_state is transition.to_state:
            self.draw_transition_self(cr, transition, *args, **kwargs)
        else:
            self.draw_transition_arc(cr, transition, *args, **kwargs)

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
                self.draw_transition(cr, transition, state_radius, ccw=True)
                break



