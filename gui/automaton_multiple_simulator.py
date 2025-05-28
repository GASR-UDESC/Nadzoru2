from gi.repository import Gtk
from gui.base import PageMixin
from gi.repository import GLib
from renderer.automaton_renderer import AutomatonRenderer
from gui.property_box import PropertyBox

#class for creating the simulation window
class AutomatonSimulatorWindow(Gtk.Window):
    def __init__(self, automaton_player, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.automaton_player = automaton_player

        self.set_title(f"simulation - {self.automaton_player.automaton.get_id_name()}")
        self.set_default_size(600, 400)

        #create the automaton simulator - graphical display
        self.automaton_renderer = AutomatonRenderer(self.automaton_player.automaton) 
        self.automaton_renderer.connect("draw", self.on_draw)
        self.add(self.automaton_renderer)

        self.show_all()

    # def update(self):
    #    pass
        
    def on_draw(self, wid, cr):
        self.automaton_renderer.draw(cr, highlight_state=self.automaton_player.current_state)
    
    def queue_draw(self): #update
        self.automaton_renderer.queue_draw()


class AutomatonPlayer:
    def __init__(self, automaton):
        self.automaton = automaton
        self.current_state = self.automaton.initial_state
        self.simulation_window = None

    def reset(self):
        self.current_state = self.automaton.initial_state
        if self.simulation_window is not None:
            self.simulation_window.queue_draw()

    def show_window(self):
        if self.simulation_window is None:
            self.simulation_window = AutomatonSimulatorWindow(self)
            self.simulation_window.connect("destroy", self.on_window_destroyed)
    
    def hide_window(self):
        if self.simulation_window is not None:
            self.simulation_window.destroy()
            self.simulation_window = None

    def on_window_destroyed(self, _):
        self.simulation_window = None

    def apply_event(self, event_name):
        for transition in self.current_state.out_transitions:
            if transition.event.name == event_name:
                self.current_state = transition.to_state
                # print(f"[{self.automaton.get_id_name()}] avançou para: {self.current_state.name}") #log
                if self.simulation_window:
                    self.simulation_window.queue_draw()
                return True
        return False

# main class that handles the automaton simulation process
class AutomatonSimulatorController(PageMixin, Gtk.Box):
    def __init__(self, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.selected_automata = list()
        self.players = {}
        self.simulation_active = False
        self.automatonlist = list()

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.connect('parent-set', self.on_parent_set)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10) 
        self.pack_start(self.vbox, True, True, 0)
        self.pack_start(self.transitions_panel(), True, True, 0)

        self.property_box = PropertyBox()
        self.property_box.connect('nadzoru-property-change', self.prop_edited)
        self.vbox.pack_start(self.property_box, True, True, 0)

        self.vbox.pack_start(self.simulation_panel(), False, False, 0)

    def on_parent_set(self, widget, oldparent):
        if oldparent is None:                       
            app = widget.get_application()          
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()
        self.update_property_box()

    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        self.update_property_box()

    def update_property_box(self):
        open_automata = list()
        self.property_box.clear()

        for automato in self.automatonlist:
            open_automata.append((automato.get_name(), automato))

        #self.property_box.add_dualListSelector("Automaton", open_automata, 'automaton')
        self.property_box.add_dualListSelector("Automaton", open_automata, data='automaton')

    def prop_edited(self, widget, value, property_name, widget_name=None):
        if property_name == 'automaton':
            self.selected_automata = value
            # print(f"automatos selecionados atualizados: {[a.get_id_name() for a in value]}") #log
            self.update_selected_list_view()

            if not self.simulation_active:
                self.events_tree_store.clear()

    def update_selected_list_view(self):
        self.selected_list_store.clear()
        for automato in self.selected_automata:
            self.selected_list_store.append([automato.get_id_name(), automato])
            
    def simulation_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # treeview with selected automaton
        self.selected_list_store = Gtk.ListStore(str, object)
        self.selected_tree_view = Gtk.TreeView(model=self.selected_list_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Selected Automata", renderer, text=0)
        self.selected_tree_view.append_column(column)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(120)
        scrolled_window.add(self.selected_tree_view)
        panel.pack_start(scrolled_window, True, True, 0)

        # buttons
        self.run_button = Gtk.Button(label="Run")
        self.run_button.connect("clicked", self.on_run_clicked)
        panel.pack_start(self.run_button, False, False, 0)

        self.reset_button = Gtk.Button(label="Reset")
        self.reset_button.connect("clicked", self.on_reset_clicked)
        panel.pack_start(self.reset_button, False, False, 0)

        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_clicked)
        panel.pack_start(self.stop_button, False, False, 0)

        self.show_button = Gtk.Button(label="Show")
        self.show_button.connect("clicked", self.on_show_clicked)
        panel.pack_start(self.show_button, False, False, 0)

        self.hide_button = Gtk.Button(label="Hide")
        self.hide_button.connect("clicked", self.on_hide_clicked)
        panel.pack_start(self.hide_button, False, False, 0)

        self.run_button.set_sensitive(True)
        self.reset_button.set_sensitive(False)
        self.stop_button.set_sensitive(False)
        self.show_button.set_sensitive(False)
        self.hide_button.set_sensitive(False)

        return panel
    
    def transitions_panel(self):        
        self.events_tree_store = Gtk.ListStore(str)
        self.events_tree_view = Gtk.TreeView(model=self.events_tree_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Transitions", renderer, text=0)
        self.events_tree_view.append_column(column)

        self.events_tree_view.connect("row-activated", self.on_transition_selected)

        transitions_scrolled_window = Gtk.ScrolledWindow()
        transitions_scrolled_window.set_min_content_height(200)
        transitions_scrolled_window.add(self.events_tree_view)
        #panel.pack_start(transitions_scrolled_window, True, True, 0)
        
        return transitions_scrolled_window
    
    def update_transitions_list(self):
        self.events_tree_store.clear()
        events_added = set()
        blocked_events = set()

        automaton_to_transitions = {}
        for automaton, player in self.players.items():
            current_state = player.current_state
            automaton_to_transitions[automaton] = {
                transition.event.name: transition for transition in current_state.out_transitions
            }

        for automaton, player in self.players.items():
            current_state = player.current_state

            for transition in current_state.out_transitions:
                event_name = transition.event.name
                allowed = True

                for other_automaton, other_player in self.players.items():
                    if event_name not in other_automaton.event_get_name_list():
                        continue
                    other_transitions = automaton_to_transitions.get(other_automaton, {})
                    if event_name not in other_transitions:
                        allowed = False
                        blocked_events.add(event_name)
                        break

                if allowed and event_name not in events_added:
                    self.events_tree_store.append([event_name])
                    events_added.add(event_name)


    def on_run_clicked(self, button):

        self.run_button.set_sensitive(False)
        self.reset_button.set_sensitive(True)
        self.stop_button.set_sensitive(True)
        self.show_button.set_sensitive(True)
        self.hide_button.set_sensitive(True)

        if self.simulation_active:
            return

        if not self.selected_automata:
            # print("nenhum autômato selecionado") #log
            return

        self.simulation_active = True
        self.property_box.set_sensitive(False)

        for automato in self.selected_automata:
            if automato not in self.players:
                player = AutomatonPlayer(automato)
                self.players[automato] = player

        self.update_transitions_list()
        # print("simulação iniciada com:", [a.get_id_name() for a in self.selected_automata]) #log
    
    def on_stop_clicked(self, button):
        self.run_button.set_sensitive(True)
        self.reset_button.set_sensitive(False)
        self.stop_button.set_sensitive(False)
        self.show_button.set_sensitive(False)
        self.hide_button.set_sensitive(False)
        if not self.simulation_active:
            return

        self.simulation_active = False
        self.property_box.set_sensitive(True)

        for player in self.players.values():
            if player.simulation_window is not None:
                player.simulation_window.destroy()
                player.simulation_window = None

        self.events_tree_store.clear()

        self.players.clear()

        # print("simulação parada e PropertyBox desbloqueada") #log

    def on_show_clicked(self, button):
        selection = self.selected_tree_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return

        automato = model[treeiter][1]
        if automato in self.players:
            self.players[automato].show_window()
            #print(f"janela de {automato.get_id_name()} aberta") #log

    def on_hide_clicked(self, button):
        selection = self.selected_tree_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return

        automato = model[treeiter][1]
        if automato in self.players:
            self.players[automato].hide_window()
            # print(f"janela de {automato.get_id_name()} fechada") #log
    
    def on_reset_clicked(self, button):
        if not self.simulation_active:
            # print("simulacao não está ativa") #log
            return

        for player in self.players.values():
            player.reset()

        self.update_transitions_list()
        # print("todos os automatos foram resetados para o estado inicial") #log

    def on_transition_selected(self, treeview, path, column):
        model = treeview.get_model()
        iter_ = model.get_iter(path)
        event_name = model.get_value(iter_, 0)

        # print(f"evento clicado: {event_name}") #log

        for player in self.players.values():
            success = player.apply_event(event_name)
            if not success:
                # print(f"[{player.automaton.get_id_name()}] evento '{event_name}' não aplicável no estado atual") #log
                pass
        self.update_transitions_list()
