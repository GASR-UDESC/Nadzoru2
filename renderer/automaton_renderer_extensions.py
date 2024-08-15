from renderer.automaton_renderer import AutomatonRenderer

class AutomatonRendererPublic(AutomatonRenderer):
    
    def get_transition_texts_and_colors(self, event):
        event_texts, event_colors = super().get_transition_texts_and_colors(event)
        if event.public:
            event_texts.append(' (pub)')
            event_colors.append('K')
        return event_texts, event_colors
