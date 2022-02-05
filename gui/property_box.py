import gi
gi.require_version("Gtk", "3.0")  # TEST
import logging
from gi.repository import GLib, Gio, Gtk, GObject

class PropertyBox(Gtk.ListBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

    def clear(self):
        for row in self:
            row.destroy()

    def _add_row(self, label_text, widget):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row.add(hbox)
        self.add(row)

        label = Gtk.Label(label=label_text, xalign=0)
        hbox.pack_start(label, True, True, 0)
        hbox.pack_start(widget, False, False, 0)
        self.show_all()

    def add_checkbutton(self, label, value, data=None, callback=None):
        widget = Gtk.CheckButton(active=value)
        widget.connect('toggled', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)

    def add_switch(self, label, value, data=None, callback=None):
        widget = Gtk.Switch(active=value)
        widget.connect('notify::active', self.prop_edited, data, callback, None)
        self._add_row(label, widget)

    def add_entry(self, label, value, data=None, callback=None):
        widget = Gtk.Entry(text=str(value), xalign=1, width_chars=10, has_frame=False)
        widget.connect('activate', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)

    def add_spinbutton(self, label, value, data=None, callback=None, lower=0, upper=1000, step_increment=1, page_increment=100, width_chars=4):
        adjustment = Gtk.Adjustment(value=value, lower=lower, upper=upper, step_increment=step_increment, page_increment=page_increment)
        widget = Gtk.SpinButton(adjustment=adjustment, width_chars=width_chars)
        widget.connect('value-changed', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)

    def add_combobox(self, label, options, value=None, data=None, callback=None): 
        ### options = [("Label", Object), ("Label", Object)]
        widget = Gtk.ComboBoxText()
        #widget.set_entry_text_column(0)


        widget.connect('changed', self.prop_edited, None, data, callback, options)
        for option in options:
            widget.append_text(option[0])
        self._add_row(label, widget)

    # def add_combobox(self, label, options,value=None, data=None, callback=None):  
    #     store = Gtk.ListStore(str)
    #     for option in options:
    #         store.append([option[0]])
    #     widget = Gtk.ComboBox()
    #     tree = Gtk.TreeView(store)
    #     tree.connect('button-press-event', self.prop_edited, None, data, callback)
    #     selector = tree.get_selection()
    #     widget_cell_text = Gtk.CellRendererText()
    #     column_text = Gtk.TreeViewColumn(f"{label}", widget_cell_text, text=0)
    #     tree.append_column(column_text)
    #     widget.add(tree)
    #     self._add_row(label, widget)


    def add_chooser(self, label, value, options, data=None, callback=None):
        widget = Chooser()
        widget.add_chooser(label, value, options, data, callback)
        widget.connect('nadzoru-chooser-change', self.chooser_changed)
        self._add_row(label, widget)

    def chooser_changed(self, chooser, selected, data):
        self.prop_edited(chooser, None, data, None, selected)

    def prop_edited(self, widget, gparam, data, callback, values):
        if type(widget) == Gtk.CheckButton:
            value = widget.get_active()
        elif type(widget) == Gtk.Switch:
            value = widget.get_active()
        elif type(widget) == Gtk.Entry:
            value = widget.get_text()
        elif type(widget) == Gtk.SpinButton:
            value = widget.get_value_as_int()
        elif  type(widget)== Gtk.ComboBoxText:
            tree_iter = widget.get_active_iter()
            if tree_iter is not None:
                #model = widget.get_model()
                tree_indice = widget.get_active()
                automaton = values[tree_indice][1]
                value = automaton
                
        elif type(widget) == Chooser:
            value = values
        else:
            value = None

        self.emit('nadzoru-property-change', value, data)
        if callback is not None:
            callback(value, data)

class Chooser(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.selected = list()
        self.unselected = list()
        self.data = None
        self.property_name = None

    def add_chooser(self, label, value, options, data=None, callback=None):
        # self.options = options
        self.property_name = data
        for obj_label, obj in options:
            self.unselected.append([obj_label, obj])

        def _create_treeview(liststore, column_label):
            treeview = Gtk.TreeView(model=liststore)
            selection = treeview.get_selection()
            selection.set_mode(Gtk.SelectionMode.MULTIPLE)
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_label, cell, text=0)
            treeview.append_column(column)
            
            return treeview, selection

        # create unselected treeview widget
        self.unsel_ls = Gtk.ListStore(str, object)
        unsel_tv, unsel_selection = _create_treeview(self.unsel_ls, "Automaton")

        # create selected treeview widget
        self.sel_ls = Gtk.ListStore(str, object)
        sel_tv, sel_selection = _create_treeview(self.sel_ls, "Automaton")

        # create buttons widget
        hbox_buttons = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        btn = Gtk.Button(label = "----->")
        btn.connect('clicked', self._chooser_btns, unsel_selection, self.selected, self.unselected)
        hbox_buttons.pack_start(btn, True, False, 0)
        btn = Gtk.Button(label = "<-----")
        btn.connect('clicked', self._chooser_btns, sel_selection, self.unselected, self.selected)
        hbox_buttons.pack_start(btn, True, False, 0)

        # add all widgets to box
        self.pack_start(unsel_tv, True, True, 0)
        self.pack_start(hbox_buttons, False, True, 25)
        self.pack_start(sel_tv, True, True, 0)

        self.update_chooser()

    def _chooser_btns(self, widget, selection, list_to_add, list_to_remove):
        liststore, tree_path_list = selection.get_selected_rows()
        if tree_path_list is not None:
            for tree_path in tree_path_list:
                tree_iter = liststore.get_iter(tree_path)
                row = ([liststore[tree_iter][0], liststore[tree_iter][1]])
                list_to_add.append(row)
                list_to_remove.remove(row)
            self.update_chooser()
    
    def update_chooser(self):
        self.unselected.sort(key=lambda row: row[0])
        self.selected.sort(key=lambda row: row[0])
        
        self.unsel_ls.clear()
        for row in self.unselected:
            self.unsel_ls.append(row)

        self.sel_ls.clear()
        for row in self.selected:
            self.sel_ls.append(row)
        selected_automatons = list()
        for automaton_list in self.selected:
            selected_automatons.append(automaton_list[1])
        self.emit('nadzoru-chooser-change', selected_automatons, self.property_name)
        
GObject.signal_new('nadzoru-chooser-change',
    Chooser,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,))

GObject.signal_new('nadzoru-property-change',
    PropertyBox,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,))

if __name__ == '__main__':
    def cbk(prop, *args, **kwargs):
         print(args)
         print(kwargs)

    win = Gtk.Window()
    box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
    prop = PropertyBox()
    prop.add_entry("Valor de X", 100, 'x')
    prop.add_entry("Valor de y", 200, 'y')
    prop.add_spinbutton("Valor do fator", 1, 'fator')
    #prop.connect('nadzoru-property-change', cbk)
    #prop.add_combobox("Automata", 2, options=[("first", 1), ("second", 2), ("third", 3)], 'g')
    #prop.add_chooser("Automata", [1,3], options=[("first", 1), ("second", 2), ("third", 3)], 'g')
    #prop.add_combobox('Moedas',[("Euro",1),("US Dollars",2),("British Pound",3)])
    #prop.add_combobox('Moedas',[("Euro",1),("US Dollars",2),("British Pound",3)])
    prop.add_combobox("Automata",[("first", 1), ("second", 2), ("third", 3)])
    prop.add_checkbutton(label= 'TESTE',value = 'toggled' )
    prop.add_chooser("Automata", [1,3], options=[("first", "1"), ("second", "2"), ("third", "3")])

    def rebuild(*args, **kwargs):
        prop.clear()
        prop.add_entry("Valor de X2", 100, 'x')
        prop.add_entry("Valor de y2", 200, 'y')
        prop.add_spinbutton("Valor do fatorx", 1, 'fator')
        #prop.add_combobox('Moedas',[("Euro",1),("US Dollars",2),("British Pound",3)])
        #prop.add_combobox('Moedas',["Euro","US Dollars","British Pound","Japanese Yen","Russian Ruble","Mexican peso","Swiss franc"])
        prop.add_combobox("Automata",[("first", 1), ("second", 2), ("third", 3)])
        prop.add_checkbutton(label= 'TESTE',value = 'toggled')

        prop.show_all()

    btn = Gtk.Button(label = "Rebuild props")
    btn.connect('clicked', rebuild)

    box.pack_start(prop, True, True, 0)
    box.pack_start(btn, True, True, 0)



    win.add(box)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
