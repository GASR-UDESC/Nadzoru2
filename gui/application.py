import sys
import gi
from gi.repository import Gdk, Gio, Gtk

from machine.automaton import Automaton
from gui.automaton_editor import AutomatonEditor
from gui.automaton_simulator import AutomatonSimulator
from gui.main_window import MainWindow

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.nadzoru2.application", **kwargs)
        self.window = None
        self.elements = list()

    def create_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.create_action("new-automaton", self.on_new_automaton)
        self.create_action("load-automaton", self.on_load_automaton)
        self.create_action("save-automaton", self.on_save_automaton)
        self.create_action("edit-automaton", self.on_edit_automaton)
        self.create_action("simulate-automaton", self.on_simulate_automaton)
        self.create_action("close-tab", self.on_close_tab)
        self.create_action("quit", self.on_quit)

        builder = Gtk.Builder()
        builder.add_from_file("gui/ui/menubar.ui")
        self.menubar = builder.get_object("menubar")
        self.set_menubar(self.menubar)

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self, title="Nadzoru 2")
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        self.activate()
        return

    def validade_quit(self):
        # TODO: For each file not save ask: cancel, discard, save. If no file just quit!
        dialog = Gtk.Dialog("Nazoru2", self.window)
        dialog.modify_style
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_DISCARD, Gtk.ResponseType.YES, Gtk.STOCK_SAVE, Gtk.ResponseType.APPLY)
        dialog.set_default_size(150, 100)

        label = Gtk.Label()
        #label.set_text("File {} not saved!")
        label.set_text("Do you really want to exit?")
        label.set_justify(Gtk.Justification.LEFT)

        box_dialog = dialog.get_content_area()
        box_dialog.add(label)
        box_dialog.show_all()

        result = dialog.run()
        dialog.destroy()

        if result == Gtk.ResponseType.YES or result == Gtk.ResponseType.APPLY:
            self.quit()

    # TODO: open editor with 'a' and add in a new page (tab)
    def on_new_automaton(self, action, param):
        from test_automata import automata_01  # For testing
        automaton = Automaton()
        automata_01(automaton)  # For testing
        self.elements.append(automaton)
        editor = AutomatonEditor(automaton)
        self.window.add_tab(editor, "[new] *")


        #~ self.automaton = a
        #~ self.lst_state = list(a.states)
        #~ self.ar = AutomatonRender()

        # Creating Drawing Area
        #~ self.darea = Gtk.DrawingArea()
        #~ self.darea.connect("draw", self.on_draw)
        #~ self.darea.set_events(Gdk.EventMask.BUTTON_MOTION_MASK |
                            #~ Gdk.EventMask.BUTTON_PRESS_MASK
        #~ )
        #~ self.darea.connect("motion-notify-event", self.on_motion_notify)
        #~ self.darea.connect("button-press-event", self.on_button_press)

        #~ self.page = self.window.add_tab(self.darea, "automata")
        # print("[*] Current Notebook Page ID: ", self.page)

    #~ def on_draw(self, wid, cr):
        #~ self.ar.draw(cr, self.automaton)

    #~ def on_motion_notify(self, w, e):
        #~ if e.type == Gdk.EventType.MOTION_NOTIFY and (e.state & Gdk.ModifierType.BUTTON1_MASK):
            #~ s = self.lst_state[0]
        #~ elif e.type == Gdk.EventType.MOTION_NOTIFY and (e.state & Gdk.ModifierType.BUTTON3_MASK):
            #~ s = self.lst_state[1]
        #~ else:
            #~ return
        #~ s.x = e.x
        #~ s.y = e.y
        #~ self.darea.queue_draw()

    #~ def on_button_press(self, w, e):
        #~ if e.type == Gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.LEFT_BUTTON:
            #~ s = self.lst_state[0]
        #~ elif e.type == Gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.RIGHT_BUTTON:
            #~ s = self.lst_state[1]
        #~ else:
            #~ return
        #~ s.x = e.x
        #~ s.y = e.y
        #~ self.darea.queue_draw()

    def on_simulate_automaton(self, action, param):
        from test_automata import automata_01  # For testing
        automaton = Automaton()
        automata_01(automaton)  # For testing
        self.elements.append(automaton)
        simulator = AutomatonSimulator(automaton)
        self.window.add_tab(simulator, "Simulator")

    def on_load_automaton(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self.window, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT))
        result = dialog.run()
        if result == Gtk.ResponseType.ACCEPT:
            a = Automaton()
            a.load(dialog.get_filename())
            self.elements.append(a)
        dialog.destroy()

    def on_edit_automaton(self, action, param):
        print("You opened in editor automata")

    def on_save_automaton(self, action, param):
        print("You saved the automata")

    def on_close_tab(self, action, param):
        print("[*] You closed the current tab")
        self.window.remove_tab(self.window.note.get_current_page())

    def on_quit(self, action, param):
        self.validade_quit()



