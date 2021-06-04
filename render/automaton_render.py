import cairo
import math

# from machine.automaton import Automaton


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Point2D(self.x, self.y)

    @classmethod
    def from_angle(cls, deg_angle):
        angle = math.pi * deg_angle / 180.0
        return cls(math.cos(angle), math.sin(angle))

    @classmethod
    def from_rad_angle(cls, angle):
        return cls(math.cos(angle), math.sin(angle))

    def __str__(self):
        return "({:.1f},{:.1f})".format(self.x, self.y)

    # Operators: V = W + X creates a new object V, V += 2 updates V

    # -- ADD -- #
    def add(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __add__(self, other):
        return self.copy().add(other)

    # def __radd__(self, value):  # when this object is on the right side
    #    return self.copy().add_length(value)

    def __iadd__(self, other):
        return self.add(other)

    # -- SUB -- #
    def sub(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __sub__(self, other):
        return self.copy().sub(other)

    # def __rsub__(self, value):
    #    return self.copy().rm_length(value)

    def __isub__(self, other):
        return self.sub(other)

    # -- MUL -- #
    def mul(self, value):
        self.x *= value
        self.y *= value
        return self

    def __mul__(self, value):
        return self.copy().mul(value)

    def __rmul__(self, value):
        return self.copy().mul(value)

    def __imul__(self, value):
        return self.mul(value)

    # -- TRUE DIV (i.e. float) -- #
    def truediv(self, value):
        self.x /= value
        self.y /= value
        return self

    def __truediv__(self, value):
        return self.copy().truediv(value)

    def __rtruediv__(self, value):
        return self.copy().truediv(value)

    def __itruediv__(self, value):
        return self.truediv(value)

    # ---- #

    def mid_point(self, other):
        """
            This is one of the few methods that actually generates a new
            Point2D object.
        """
        # return (self - other)/2 + other
        new_point = self - other
        new_point /= 2
        new_point += other
        return new_point

    def orthogonal_cw(self):
        self.x, self.y = self.y, -self.x
        return self

    def orthogonal_ccw(self, new=True):
        self.x, self.y = -self.y, self.x
        return self

    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def length(self):  # vector norm or magnitude
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        self /= self.length()
        return self

    def set_length(self, value):
        length = self.length()
        self *= value
        self /= length
        return self

    def rm_length(self, value):
        """
            if value is too large it will also swap direction.
            Take care in case length and value are close.
        """
        return self.set_length(self.length() - value)

    def add_length(self, value):
        return self.set_length(self.length() + value)

    def angle(self, origin, r=None):
        """Get the angle self is based on the origin 'origin'.
        Cairo angles increase cw (as positive y is downwards.
        a = arccos((x0*x1 + y0*y1) / (sqrt(x0**2 + y0**2) *
            sqrt(x1**2 + y1**2)))
        Note that we want the angle to the vector (x1, y1) =  (1,0), so
        a = acos(x0 / (sqrt(x0**2 + y0**2) * sqrt(1**2 + 0)
        a = acos(x0 / sqrt(x0**2 + y0**2) = acos(x0 / r) where r
        is the distance
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
    FONT_SIZE = 26
    TRANSITION_TEXT_SPACE = 12
    ARROW_LENGTH = 20
    ARROW_MID_HEIGHT = 5
    CENTER = (0., 0.)
    UP = (0., 1.)
    DOWN = (0., -1.)
    RIGHT = (1., 0.)
    LEFT = (-1., 0.)
    COLORS = {
        'k': (0, 0, 0, 0.25),
        'r': (0.7, 0, 0, 0.25),
        'g': (0, 0.7, 0, 0.25),
        'b': (0, 0, 0.7, 0.25),
        'y': (0.7, 0.7, 0, 0.25),
        'm': (0.7, 0, 0.7, 0.25),
        'c': (0, 0.7, 0.7, 0.25),
        'w': (0.6, 0.6, 0.6, 0.25),

        'K': (0, 0, 0, 1),
        'R': (1, 0, 0, 1),
        'G': (0, 1, 0, 1),
        'B': (0, 0, 1, 1),
        'Y': (1, 1, 0, 1),
        'M': (1, 0, 1, 1),
        'C': (0, 1, 1, 1),
        'W': (1, 1, 1, 1),

    }

    def __init__(self):
        pass

    def _draw_point(self, cr, V, r=0, g=0, b=0):
        cr.set_source_rgb(r, g, b)
        cr.arc(V.x, V.y, 2, 0, 2 * math.pi)
        cr.stroke()

    def get_event_display_cfg(self, event):
        cfg = {}
        if event.controllable and event.observable:
            cfg['color'] = 'B'
        elif event.controllable and (not event.observable):
            cfg['color'] = 'b'
        elif (not event.controllable) and event.observable:
            cfg['color'] = 'R'
        elif (not event.controllable) and (not event.observable):
            cfg['color'] = 'r'

        return cfg

    def write_text(
        self, cr, x, y, *texts, align=CENTER, font_size=FONT_SIZE,
        font_slant=cairo.FONT_SLANT_OBLIQUE,
        font_weight=cairo.FONT_WEIGHT_NORMAL,
        colors=None, **kwargs
    ):
        cr.select_font_face("sans", font_slant, font_weight)
        cr.set_font_size(font_size)
        alltext = ''.join(texts)
        xbearing, ybearing, width, height, xadvance, yadvace = cr.text_extents(alltext)
        cr.move_to(x - xbearing - width/2, y - ybearing - height/2)
        for i, text in enumerate(texts):
            if isinstance(colors, str):
                cr.set_source_rgba(*self.COLORS[colors])
            elif isinstance(colors, list) or isinstance(colors, tuple):
                cr.set_source_rgba(*self.COLORS[colors[i]])
            cr.show_text(text)
        cr.stroke()

        # data used to set the state's circle's radius
        min_radius = math.sqrt((width/2)**2 + (height/2)**2)
        return min_radius + self.DOUBLE_RADIUS_GAP + self.TEXT_RADIUS_GAP

    def draw_arrow(self, cr, Vs, Ve):
        Vbase = (Vs - Ve).normalize()
        V1 = Vbase.copy().orthogonal_cw().mul(self.ARROW_MID_HEIGHT).add(Ve)
        V2 = Vbase.copy().orthogonal_ccw().mul(self.ARROW_MID_HEIGHT).add(Ve)
        cr.set_source_rgb(0, 0, 0)

        cr.move_to(Vs.x, Vs.y)
        cr.line_to(V1.x, V1.y)
        cr.line_to(V2.x, V2.y)
        cr.line_to(Vs.x, Vs.y)
        # cr.stroke()
        cr.fill()

    def draw_state_transitions(self, cr, from_state, states_radius, factor=1.0,
                               ccw=True):
        transitions = dict()
        for trans in from_state.out_transitions:
            if trans.to_state not in transitions:
                transitions[trans.to_state] = list()
            transitions[trans.to_state].append(trans)

        for to_state, layout in from_state.transition_layouts.items():
            if to_state not in states_radius:
                continue  # probably this state is not in draw_partial
            # radius of each state: 's'tart and 'e'nd states
            rs = states_radius[from_state]
            re = states_radius[to_state]

            # centre of each state
            Vs = Point2D(from_state.x, from_state.y)  # start state
            Ve = Point2D(to_state.x, to_state.y)  # end state
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
                V2.y = -V2.y  # cairo works with Y axis pointing down
                V3 = Point2D(-V2.x, -V2.y)
            else:
                V1 = Vm - Vs  # vector from start state centre to middle point
                if ccw is True:
                    V2 = V1.copy().orthogonal_ccw()  # vector between Vm and Vc
                    V3 = V1.copy().orthogonal_cw().normalize()  # vector to the text direction
                else:
                    V2 = V1.copy().orthogonal_cw()
                    V3 = V1.copy().orthogonal_ccw().normalize()

            # TODO improve the impact of factor (f) in the rm_length
            f = (factor * layout.render_factor)
            if f >= 1.0:
                V2.rm_length((rs+re)/2).mul(f)
            else:
                V2.mul(f).rm_length((rs+re)/2)
            Vc = Vm + V2  # Vc: centre of the transition arc
            r = Vs.distance(Vc)                 # radius of the transition arc
            Vtext = V3.copy().set_length(r + self.TRANSITION_TEXT_SPACE).add(Vc)

            # Write the events names
            texts  = list()
            colors = list()
            for i, transition in enumerate(transitions[to_state]):
                if i > 0:
                    texts.append(", ")
                    colors.append('K')
                event = transition.event
                texts.append(event.name)
                event_cfg = self.get_event_display_cfg(event)
                colors.append(event_cfg['color'])
            self.write_text(cr, Vtext.x, Vtext.y, *texts, colors=colors,
                            font_weight=cairo.FONT_WEIGHT_BOLD)

            # start and end angles of the transition's arc. Initially from centre of start state to centre of end state
            Acs = Vs.angle(Vc, r)  # angle from (1, 0) to the point Vs using Vc as the origin
            Ace = Ve.angle(Vc, r)  # angle from (1, 0) to the point Ve using Vc as the origin
            Ads = 2 * math.asin(rs/(2*r))  # angle to add/subtract from Acs. Considering the radious of the state's circle as the chord of the transition arc ...
            Ade = 2 * math.asin(re/(2*r))  # angle to add/subtract from Ace. ... this gives the [small] piece of arc that needs to be removed, from center of the state to its border.
            Aae = 2 * math.asin(self.ARROW_LENGTH/(2*r))  # angle to add/subtract for the arrow end point

            # Draw arc and arrow
            cr.set_source_rgb(0, 0, 0)
            if ccw is True:
                cr.arc(Vc.x, Vc.y, r, Acs + Ads, Ace - Ade - Aae)
                Varrow = Point2D.from_rad_angle(Ace - Ade).set_length(r).add(Vc)
                Varrowend = Point2D.from_rad_angle(Ace - Ade - Aae).set_length(r).add(Vc)
            else:
                cr.arc(Vc.x, Vc.y, r, Ace + Ade + Aae, Acs - Ads)
                Varrow = Point2D.from_rad_angle(Ace + Ade).set_length(r).add(Vc)
                Varrowend = Point2D.from_rad_angle(Ace + Ade + Aae).set_length(r).add(Vc)
            cr.stroke()
            self.draw_arrow(cr, Varrow, Varrowend)

    def draw_state(self, cr, state, txt_color=(0, 0, 0), arc_color=(0, 0, 0)):
            cr.set_source_rgb(*txt_color)
            radius = self.write_text(cr, state.x, state.y, state.name)
            cr.set_source_rgb(*arc_color)
            cr.arc(state.x, state.y, radius, 0, 2 * math.pi)
            cr.stroke()
            if state.marked:
                cr.arc(state.x, state.y, radius - self.DOUBLE_RADIUS_GAP, 0, 2 * math.pi)
                cr.stroke()
            return radius

    def draw(self, cr, automaton):
        # draw states
        state_radius = dict()

        for state in automaton.states:
            state_radius[state] = self.draw_state(cr, state, arc_color=(0, 0, 0))

        for state in automaton.states:
            self.draw_state_transitions(cr, state, state_radius, ccw=True, factor=2.0)

    def get_connected_states(self, state, forward_deep, backward_deep):
        states = [state]

        # forward
        state_lvl_map = {state: 0}
        stack = [state]
        while stack:
            src = stack.pop()
            lvl = state_lvl_map[src]
            if lvl < forward_deep:
                for trans in src.out_transitions:
                    trg = trans.to_state
                    if trg not in state_lvl_map:
                        state_lvl_map[trg] = lvl + 1
                        states.append(trg)
                        stack.append(trg)

        # backward
        state_lvl_map = {state: 0}
        stack = [state]
        while stack:
            trg = stack.pop()
            lvl = state_lvl_map[trg]
            if lvl < backward_deep:
                for trans in trg.in_transitions:
                    src = trans.from_state
                    if src not in state_lvl_map:
                        state_lvl_map[src] = lvl + 1
                        states.append(src)
                        stack.append(src)

        return states
        

    def draw_partial(self, cr, automaton, current_state, forward_deep=1, backward_deep=0):
        state_radius = dict()
        show_states = self.get_connected_states(current_state, forward_deep=forward_deep, backward_deep=backward_deep)
        
        for state in show_states:
            c = (0, 0, 0)
            if state == current_state:
                radius = self.draw_state(cr, state, arc_color=(1, 0, 0))
            else:
                radius = self.draw_state(cr, state, arc_color=(0, 0, 0))
            state_radius[state] = radius

        for state in show_states:
            self.draw_state_transitions(cr, state, state_radius, ccw=True, factor=2.0)



