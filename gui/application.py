import sys
import gi
from gi.repository import GLib, Gio, Gtk


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This will be in the windows group and have the "win" prefix
        max_action = Gio.SimpleAction.new_stateful("maximize", None, GLib.Variant.new_boolean(False))
        max_action.connect("change-state", self.on_maximize_toggle)
        self.add_action(max_action)

        # Keep it in sync with the actual state
        self.connect("notify::is-maximized",
            lambda obj, pspec: max_action.set_state(
                GLib.Variant.new_boolean(obj.props.is_maximized)
            ),
        )

    def on_maximize_toggle(self, action, value):
        action.set_state(value)
        if value.get_boolean():
            self.maximize()
        else:
            self.unmaximize()


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.nadzoru2.application",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None,)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application, when the last one is closed the application shuts down
            self.window = MainWindow(application=self, title="Nadzoru 2")
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()  # convert GVariantDict -> GVariant -> dict

        if "test" in options:
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0

    def on_quit(self, action, param):
        self.quit()

        
