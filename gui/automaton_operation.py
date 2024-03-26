
from gi.repository import Gtk
from gui.base import PageMixin
from machine.automaton import Automaton
from gui.property_box import PropertyBox
import machine.exceptions as expt

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
        self.op_label = None
        self.op_fn = None
        self.op_params = None

        self.clear_oparguments()

        self.operations = [
            {
                'label': "SupC", 'fn': Automaton.sup_c, 'params': [
                    {'label': "G", 'type': 'combobox', 'name': 'G'},
                    {'label': "K", 'type': 'combobox', 'name': 'R'},
                    ]},
            {
                'label': "Sync", 'fn': Automaton.synchronization, 'params': [
                    {'label': "Automaton", 'type': 'duallistselector', 'name': 'args'},
                    ]},
            {
                'label': "Observer", 'fn': Automaton.observer, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'}
                ]},
            {
                'label': "Accessible", 'fn': Automaton.accessible, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'}
                ]},
            {
                'label': "Coaccessible", 'fn': Automaton.coaccessible, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'}
                ]},
            {
                'label': "Trim", 'fn': Automaton.trim, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'}
                ]},
            {
                'label': "Minimize", 'fn': Automaton.minimize, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'}
                ]},
            {
                'label': "Supervisor Reduction", 'fn': Automaton.supervisor_reduction, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'},
                    {'label': "G", 'type': 'combobox', 'name': 'G'},
                    {'label': "Criteria", 'type': 'explicit_combobox', 'cb_content': [("Minimum dependancies", 'b'), ("Target state intersection", 'c'), ("Future agregation", 'd'), ("Random", 'e')], 'name': 'criteria'}]},
            {
                'label': "Labeller", 'fn': Automaton.labeller, 'params': [
                    {'label': "Fault events", 'type': 'ev_chooser', 'name': 'fault_events'}
                ]},
            {
                'label': "Diagnoser", 'fn': Automaton.diagnoser, 'params': [
                    {'label': "Automaton", 'type': 'combobox', 'name': 'self'},
                    {'label': "Labeller", 'type': 'combobox', 'name': 'labeller'}
                ]},
        ]

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.pack_start(left_box, True, True, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(separator, False, False, 0)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.pack_start(right_box, True, True, 0)

        # Treeview with the list of operations
        treeview = self.build_treeview()  
        left_box.pack_start(treeview, True, True, 0)

        # Operation execute button
        execute_button = Gtk.Button(label='EXECUTE')
        execute_button.connect('clicked', self.on_execute_btn)
        right_box.pack_end(execute_button, False, False, 0)

        # Parameter editor box
        self.property_box = PropertyBox()
        self.property_box.connect('nadzoru-property-change', self.prop_edited)
        right_box.pack_start(self.property_box, True, True, 0)

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:                       
            app = widget.get_application()          
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()

    def clear_oparguments(self):
        self.kwarguments_op = dict()
        self.argumentslist_op = list()

    def build_treeview(self):
        liststore = Gtk.ListStore(str, object, object)
        treeview = Gtk.TreeView(model=liststore, headers_visible=False)
        selected_row = treeview.get_selection()
        selected_row.connect("changed", self.on_operation_selected)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Operation', cell, text=0)
        treeview.append_column(column)
        

        for op in self.operations:
            row = [op['label'], op['fn'], op['params']]
            liststore.append(row)
        
        return treeview
    
    def on_add_btn(self, widget):
        self.get_ancestor_window().add_tab_operationdesigner()
    
    def prop_edited(self, widget, value, property_name):
        if property_name == 'output':
            self.result_name = value
        elif property_name == 'open':
            self.result_open = value
        elif property_name == 'args':
            self.argumentslist_op = value
        else:
            self.kwarguments_op.update({property_name: value})

    def on_execute_btn(self, widget):
        if self.result_name == "":
            list_name = []
            for argument in self.argumentslist_op:
                if type(argument) is Automaton:
                    list_name.append(argument.get_name())
            for key, value in self.kwarguments_op.items():
                if type(value) is Automaton:
                    list_name.append(f'{key}: {value.get_name()}')
            separator = ', '
            self.result_name = f'{str(self.op_label)} ({separator.join(list_name)})'
        # print(self.property_box.get_children()) # probably must check if user selected all necessary inputs

        def push_msg_statusbar(message):
            win = self.get_ancestor_window()
            win.statusbar.push(message)

        try:
            result = self.op_fn(*self.argumentslist_op, **self.kwarguments_op)  # result is an automaton
            result.clear_file_path_name()
            result.set_name(self.result_name)
            self.get_application().add_to_automatonlist(result)
            self.result_name = ""
            result.arrange_states_position()

            if not (self.result_open):
                return
            window = self.get_ancestor_window()
            window.add_tab_editor(result, result.get_name())
            window.set_tab_label_color(window.get_current_tab_widget(), 'label-red')

        except expt.NadzoruError as e:
            push_msg_statusbar(str(e))


    def on_operation_selected(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            self.clear_oparguments()
            self.op_params = model[row][2]
            self.op_label = str(model[row][0])
            self.op_fn = model[row][1]
            self.build_rhs_operation_box(self.op_label, self.op_params)

    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        if self.op_fn:
            self.build_rhs_operation_box(self.op_label, self.op_params)

    def build_rhs_operation_box(self, operation_name, params):
        open_automata = list()
        _events = dict()
        events = list()
        self.property_box.clear()

        for automato in self.automatonlist:
            open_automata.append((automato.get_name(), automato))
            for event in automato.events:
                _events[event.name] = event
        
        for k, v in _events.items():
            events.append((k, v))

        for obj in params:
            if obj['type'] == 'explicit_combobox':
                self.property_box.add_combobox(obj['label'], obj['cb_content'], data=obj['name'])
            elif obj['type'] == 'ev_combobox':
                self.property_box.add_combobox(obj['label'], events, data=obj['name'])
            elif obj['type'] == 'ev_chooser':
                self.property_box.add_chooser(obj['label'], [], events, data=obj['name'], scrollable=True, scroll_hmax=300, scroll_hmin=200)
            elif obj['type'] == 'combobox':
                self.property_box.add_combobox(obj['label'], open_automata, data=obj['name'])
            elif obj['type'] == 'entry':
                self.property_box.add_entry(obj['label'], obj['default_value'], data=obj['name'], placeholder=obj.get('placeholder', None))
            elif obj['type'] == 'chooser':
                self.property_box.add_chooser(obj['label'], [], open_automata, data=obj['name'], scrollable=True, scroll_hmax=300, scroll_hmin=200) # Check if list is really needed
            elif obj['type'] == 'checkbutton':
                self.property_box.add_checkbutton(obj['label'],self.result_open, data=obj['name'])
            elif obj['type'] == 'duallistselector':
                self.property_box.add_dualListSelector(obj['label'], open_automata, data=obj['name'])

        # build the default widgets: entry for naming the new automaton; checkbutton asking if it should be opened in editor
        self.property_box.add_entry("Result", "", data='output', placeholder="type a name")
        self.property_box.add_checkbutton("Open result ", self.result_open, data='open')
