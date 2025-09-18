from gi.repository import Gtk
from gui.base import PageMixin
from codegen.code_gen import ArduinoGenerator, KilobotGenerator, CGenerator, CPPGenerator, PythonGenerator
from gui.property_box import PropertyBox
from gui.dual_list_selector import DualListSelector

from codegen.code_gen_extensions import *
from gui.parse_argument import Extension

class AutomatonGenerator(PageMixin, Gtk.Box):
    devices = {}

    def __init__(self, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.connect('parent-set', self.on_parent_set)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # DEVICES
        if Extension.mode == 'public':
            self.__class__.devices = {
                'Arduino': ArduinoGeneratorPublic,
                'C': CGeneratorPublic,
                'C++': CPPGeneratorPublic,
                'Kilobot': KilobotGeneratorPublic,
                'Python': PythonGeneratorPublic,
            }
        elif Extension.mode == 'prob':
            self.__class__.devices = {
                'C': CGeneratorProbabilistic,
                'C++': CPPGeneratorProbabilistic,
                'Kilobot': KilobotGeneratorProbabilistic,
                'Python': PythonGeneratorProbabilistic,
            }
        else:
            self.__class__.devices = {
                'Arduino': ArduinoGenerator,
                'C': CGenerator,
                'C++': CPPGenerator,
                'Kilobot': KilobotGenerator,
                'Python': PythonGenerator,
            }

        self.selected_automatons = None
        self.generator = None
        self.output_path = None

        self.automatonlist = list()

        self.prop_box = PropertyBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.prop_box.connect('nadzoru-property-change', self.on_prop_change)

        # self.paned = Gtk.Paned(wide_handle=True)
        # self.paned.set_position(300)
        # self.pack_start(self.paned, True, True, 0)

        btn = Gtk.Button('Execute')
        btn.connect('clicked', self.on_exec_btn)
        self.pack_end(btn, False, False, 0)

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:
            app = widget.get_application()
            app.connect('nadzoru-automatonlist-change',
                        self.on_automatonlist_change)

            self.automatonlist = [(automaton.get_name(), automaton)
                                  for automaton in app.get_automatonlist()]
            self.build_options_box()

    def on_exec_btn(self, button):
        if self.selected_automatons is not None and self.output_path is not None:
            self.generator.write(self.selected_automatons,
                                 self.codegen_args, self.output_path)

    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = [(automaton.get_name(), automaton)
                              for automaton in automatonlist]
        self.list_selector.reset_list(self.automatonlist)

        
        # self.list_selector.add_new_available(label, obj)

    def build_options_box(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_propagate_natural_height(True)
        scrolled.set_propagate_natural_width(True)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled.add(vbox)
        # self.paned.pack1(scrolled, True, True)
        self.pack_start(scrolled, False, False, 0)

        upper_prop_box = PropertyBox(orientation=Gtk.Orientation.HORIZONTAL)
        upper_prop_box.connect('nadzoru-property-change', self.on_prop_change)
        upper_prop_box.set_activate_on_single_click(False)
        vbox.pack_start(upper_prop_box, False, False, 0)
        vbox.pack_start(self.prop_box, False, False, 0)

        self.list_selector = upper_prop_box.add_dualListSelector(None, self.automatonlist, data='selected_automatons', scroll_hmin=150)

        upper_prop_box.add_combobox("Select a device",
                                    [(dev_key, dev_class) for dev_key, dev_class in self.devices.items()], data='selected_device')
        upper_prop_box.add_filechooserbutton(
            "Select a destination folder", None, data='selected_folder', action=Gtk.FileChooserAction.SELECT_FOLDER)
        scrolled.set_size_request(300, -1)


    def on_device_changed(self, widget):
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            device_cls = model[tree_iter][1]
            self.generator = device_cls()
            self.update_options_box()

    def update_options_box(self):
        self.prop_box.clear()
        
        for opt_name, opts in self.generator.get_options():
            if opt_name != 'device':
                if opts['widget_type'] == 'choice':
                    combobox = self.prop_box.add_combobox(
                        opts['label'], opts['options'], data=opt_name)
                    combobox.set_active(0)

    def on_prop_change(self, prop_box, value, property_name, name=None):
        if property_name == 'selected_device':
            self.codegen_args = dict()
            self.generator = value()
            self.update_options_box()
        elif property_name == 'selected_folder':
            self.output_path = value
        elif property_name == 'selected_automatons':
            self.selected_automatons = value
        else:
            self.codegen_args.update({property_name: value})

