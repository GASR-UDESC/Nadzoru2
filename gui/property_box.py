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
        
    def add_event_table(self, label, columns, events, data=None, callback=None):
        def on_table_changed():
            self.prop_edited(widget, None, data, callback, None)
            
        widget = EventTableWidget(columns, events, on_table_changed)
        
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.pack_start(Gtk.Label(label=label, xalign=0), False, False, 0)
        vbox.pack_start(widget, True, True, 0)
        row.add(vbox)
        self.add(row)
        self.show_all()
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
            
        elif type(widget) == EventTableWidget:
            value = widget.get_data() # Puxa todas as linhas da tabela formatadas
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

class EventTableWidget(Gtk.Box):
    def __init__(self, columns, events, on_change_callback):
        Gtk.Box.__init__(self) # Failsafe init
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.columns = columns
        self.events = events
        self.on_change_callback = on_change_callback 
        self.rows = []

        self.rows_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.pack_start(self.rows_box, True, True, 0)
        
        btn_add = Gtk.Button(label="+ Add Event")
        btn_add.connect('clicked', self.on_add_row)
        
        btn_save = Gtk.Button(label="Save")
        btn_save.connect('clicked', self.on_save_clicked)

        btn_import = Gtk.Button(label="Import")
        btn_import.connect('clicked', self.on_import_clicked)
        
        box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box_btn.pack_start(btn_add, False, False, 0)
        box_btn.pack_start(btn_save, False, False, 0)
        box_btn.pack_start(btn_import, False, False, 0)
        box_btn.pack_start(btn_import, False, False, 0)
        self.pack_start(box_btn, False, False, 10)

        # Create SizeGroups for alignment
        self.sg_event = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.sg_ctrl = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.sg_io = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.sg_cols = {col_key: Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL) for col_key in self.columns}
        self.sg_action = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        # cabecalho tabela
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        def _add_header_col(label_text, sg):
            lbl = Gtk.Label(label=label_text, xalign=0.5)
            sg.add_widget(lbl)
            header.pack_start(lbl, True, True, 0)
            
        _add_header_col("Event", self.sg_event)
        _add_header_col("Controllable", self.sg_ctrl)
        _add_header_col("Input/Output", self.sg_io)
        for col_key, col_config in self.columns.items():
            _add_header_col(col_config['label'], self.sg_cols[col_key])
            
        lbl_action = Gtk.Label(label="Action", xalign=0.5)
        self.sg_action.add_widget(lbl_action)
        header.pack_start(lbl_action, False, False, 0)
        
        self.rows_box.pack_start(header, False, False, 0)

    def trigger_change(self):
        if self.on_change_callback:
            self.on_change_callback()

    def on_add_row(self, widget):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        row_widgets = {}

        # cria a caixa de selecao de event
        ev_combo = Gtk.ComboBoxText()
        ev_combo.append_text("Select Event")
        for ev in self.events:
            ev_combo.append_text(ev.name)
        ev_combo.set_active(0)
        self.sg_event.add_widget(ev_combo)
        row_box.pack_start(ev_combo, True, True, 0)
        row_widgets['event'] = ev_combo

        # controllabel
        ctrl_label = Gtk.Label(label="-")
        self.sg_ctrl.add_widget(ctrl_label)
        row_box.pack_start(ctrl_label, True, True, 0)
        row_widgets['is_controllable_label'] = ctrl_label

        #  Input/Output
        ctrl_combo = Gtk.ComboBoxText()
        ctrl_combo.append_text("Select I/O")
        ctrl_combo.append_text("Output")  # controllable = True
        ctrl_combo.append_text("Input")   # controllable = False
        ctrl_combo.set_active(0)
        self.sg_io.add_widget(ctrl_combo)
        row_box.pack_start(ctrl_combo, True, True, 0)
        row_widgets['controllable'] = ctrl_combo

      
        for col_key, col_config in self.columns.items():
            if col_config['widget_type'] == 'choice':
                combo = Gtk.ComboBoxText()
                for opt_label, opt_val in col_config['options']:
                    combo.append_text(opt_label)
                combo.set_active(0)
                combo.connect('changed', lambda w: self.trigger_change())
                self.sg_cols[col_key].add_widget(combo)
                row_box.pack_start(combo, True, True, 0)
                row_widgets[col_key] = combo

            elif col_config['widget_type'] == 'dynamic_choice':
                combo = Gtk.ComboBoxText()
                combo.append_text("Select Type")
                combo.set_active(0)
                combo.connect('changed', lambda w: self.trigger_change())
                self.sg_cols[col_key].add_widget(combo)
                row_box.pack_start(combo, True, True, 0)
                row_widgets[col_key] = combo

            elif col_config['widget_type'] == 'text':
                entry = Gtk.Entry(text=col_config.get('default', ''))
                entry.connect('changed', lambda w: self.trigger_change())
                self.sg_cols[col_key].add_widget(entry)
                row_box.pack_start(entry, True, True, 0)
                row_widgets[col_key] = entry


        def update_dynamic_options():
            for c_key, c_config in self.columns.items():
                if c_config['widget_type'] == 'dynamic_choice':
                    dyn_combo = row_widgets[c_key]
                    dyn_combo.remove_all() 
                    
                    ctrl_idx = ctrl_combo.get_active()
                    if ctrl_idx == 1:  # Output
                        opts = c_config.get('options_yes', [])
                    elif ctrl_idx == 2:  # Input
                        opts = c_config.get('options_no', [])
                    else:
                        opts = [("Select Type", None)]
                        
                    for opt_label, opt_val in opts:
                        dyn_combo.append_text(opt_label)
                    dyn_combo.set_active(0)

        def on_ev_changed(combo):
            idx = combo.get_active()
            
            if idx > 0:
                ev = self.events[idx - 1]
                is_controllable = ev.controllable
                ctrl_label.set_text("YES" if is_controllable else "NO")
                ctrl_combo.set_active(1 if is_controllable else 2)
            else:
                ctrl_label.set_text("-")
                ctrl_combo.set_active(0)

            update_dynamic_options()
            self.trigger_change()

  
        def on_ctrl_changed(combo):
            update_dynamic_options()
            self.trigger_change()


        ev_combo.connect('changed', on_ev_changed)
        ctrl_combo.connect('changed', on_ctrl_changed)

        btn_del = Gtk.Button(label="Delete")
        btn_del.connect('clicked', self.on_delete_row, row_box, row_widgets)
        self.sg_action.add_widget(btn_del)
        row_box.pack_start(btn_del, False, False, 0)

        self.rows_box.pack_start(row_box, False, False, 0)
        self.rows.append(row_widgets)
        self.show_all()
        self.trigger_change()

    def on_delete_row(self, btn, row_box, row_widgets):
        self.rows_box.remove(row_box)
        self.rows.remove(row_widgets)
        self.trigger_change()

    def get_data(self):
        mapped_controllable = {}
        for row in self.rows:
            ev_idx = row['event'].get_active()
            if ev_idx > 0:
                event = self.events[ev_idx - 1]
                ctrl_idx = row['controllable'].get_active()
                if ctrl_idx == 2:  # Input
                    mapped_controllable[event] = False
                elif ctrl_idx == 1 and mapped_controllable.get(event) is not False:  # Output
                    mapped_controllable[event] = True

        for event, is_controllable in mapped_controllable.items():
            event.controllable = is_controllable

        data = []
        for row in self.rows:
            ev_idx = row['event'].get_active()
            if ev_idx <= 0:  
                continue
            
            row_data = {}
            event = self.events[ev_idx - 1]
            row_data['event'] = event.name
            
            ctrl_idx = row['controllable'].get_active()
            row_data['is_output'] = (ctrl_idx == 1)
            
            
            for col_key, col_config in self.columns.items():
                widget = row[col_key]
                if col_config['widget_type'] == 'choice':
                    idx = widget.get_active()
                    row_data[col_key] = col_config['options'][idx][1] if idx >= 0 else None
                elif col_config['widget_type'] == 'dynamic_choice':
                    idx = widget.get_active()
                    if ctrl_idx == 1:  # Output
                        opts = col_config.get('options_yes', [])
                    elif ctrl_idx == 2:  # Input
                        opts = col_config.get('options_no', [])
                    else:
                        opts = [("Select Type", None)]
                    
                    if idx >= 0 and idx < len(opts):
                        row_data[col_key] = opts[idx][1]
                    else:
                        row_data[col_key] = None
                elif col_config['widget_type'] == 'text':
                    row_data[col_key] = widget.get_text()
            data.append(row_data)
        return data

    def on_save_clicked(self, widget):
        try:
            dialog = Gtk.FileChooserDialog(
                title="Save Configuration",
                parent=None,
                action=Gtk.FileChooserAction.SAVE
            )
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
            dialog.set_current_name("table_config.json")
            
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                filepath = dialog.get_filename()
                data = self.get_data()
                with open(filepath, 'w') as f:
                    import json
                    json.dump(data, f, indent=4)
            dialog.destroy()
        except Exception as e:
            print(f"Exception in on_save_clicked: {e}")

    def on_import_clicked(self, widget):
        try:
            dialog = Gtk.FileChooserDialog(
                title="Import Configuration",
                parent=None,
                action=Gtk.FileChooserAction.OPEN
            )
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            
            filter_json = Gtk.FileFilter()
            filter_json.set_name("JSON files")
            filter_json.add_pattern("*.json")
            dialog.add_filter(filter_json)
            
            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            dialog.add_filter(filter_any)

            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                filepath = dialog.get_filename()
                import json
                with open(filepath, 'r') as f:
                    data = json.load(f)
                self.load_data(data)
            dialog.destroy()
        except Exception as e:
            print(f"Exception in on_import_clicked: {e}")

    def load_data(self, data):
        try:
            children = self.rows_box.get_children()
            for child in children[1:]:
                self.rows_box.remove(child)
            self.rows.clear()
            
            # Add new rows
            for row_data in data:
                self.on_add_row(None)
                row_widgets = self.rows[-1]
                
                ev_name = row_data.get('event')
                ev_idx = 0
                for i, ev in enumerate(self.events):
                    if ev.name == ev_name:
                        ev_idx = i + 1
                        row_widgets['is_controllable_label'].set_text("YES" if ev.controllable else "NO")
                        break
                row_widgets['event'].set_active(ev_idx)
                
                if 'is_output' in row_data:
                    row_widgets['controllable'].set_active(1 if row_data['is_output'] else 2)
                    
                for col_key, col_config in self.columns.items():
                    if col_key in row_data:
                        val = row_data[col_key]
                        widget = row_widgets[col_key]
                        
                        if col_config['widget_type'] in ('choice', 'dynamic_choice'):
                            if col_config['widget_type'] == 'choice':
                                opts = col_config['options']
                            else:
                                ctrl_idx = row_widgets['controllable'].get_active()
                                if ctrl_idx == 1:
                                    opts = col_config.get('options_yes', [])
                                elif ctrl_idx == 2:
                                    opts = col_config.get('options_no', [])
                                else:
                                    opts = [("Select Type", None)]
                                    
                            idx = 0
                            for i, (opt_label, opt_val) in enumerate(opts):
                                if opt_val == val:
                                    idx = i
                                    break
                            widget.set_active(idx)
                        elif col_config['widget_type'] == 'text':
                            widget.set_text(str(val) if val is not None else "")
            self.trigger_change()
        except Exception as e:
            print(f"Exception in load_data: {e}")
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
