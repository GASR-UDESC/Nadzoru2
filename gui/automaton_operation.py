from sqlite3 import apilevel
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# import sys
# import gi
# from gi.repository import GLib, Gio, Gtk, GObject

from gui.base import PageMixin
from machine.automaton import Automaton
from gui.property_box import PropertyBox

class AutomatonOperation(PageMixin, Gtk.Box):

    def __init__(self, automata, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.automata = automata
        self.result_name = 'untitled'
        self.result_open = False
        self.selected_op = None
        self.arguments_op = dict()
        self.argumentslist_op = list()
    

        self.operations = [
            {
                'label': "SUPC", 'fn': Automaton.sup_c, 'params': [
                    {'label': "G", 'type': 'combobox', 'name': 'G'},
                    {'label': "K", 'type': 'combobox', 'name': 'R'},
                    {'label': "Result", 'type': 'entry', 'name': 'output'},
                    {'label': "Open result ", 'type':'CheckButton','name':'open'}
                    ]},
            {
                'label': "SYNC", 'fn': Automaton.synchronization, 'params': [
                    {'label': "Automaton", 'type': 'chooser', 'name': 'args'},
                    {'label': "Result", 'type': 'entry', 'name': 'output'},
                    {'label': "Open result ", 'type':'CheckButton','name':'open'}
                    ]
            }

        ]
        # tree View # left column
        self.liststore = Gtk.ListStore(str, object, object)
        self.treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)
        self.selected_row = self.treeview.get_selection()
        self.selected_row.connect("changed", self.item_selected)
        self.cell = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn('Operation', self.cell, text=0)
        self.treeview.append_column(self.column)
        self.pack_start(self.treeview, True, True, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(separator, False, False, 0)
        self.update_treeview()

        self.right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.pack_start(self.right, True, True, 0)

        # execute button
        self.execute_button = Gtk.Button(label='EXECUTE')
        self.execute_button.connect('clicked', self.execute)
        self.right.pack_end(self.execute_button, False, False, 0)

        # property BOX
        self.property_box = PropertyBox()
        self.property_box.connect('nadzoru-property-change', self.prop_edited)
        self.right.pack_start(self.property_box, True, True, 0)

    def prop_edited(self, widget, value, property_name):
        print(property_name)
        if property_name == 'output':
            self.result_name = value
        elif property_name =='open':
            self.result_open = value
        elif property_name == 'args':
            self.argumentslist_op = value
        else:
            self.arguments_op.update({property_name: value})
 
    def execute(self, widget):
        if self.result_name == '' or 'Untitled':
            list_name = []
            for argument in self.argumentslist_op:
                list_name.append(argument.get_name())
            separator = ', '
            self.result_name = f'{str(self.selected_op[0])} ({separator.join(list_name)})'

        # print(self.property_box.get_children()) # probably must check if user selected all necessary inputs
        result = self.selected_op[1](*self.argumentslist_op, **self.arguments_op)  # result is an automaton
        result.set_name(self.result_name)
        print(result)
        #result.save(f"/home/krischanski/Nadzoru2/{self.result_name}.xml") # set your path for testing
        window = self.get_ancestor_window()
        window.props.application.elements.append(result)
        if not(self.result_open):
            return
        window.add_tab_editor(result,result.get_name())
        window.set_tab_label_color(window.get_current_tab_widget(),'#F00')
    

    def update_treeview(self):
        print(self.automata)
        for op in self.operations:
            row = [op['label'], op['fn'], op['params']]
            self.liststore.append(row)

    def item_selected(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            self.arguments_op = dict()
            self.creation_property_operation(str(model[row][0]), model[row][2])
            self.selected_op = (model[row][0],model[row][1])

    def creation_property_operation(self, operation_name, params):
        open_automata = []
        self.property_box.clear()

        for automato in self.automata:
            open_automata.append((automato.get_name(), automato))

        for obj in params:
            if obj['type'] == 'combobox':
                self.property_box.add_combobox(obj['label'], open_automata, data=obj['name'])
            elif obj['type'] == 'entry':
                self.property_box.add_entry(obj['label'], "untitled", data=obj['name'])
            elif obj['type'] == 'chooser':
                self.property_box.add_chooser(obj['label'], [1, 3], open_automata, data=obj['name'])
            elif obj['type'] == 'CheckButton':
                self.property_box.add_checkbutton(obj['label'],self.result_open, data=obj['name'])


#     class Operation():
        # operation = [
        #     {
        #         'label': "SUPC", 'Fn': Automaton.sup_c(), 'params':[
        #             {'label': "G", 'type': 'combobox'},
        #             {'label': "K", 'type': 'combobox'},
        #             {'label': "Result", 'type': 'label'}]},
        #     {
        #         'label': "SYNC", 'Fn': Automaton.synchronization(), 'params':[
        #             {'label': "Automaton", 'type': 'mult'},
        #             {'label': "Result", 'type': 'label'}]
        #     }

        # ]


#         def __init__(self,method, label):
#             self.method = method
#             self.label = label

#         def param_automaton(self,name):
#             # TODO ...
#             return self

#         def param_automata_list(self, name):
#             # TODO ...
#             return self
        
#         def paran_string(self,name):
#             # TODO ...
#             return self
        
#     @classmethod
#     def register_operation(cls,method, label):
#         op = Operation(method, label)
#         self.append(op)
#         return op

            
if __name__ == '__main__':
    a = AutomatonOperation()
    a.connect("delete-event", Gtk.main_quit)
    a.show_all()
    Gtk.main()

