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
        self.automata = automata
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.operations = [
            {
                'label': "SUPC", 'Fn': 'Automaton.sup_c()', 'params':[
                    {'label': "G", 'type': 'combobox'},
                    {'label': "K", 'type': 'combobox'},
                    {'label': "Result", 'type': 'entry'}]},
            {
                'label': "SYNC", 'Fn': 'Automaton.synchronization()', 'params':[
                    {'label': "Automaton", 'type': 'chooser'},
                    {'label': "Result", 'type': 'entry'}]
            }

        ]
        #tree View # left column
        self.liststore = Gtk.ListStore(str, str, object)
        self.treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)
        self.selected_row = self.treeview.get_selection()
        self.selected_row.connect("changed", self.item_selected)
        self.cell = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn('Operation', self.cell, text=0)
        self.treeview.append_column(self.column)
        self.pack_start(self.treeview, True, True, 0)
        self.update_treeview()

        self.right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.pack_start(self.right, True, True,0)

        #execute button
        self.execute_button = Gtk.Button(label = 'EXECUTE')
        self.execute_button.connect('clicked', self.execute)
        self.right.pack_end(self.execute_button, True,True,0)

        #property BOX
        self.property_box = PropertyBox()
        self.right.pack_start(self.property_box,True, True,0)
       

    def execute(self, widget):
        print("Executed")
        pass



    def update_treeview(self):
        for op in self.operations:
            row = [op['label'], op['Fn'],op['params']]
            self.liststore.append(row)


    def item_selected(self,selection):
        model, row = selection.get_selected()
        if row is not None:
            self.creation_property_operation(str(model[row][0]),model[row][2])
            

    def creation_property_operation(self, operation_name,params):
        open_automata=[]
        self.property_box.clear()
        
        for automato in self.automata:
            open_automata.append((automato.get_file_name(), automato))
            

        for obj in params:
            if obj['type'] == 'combobox':
                self.property_box.add_combobox(obj['label'],open_automata)
            elif obj['type'] == 'entry':
                self.property_box.add_entry(obj['label'],"untitled")
            elif obj['type'] == 'chooser':
                self.property_box.add_chooser(obj['label'],[1,3],options=open_automata)
            
        

    def selected_row_operation(self,widget,event):
        print(self.operation_box.prop_edited())

        print(self.list_box_operation.get_selected_row().get_child().get_text())
        return self.list_box_operation.get_selected_row().get_child().get_text()


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

