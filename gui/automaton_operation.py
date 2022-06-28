
from gi.repository import Gtk

# import sys
# import gi
# from gi.repository import GLib, Gio, Gtk, GObject

from gui.base import PageMixin
from machine.automaton import Automaton
from gui.property_box import PropertyBox

class AutomatonOperation(PageMixin, Gtk.Box):

    def __init__(self, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.automatonlist = list()
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.connect('parent-set', self.on_parent_set)

        self.result_name = ""
        self.result_open = False
        self.selected_op = None

        self.clear_oparguments()

        self.operations = [
            {
                'label': "SUPC", 'fn': Automaton.sup_c, 'params': [
                    {'label': "G", 'type': 'combobox', 'name': 'G'},
                    {'label': "K", 'type': 'combobox', 'name': 'R'},
                    {'label': "Result", 'type': 'entry', 'name': 'output', 'default_value': "",  'placeholder': "type a name"},
                    {'label': "Open result ", 'type':'CheckButton','name':'open'}
                    ]},
            {
                'label': "SYNC", 'fn': Automaton.synchronization, 'params': [
                    {'label': "Automaton", 'type': 'chooser', 'name': 'args'},
                    {'label': "Result", 'type': 'entry', 'name': 'output', 'default_value': "", 'placeholder': "type a name" },
                    {'label': "Open result ", 'type':'CheckButton','name':'open'}
                    ]
            }
        ]

        self.build_treeview()   # Build the treeview in the left side
        
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(separator, False, False, 0)

        self.right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.pack_start(self.right, True, True, 0)

        # execute button
        execute_button = Gtk.Button(label='EXECUTE')
        execute_button.connect('clicked', self.execute)
        self.right.pack_end(execute_button, False, False, 0)

        # property BOX
        self.property_box = PropertyBox()
        self.property_box.connect('nadzoru-property-change', self.prop_edited)
        self.right.pack_start(self.property_box, True, True, 0)

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:                       
            app = widget.get_application()          
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()

    def clear_oparguments(self):
        self.arguments_op = dict()
        self.argumentslist_op = list()

    def build_treeview(self):
        self.liststore = Gtk.ListStore(str, object, object)
        treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)
        self.selected_row = treeview.get_selection()
        self.selected_row.connect("changed", self.item_selected)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Operation', cell, text=0)
        treeview.append_column(column)
        self.pack_start(treeview, True, True, 0)

        for op in self.operations:
            row = [op['label'], op['fn'], op['params']]
            self.liststore.append(row)

    def prop_edited(self, widget, value, property_name):
        if property_name == 'output':
            self.result_name = value
        elif property_name == 'open':
            self.result_open = value
        elif property_name == 'args':
            self.argumentslist_op = value
        else:
            self.arguments_op.update({property_name: value})

    def execute(self, widget):
        if self.result_name == '':
            list_name = []
            for argument in self.argumentslist_op:
                list_name.append(argument.get_name())
            separator = ', '
            self.result_name = f'{str(self.selected_op[0])} ({separator.join(list_name)})'
        # print(self.property_box.get_children()) # probably must check if user selected all necessary inputs
        operation_fn = self.selected_op[1]
        result = operation_fn(*self.argumentslist_op, **self.arguments_op)  # result is an automaton
        result.clear_file_path_name(name=self.result_name)

        self.get_application().add_to_automatonlist(result)

        if not(self.result_open):
            return
        window = self.get_ancestor_window()
        window.add_tab_editor(result, result.get_name())
        window.set_tab_label_color(window.get_current_tab_widget(), 'label-red')

    def item_selected(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            self.clear_oparguments()
            op_params = model[row][2]
            op_label = str(model[row][0])
            op_fn = model[row][1]
            self.creation_property_operation(op_label, op_params)
            self.selected_op = (op_label, op_fn, op_params)

    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        op_label = self.selected_op[0]
        op_params = self.selected_op[2]
        self.creation_property_operation(op_label, op_params)

    def creation_property_operation(self, operation_name, params):
        open_automata = []
        self.property_box.clear()
        for automato in self.automatonlist:
            open_automata.append((automato.get_name(), automato))

        for obj in params:
            if obj['type'] == 'combobox':
                self.property_box.add_combobox(obj['label'], open_automata, data=obj['name'])
            elif obj['type'] == 'entry':
                self.property_box.add_entry(obj['label'], obj['default_value'], data=obj['name'], placeholder=obj.get('placeholder', None))
            elif obj['type'] == 'chooser':
                self.property_box.add_chooser(obj['label'], [], open_automata, data=obj['name'], scrollable=True, scroll_hmax=300, scroll_hmin=200) # Check if list is really needed
            elif obj['type'] == 'CheckButton':
                self.property_box.add_checkbutton(obj['label'],self.result_open, data=obj['name'])

