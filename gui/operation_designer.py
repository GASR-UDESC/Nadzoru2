import gi
import re #teste
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui.base import PageMixin
from machine.automaton import Automaton
from inspect import signature

class OperationMacro:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.function_args = args if args else []
        self.function_kwargs = kwargs if kwargs else {}
        self.func_params = {param: None for param in signature(func).parameters}


    def __call__(self, *args, **kwargs):
        args = [
            arg(*args, **kwargs) if isinstance(arg, OperationMacro) else arg
            for arg in self.function_args
        ]
        kwargs = {
            key: value(*args, **kwargs) if isinstance(value, OperationMacro) else value
            for key, value in self.function_kwargs.items()
        }
        
        return self.func(*args, **kwargs)

    
    def pass_argument(self, arg, value):
        if arg not in self.func_params:
            raise Exception(f'Argument {arg} not found')
        if callable(value):
            child = OperationMacro(value)
            self.function_kwargs[arg] = child
            return child
        else:
            self.function_kwargs[arg] = value

class OperationDesigner(PageMixin, Gtk.Box):
    operations = [
        {
            'label': "SupC", 'fn': Automaton.sup_c, 'params': [
                {'label': "G", 'type': 'combobox', 'name': 'G'},
                {'label': "K", 'type': 'combobox', 'name': 'R'},
                ]},
        {
            'label': "Sync", 'fn': Automaton.synchronization, 'params': [
                {'label': "List", 'type': 'duallistselector', 'name': 'args'},
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
                {'label': "AutAutomaton.SupC(G, R)omaton", 'type': 'combobox', 'name': 'self'},
                {'label': "Labeller", 'type': 'combobox', 'name': 'labeller'}
            ]},
    ]
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.automatonlist = list()
        self.connect('parent-set', self.on_parent_set)
        
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=5)
        
        self.text_editor = Gtk.TextView()
        self.buffer = self.text_editor.get_buffer()

        # development only
        btn = Gtk.Button(label='Execute')
        btn.connect('clicked', self._on_exec_btn)
        self.vbox.pack_end(btn, False, False, 0)
        
        self.operation_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=5)
        self.operations_list = Gtk.ListStore(str, object, object)
        self.operations_view = self._build_operations_view(self.operations_list)
        btn = Gtk.Button(label='Add')
        btn.connect('clicked', self._on_add_operation_btn)
        self.operation_vbox.pack_end(btn, False, False, 0)
        self.operation_vbox.pack_start(self.operations_view, True, True, 0)

        self.automatonlist_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=5)
        self.automatonliststore = Gtk.ListStore(str, object)
        self.automatonlist_view = self._build_automatons_view(self.automatonliststore)
        btn = Gtk.Button(label='Add')
        btn.connect('clicked', self._on_add_automaton_btn)
        self.automatonlist_vbox.pack_end(btn, False, False, 0)
        self.automatonlist_vbox.pack_start(self.automatonlist_view, True, True, 0)

        self.vbox.pack_start(self.text_editor, True, True, 0)
        self.pack_start(self.operation_vbox, False, False, 0)

        self.pack_start(self.automatonlist_vbox, True, True, 0)
        self.pack_start(self.vbox, True, True, 0)

    def on_parent_set(self, widget, oldparent):     # Widget is self
        # GTK removes self's parent first when a tab is moved to another window or
        # when the application is closed, thus, it isn't possible to get_application.
        # This happens when there was a parent, that is, oldparent isn't None.
        if oldparent is None:                       
            app = widget.get_application()          
            app.connect('nadzoru-automatonlist-change', self.on_automatonlist_change)
            self.automatonlist = app.get_automatonlist()
            self._update_automatons_list()


    
    def on_automatonlist_change(self, widget, automatonlist):
        self.automatonlist = automatonlist
        self._update_automatons_list()

    def _build_automatons_view(self, liststore):
        treeview = Gtk.TreeView(model=liststore)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Automatons', cell, text=0)
        treeview.append_column(column)
        treeview.set_enable_search(True)
        # treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        self._update_automatons_list()
        return treeview
        
    def _update_automatons_list(self):
        self.automatonliststore.clear()
        rows = list()
        for automaton in self.automatonlist:
            rows.append([automaton.get_name(), automaton])

        rows.sort(key=lambda row: row[0])

        for row in rows:
            self.automatonliststore.append(row)


    def _build_operations_view(self, liststore):
        treeview = Gtk.TreeView(model=liststore)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Available Operations', cell, text=0)
        treeview.append_column(column)
        treeview.set_enable_search(True)

        self._update_operations_list()
        return treeview

    def _update_operations_list(self):
        for op in self.operations:
            self.operations_list.append([op['label'], op['fn'], op['params']])

    def get_selected_operation(self):
        selection = self.operations_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is None:
            raise Exception("No operation selected")

        return model[treeiter]

    def _on_add_automaton_btn(self, button):
        name, automaton = self.get_selected_automatons()
        self.insert_text(name)

    def get_selected_automatons(self):
        selection = self.automatonlist_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is None:
            raise Exception("No operation selected")

        return model[treeiter]


    def _on_add_operation_btn(self, button):
        label, fn, params = self.get_selected_operation()
        
        self.insert_text(f"{label}(")
        text=''
        for param in params:
            label = param['label']
            text += f'{label} =  , '
        text = text.rstrip(", ")
        self.insert_text(text)

        self.resulting_code = fn
        

    def insert_text_end(self, text):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, text)

    def insert_text(self, text):
        iter_insert = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        self.buffer.insert(iter_insert, text)

    def _on_exec_btn(self, button):
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        code = self.buffer.get_text(start_iter, end_iter, True)
        file_paths = re.findall(r"'(.*?\.xml)'", code)

        app = self.get_application()
        
        def keep(element, name=None):
            if name is not None:
                element.set_name(name)
            app.elements.append(element)
            # TODO: reload Automaton>Edit and Automaton>Simulate quick names, open does this, how? 
        exec_scope = {'Automaton': Automaton, 'keep': keep}
        for element in app.elements:
            element_id_name = element.get_id_name()
            if element_id_name in exec_scope:
                print(f"Erro: O nome '{element_id_name}' já está em exec_scope.")
            else:
            # TODO: check if the name already in exec_scope, if so it's an error -- feito acima a principio
                exec_scope[element.get_id_name()] = element
        # print(exec_scope)
        
        try:
            exec(code, exec_scope)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    win = Gtk.Window()
    designer = OperationDesigner()

    win.add(designer)
    win.set_size_request(300, 150)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


            # result = self.op_fn(*self.argumentslist_op, **self.kwarguments_op)  # result is an automaton
            # result.clear_file_path_name()
            # result.set_name(self.result_name)
            # self.get_application().add_to_automatonlist(result)
            # self.result_name = ""
            # result.arrange_states_position()

            # if not (self.result_open):
            #     return
            # window = self.get_ancestor_window()
            # window.add_tab_editor(result, result.get_name())
            # window.set_tab_label_color(window.get_current_tab_widget(), 'label-red')