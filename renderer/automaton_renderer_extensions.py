from renderer.automaton_renderer import AutomatonRenderer

class AutomatonRendererPublic(AutomatonRenderer):
    
    def get_transition_texts_and_colors(self, event, transition):
        event_texts, event_colors = super().get_transition_texts_and_colors(event, transition)
        if event.public:
            event_texts.append(' (pub)')
            event_colors.append('K')
        return event_texts, event_colors


class AutomatonRendererProbabilistic(AutomatonRenderer):
    
    def get_transition_texts_and_colors(self, event, transition):
        event_texts, event_colors = super().get_transition_texts_and_colors(event, transition)
        event_texts.append(f' (p={transition.probability})')
        event_colors.append('K')
        return event_texts, event_colors
