import sys
import gi
from gi.repository import Gdk, Gio, Gtk

from machine.automaton import Automaton
from render import AutomatonRender

MENU_XML = """"""

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.note = Gtk.Notebook()
        self.tab = list()
        self.statusbar = Gtk.Statusbar()

        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.note, True, True, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        # self.note.popup_enable()
        self.note.popup_disable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

        # Create page example
        # self.page1 = Gtk.Box()
        # self.page1.set_border_width(10)
        # self.page1.add(Gtk.Label(label="Default Page!"))
        # self.note.append_page(self.page1, Gtk.Label(label="Automata"))

        self.show_all()

    def get_image(self, name):
        try:
            f = open(name, 'r')
            return Gtk.Image.new_from_file(name)
        except:
            return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)

    def add_tab(self, widget, title):
        note = self.note.insert_page(widget, Gtk.Label.new(title), -1)
        self.tab.append(note)
        self.show_all()
        self.note.set_current_page(note)

        return note

    def remove_tab(self, id):
        if id:
            self.note.remove_page(id)
            destroy = self.tab.remove(id)
            if destroy and destroy.destroy_callback:
                destroy.destroy_callback(destroy.param)

        self.show_all()

    def remove_current_tab(self, *args):
        id = self.note.get_current_page()
        self.remove_tab(id)

    def set_tab_page_title(self, widget, title):
        page_label = self.note.get_tab_label(widget)
        page_label.set_text(title)

        self.show_all()


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.nadzoru2.application",
            **kwargs
        )
        self.window = None
        self.elements = list()
        # self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None,)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        def create_action(action_name, callback):
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", callback)
            self.add_action(action)

        create_action("new", self.on_new_automata)
        create_action("load", self.on_load_automata)
        create_action("save", self.on_save_automata)
        create_action("edit", self.on_edit_automata)
        create_action("close", self.on_close_tab)
        create_action("quit", self.on_quit)

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

    # TODO: open editor with 'a' and add in a new page (tab)
    def on_new_automata(self, action, param):
        if(len(self.window.tab) > 5):
            print("[*] You exceed the opended pages limit")
        else: 
            print("[*] You created a new automata")
            a = Automaton()

            # Test Renderer
            from test_automata import automata_01
            automata_01(a)

            self.automaton = a
            self.lst_state = list(a.states)
            self.ar = AutomatonRender()

            # Creating Drawing Area
            self.darea = Gtk.DrawingArea()
            self.darea.connect("draw", self.on_draw)
            self.darea.set_events(Gdk.EventMask.BUTTON_MOTION_MASK |
                                Gdk.EventMask.BUTTON_PRESS_MASK
            )
            self.darea.connect("motion-notify-event", self.on_motion_notify)
            self.darea.connect("button-press-event", self.on_button_press)

            self.page = self.window.add_tab(self.darea, "automata")
            # print("[*] Current Notebook Page ID: ", self.page)

    def on_draw(self, wid, cr):
        self.ar.draw(cr, self.automaton)

    def on_motion_notify(self, w, e):
        if e.type == Gdk.EventType.MOTION_NOTIFY and (e.state & Gdk.ModifierType.BUTTON1_MASK):
            s = self.lst_state[0]
        elif e.type == Gdk.EventType.MOTION_NOTIFY and (e.state & Gdk.ModifierType.BUTTON3_MASK):
            s = self.lst_state[1]
        else:
            return
        s.x = e.x
        s.y = e.y
        self.darea.queue_draw()

    def on_button_press(self, w, e):
        if e.type == Gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.LEFT_BUTTON:
            s = self.lst_state[0]
        elif e.type == Gdk.EventType.BUTTON_PRESS and e.button == MouseButtons.RIGHT_BUTTON:
            s = self.lst_state[1]
        else:
            return
        s.x = e.x
        s.y = e.y
        self.darea.queue_draw()


    def on_load_automata(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self.window, Gtk.FileChooserAction.OPEN,
                                       ("_Cancel", Gtk.ResponseType.CANCEL,
                                        "_Open", Gtk.ResponseType.ACCEPT)
                                       )
        result = dialog.run()
        if result == Gtk.ResponseType.ACCEPT:
            a = Automaton()
            self.elements.append(a)
            print("You loaded an automata:", dialog.get_filename())
            # TODO: load and create editor tab with a
            # a.load(dialog.get_filename())
        else:
            print("You CANCELED")
        dialog.destroy()

    def on_edit_automata(self, action, param):
        print("You opened in editor automata")

    def on_save_automata(self, action, param):
        print("You saved the automata")

    def on_close_tab(self, action, param):
        print("[*] You closed the current tab")
        self.window.remove_tab(self.window.note.get_current_page())

    def on_quit(self, action, param):
        dialog = Gtk.Dialog("Nazoru2", self.window)
        dialog.modify_style
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_YES,
            Gtk.ResponseType.YES
        )
        dialog.set_default_size(150, 100)
        
        label = Gtk.Label()
        label.set_text("Do you really want to exit?")
        label.set_justify(Gtk.Justification.LEFT)

        box_dialog = dialog.get_content_area()
        box_dialog.add(label)
        box_dialog.show_all()

        result = dialog.run()

        if result == Gtk.ResponseType.YES:
            self.quit()
        else:
            print("You CANCELED")
        dialog.destroy()
        
