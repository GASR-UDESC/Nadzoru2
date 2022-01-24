import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# import sys
# import gi
# from gi.repository import GLib, Gio, Gtk, GObject

from gui.base import PageMixin
from machine.automaton import Automaton

class AutomatonOperation(PageMixin, Gtk.Box): 
    def __init__(self, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(self.main_box)
        self.main_box.connect("button-press-event", self.selected_row_operation)

        self.left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.main_box.pack_start(self.left_box, False, False, 0)
        self.main_box.pack_start(self.right_box, True, True, 0)

        self.attribute_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.state_box =Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0) 

        self.right_box.pack_start(self.attribute_box, True, True, 0)
        self.right_box.pack_start(self.state_box, False, False, 0)  

        self.list_box_selected_automata = Gtk.ListBox()
        self.list_box_button = Gtk.ListBox()
        self.list_box_unselected_automata = Gtk.ListBox()

        self.list_box_operation = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.left_box.pack_start(self.list_box_operation, False, False, 0)

        row = Gtk.ListBoxRow()
        self.list_box_operation.add(row)
        column = Gtk.Label(label="SUPC", xalign=0)
        row.add(column)

        row = Gtk.ListBoxRow()
        self.list_box_operation.add(row)
        column = Gtk.Label(label="SINC", xalign=0)
        row.add(column)


    def selected_row_operation(self,wiget,event):

        print(self.list_box_operation.get_selected_row().get_child().get_text())
        return self.list_box_operation.get_selected_row().get_child().get_text()


    
        



#     class Operation():
#         operation = [
#             {
#                 'label': "SUPC", 'Fn': Automaton.sup_c(), 'params':[
#                     {'label': "G", 'type': 'combobox'},
#                     {'label': "K", 'type': 'combobox'},
#                     {'label': "Result", 'type': 'label'}]},
#             {
#                 'label': "SYNC", 'Fn': Automaton.synchronization(), 'params':[
#                     {'label': "Automaton", 'type': 'mult'},
#                     {'label': "Result", 'type': 'label'}]
#             }

#         ]


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

            
# if __name__ == '__main__':
#     a = AutomatonOperation()
#     a.connect("delete-event", Gtk.main_quit)
#     a.show_all()
#     Gtk.main()

