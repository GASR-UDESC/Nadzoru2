import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, GObject
from gui.dual_list_selector import DualListSelector

class PropertyBox(Gtk.ListBox):
    def __init__(self, orientation=Gtk.Orientation.HORIZONTAL, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.orientation = orientation

    def clear(self):
        for row in self:
            row.destroy()

    def _add_row(self, label_text, widget):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=self.orientation, spacing=0)
        row.add(hbox)
        self.add(row)
        if label_text is not None:
            if self.orientation is Gtk.Orientation.HORIZONTAL:
                label = Gtk.Label(label=label_text, xalign=0)
            else:
                label = Gtk.Label(label=label_text)
            hbox.pack_start(label, True, True, 0)
            hbox.pack_start(widget, False, False, 0)
        else:
            hbox.pack_start(widget, True, True, 0)
        self.show_all()

    def add_checkbutton(self, label, value, data=None, callback=None):
        widget = Gtk.CheckButton(active=value)
        widget.connect('toggled', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)
        return widget

    def add_switch(self, label, value, data=None, callback=None):
        widget = Gtk.Switch(active=value)
        widget.connect('notify::active', self.prop_edited, data, callback, None)
        self._add_row(label, widget)
        return widget

    def add_entry(self, label, value, data=None, callback=None, placeholder=None):
        widget = Gtk.Entry(text=str(value), xalign=1, width_chars=10, has_frame=False)
        widget.connect('activate', self.prop_edited, None, data, callback, None)
        if placeholder is not None:
            widget.set_placeholder_text(placeholder)
        self._add_row(label, widget)
        return widget

    def add_spinbutton(self, label, value, data=None, callback=None, lower=0, upper=1000, step_increment=1, page_increment=100, width_chars=4):
        adjustment = Gtk.Adjustment(value=value, lower=lower, upper=upper, step_increment=step_increment, page_increment=page_increment)
        widget = Gtk.SpinButton(adjustment=adjustment, width_chars=width_chars)
        widget.connect('value-changed', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)
        return widget

    def add_combobox(self, label, options, value=None, data=None, callback=None): 
        ### options = [("Label", Object), ("Label", Object)]
        widget = Gtk.ComboBoxText()
        #widget.set_entry_text_column(0)

        widget.connect('changed', self.prop_edited, None, data, callback, options)
        for option in options:
            widget.append_text(option[0])
        self._add_row(label, widget)
        return widget

    def add_dualListSelector(self, label, options, value=None, data=None, callback=None, *args, **kwargs):
        widget = DualListSelector(data=options, *args, **kwargs)     
        widget.connect('selected-changed', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)
        return widget


    def add_chooser(self, label, value, options, data=None, callback=None, scrollable=False, scroll_hmax=200, scroll_hmin=200):
        widget = Chooser()
        widget.add_chooser(label, value, options, data, callback, scrollable, scroll_hmax, scroll_hmin)
        widget.connect('nadzoru-chooser-change', self.chooser_changed, callback)
        self._add_row(label, widget)
        return widget

    def add_filechooserbutton(self, label, value, data=None, callback=None, action=Gtk.FileChooserAction.OPEN):
        widget = Gtk.FileChooserButton()
        widget.set_action(action)
        widget.connect('file-set', self.prop_edited, None, data, callback, None)
        self._add_row(label, widget)
        return widget
        

    def chooser_changed(self, chooser, selected, data, callback):
        self.prop_edited(chooser, None, data, callback, selected)

    def emit_nadzoru_property_change(self, value, data, name=None):
        self.emit('nadzoru-property-change', value, data, name)

    def prop_edited(self, widget, gparam, data, callback, values, *args, **kwargs):
        # print("PropertyBox.prop_edited: ", widget, gparam, data, callback, values, args)
        # for kwarg in kwargs:
        #     print(kwarg)
        if type(widget) == Gtk.CheckButton:
            value = widget.get_active()
        elif type(widget) == Gtk.Switch:
            value = widget.get_active()
        elif type(widget) == Gtk.Entry:
            value = widget.get_text()
        elif type(widget) == Gtk.SpinButton:
            value = widget.get_value_as_int()
        elif  type(widget) == Gtk.ComboBoxText:
            tree_iter = widget.get_active_iter()
            if tree_iter is not None:
                #model = widget.get_model()
                tree_indice = widget.get_active()
                selected_value = values[tree_indice][1]
                value = selected_value
        elif type(widget) == Gtk.FileChooserButton:
            value = widget.get_filename()
        elif type(widget) == Chooser:
            value = values
        elif type(widget) == DualListSelector:
            value = widget.get_selected_objects()
        else:
            value = None

        self.emit_nadzoru_property_change(value, data, widget.get_name())
        if callback is not None:
            callback(widget, value, data)

class Chooser(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.selected = list()
        self.unselected = list()
        self.data = None
        self.property_name = None

    def add_chooser(self, label, value, options, data=None, callback=None, scrollable=False, scroll_hmax=200, scroll_hmin=200):
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
            treeview.set_enable_search(True)
            
            return treeview, selection

        # create unselected treeview widget
        self.unsel_ls = Gtk.ListStore(str, object)
        unsel_tv, unsel_selection = _create_treeview(self.unsel_ls, "Unselected")

        # create selected treeview widget
        self.sel_ls = Gtk.ListStore(str, object)
        sel_tv, sel_selection = _create_treeview(self.sel_ls, "Selected")

        # create buttons widget
        hbox_buttons = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, homogeneous=True)
        btn = Gtk.Button(label = "----->")
        btn.connect('clicked', self._chooser_btns, unsel_selection, self.selected, self.unselected)
        hbox_buttons.pack_start(btn, True, False, 0)
        btn = Gtk.Button(label = "<-----")
        btn.connect('clicked', self._chooser_btns, sel_selection, self.unselected, self.selected)
        hbox_buttons.pack_start(btn, True, False, 0)

        # add all widgets to box
        if scrollable:
            def _add_scroll(treeview, scroll_hmax, scroll_hmin):
                scrolled = Gtk.ScrolledWindow(max_content_height=scroll_hmax, min_content_height=scroll_hmin)
                scrolled.add(treeview)
                scrolled.set_propagate_natural_height(True)
                scrolled.set_propagate_natural_width(True)
                return scrolled
            
            unsel_scroll = _add_scroll(unsel_tv, scroll_hmax, scroll_hmin)
            sel_scroll = _add_scroll(sel_tv, scroll_hmax, scroll_hmin)
            self.pack_start(unsel_scroll, True, True, 0)
            self.pack_start(hbox_buttons, False, False, 25)
            self.pack_start(sel_scroll, True, True, 0)
        else:
            self.pack_start(unsel_tv, True, True, 0)
            self.pack_start(hbox_buttons, False, False, 25)
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
        out_selected_list = list()
        for _list in self.selected:
            out_selected_list.append(_list[1])
        self.emit('nadzoru-chooser-change', out_selected_list, self.property_name)

    def update(self, new_obj_list):
        objs_in_chooser = set()
        for row in self.selected:
            objs_in_chooser.add(tuple(row))
        for row in self.unselected:
            objs_in_chooser.add(tuple(row))

        objs_to_append = [list(obj) for obj in new_obj_list if obj not in objs_in_chooser]
        for obj in objs_to_append:
            self.unselected.append(obj)
        self.update_chooser()

        
# class OptionsBox(Gtk.Box):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs):

        
GObject.signal_new('nadzoru-chooser-change',
    Chooser,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,))

GObject.signal_new('nadzoru-property-change',
    PropertyBox,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,))