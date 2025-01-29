import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk

class DualListSelector(Gtk.Box):
    #~ def __init__(self, data:list[tuple[str, object]]=None,
    def __init__(self, data=None,
                 btn_spacing=5, sort=True, use_filter=True, scrollable=True, scroll_hmax=300, scroll_hmin=50,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scrollable = scrollable
        self.scroll_hmax = scroll_hmax
        self.scroll_hmin = scroll_hmin
        self.set_orientation(Gtk.Orientation.HORIZONTAL)


        self.available_liststore = Gtk.ListStore(str, object)
        self.selected_liststore = Gtk.ListStore(str, object)


        if sort:
            # Sort by the alphabetical order of the object label, index 0
            self.selected_liststore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
            self.available_liststore.set_sort_column_id(0, Gtk.SortType.ASCENDING)


        for item in data:
            self.available_liststore.append((item[0], item[1]))

        self._draw_layout(btn_spacing, use_filter, scrollable, scroll_hmax, scroll_hmin)

    #~ def reset_list(self, data:list[tuple[str, object]]):
    def reset_list(self, data):
        self.available_liststore.clear()
        self.selected_liststore.clear()
        for item in data:
            self.available_liststore.append((item[0], item[1]))

    #~ def add_new_available(self, label:str, obj:object, *args, **kwargs):
    def add_new_available(self, label, obj, *args, **kwargs):
        self.available_liststore.append((label, obj))

    #~ def add_new_selected(self, label:str, obj:object, *args, **kwargs):
    def add_new_selected(self, label, obj, *args, **kwargs):
        self.selected_liststore.append((label, obj))
        self.emit('selected-changed')

    def get_selected_objects(self):
        return [row[1] for row in self.selected_liststore]

    def get_available_objects(self):
        return [row[1] for row in self.available_liststore]

    def get_selected(self):
        return [(row[0], row[1]) for row in self.selected_liststore]

    def get_available(self):
        return [(row[0], row[1]) for row in self.available_liststore]


    def _draw_layout(self, btn_spacing, use_filter, scrollable, scroll_hmax, scroll_hmin):

        def _create_button(label, callback, *args, **kwargs):
            button = Gtk.Button(label=label)
            button.connect("clicked", callback, *args, **kwargs)
            btn_box.pack_start(button, False, False, 0)
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_name("dual-list-selector-button")

            css_provider = Gtk.CssProvider()
            css_provider.load_from_path("./gui/style.css")
            screen = Gdk.Screen.get_default()
            Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


            return button

        def _create_treeview(liststore, column_label):
            treeview = Gtk.TreeView(model=liststore)
            treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_label, cell, text=0)
            treeview.append_column(column)
            treeview.set_enable_search(True)
            return treeview

        def _add_filter_to_treeview(tv_box, treeview):
            tv_and_filter_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            filter_entry = Gtk.Entry()
            label = Gtk.Label.new(treeview.get_column(0).get_title())

            tv_and_filter_box.pack_start(label, False, False, 0)
            tv_and_filter_box.pack_start(filter_entry, False, False, 0)
            tv_and_filter_box.pack_start(tv_box, True, True, 0)


            treeview.set_headers_visible(False)

            label.set_xalign(0)
            label.set_margin_start(10)

            filter = treeview.get_model().filter_new()
            filter.set_visible_func(self._filter_tree, filter_entry)

            filter_entry.set_placeholder_text("Enter text to filter")
            filter_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
            filter_entry.connect("changed", self._on_filter_entry_text_changed, filter)
            filter_entry.connect("icon-release", lambda entry, icon_pos, event: filter_entry.set_text(""))

            treeview.set_model(filter)

            return tv_and_filter_box

        self.available_treeview = _create_treeview(self.available_liststore, "Available")
        self.selected_treeview = _create_treeview(self.selected_liststore, "Selected")



        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        available_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        selected_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)


        if scrollable:
            def _add_scroll(treeview, scroll_hmax, scroll_hmin):
                scrolled = Gtk.ScrolledWindow(max_content_height=scroll_hmax, min_content_height=scroll_hmin, max_content_width=10)
                # scrolled = Gtk.ScrolledWindow()
                scrolled.add(treeview)
                scrolled.set_propagate_natural_height(True)
                scrolled.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
                return scrolled

            av_scroll = _add_scroll(self.available_treeview, scroll_hmax, scroll_hmin)
            sel_scroll = _add_scroll(self.selected_treeview, scroll_hmax, scroll_hmin)
            available_box.pack_start(av_scroll, True, True, 0)
            selected_box.pack_start(sel_scroll, True, True, 0)

            self.available_liststore.connect("row-inserted", self._on_row_changed, av_scroll)
            self.available_liststore.connect("row-deleted", self._on_row_changed, None, av_scroll)
            self.available_liststore.connect("row-changed", self._on_row_changed, av_scroll)
            self.selected_liststore.connect("row-inserted", self._on_row_changed, sel_scroll)
            self.selected_liststore.connect("row-deleted", self._on_row_changed, None, sel_scroll)
            self.selected_liststore.connect("row-changed", self._on_row_changed, av_scroll)
            self.scrolled_set_size_request(av_scroll)
            self.scrolled_set_size_request(sel_scroll)

        else:
            available_box.pack_start(self.available_treeview, True, True, 0)
            selected_box.pack_start(self.selected_treeview, True, True, 0)

        if use_filter:
            available_box = _add_filter_to_treeview(available_box, self.available_treeview)
            selected_box = _add_filter_to_treeview(selected_box, self.selected_treeview)
        else:
            available_box.pack_start(self.available_treeview, True, True, 0)
            selected_box.pack_start(self.selected_treeview, True, True, 0)

        self.pack_start(available_box, True, True, 0)
        self.pack_start(btn_box, False, False, btn_spacing)
        self.pack_start(selected_box, True, True, 0)

        _create_button(">", self._on_move_selection, self.available_treeview, self.available_liststore, self.selected_liststore)
        _create_button("<", self._on_move_selection, self.selected_treeview, self.selected_liststore, self.available_liststore)
        _create_button(">>", self._on_move_all, self.available_treeview, self.available_liststore, self.selected_liststore)
        _create_button("<<", self._on_move_all, self.selected_treeview, self.selected_liststore, self.available_liststore)

    def _copy_lists(self):
        selected = list()
        available = list()
        for item in self.selected_liststore:
            selected.append((item[0], item[1]))
        for item in self.available_liststore:
            available.append((item[0], item[1]))
        return selected, available

    def _update_lists(self, selected, available):
        for item in available:
            obj_label, obj = item[0], item[1]
            self.available_liststore.append((obj_label, obj))
        for item in selected:
            obj_label, obj = item[0], item[1]
            self.selected_liststore.append((obj_label, obj))

        self.emit('selected-changed')

    def autosize_columns(self):
        self.available_treeview.columns_autosize()
        self.selected_treeview.columns_autosize()

    def _on_move_selection(self, button, source_treeview, source_liststore, target_liststore):
        liststore, rows = source_treeview.get_selection().get_selected_rows()
        changes = list()
        for row in rows:
            data = (liststore[row][0], liststore[row][1])
            changes.append(data)

        for data in changes:
            for row in source_liststore:
                if (row[0], row[1]) == data:
                    source_liststore.remove(row.iter)
                    break
            target_liststore.append(data)
        self.autosize_columns()
        self.emit('selected-changed')

    def _on_move_all(self, button, source_treeview, source_liststore, target_liststore):
        rows_to_remove = list()
        for src_row in source_treeview.get_model():
            target_liststore.append([src_row[0], src_row[1]])
            for row in source_liststore:
                if (row[0], row[1]) == (src_row[0], src_row[1]):
                    rows_to_remove.append(row.iter)
                    break

        for _iter in rows_to_remove:
            source_liststore.remove(_iter)

        self.autosize_columns()
        self.emit('selected-changed')

    def _on_filter_entry_text_changed(self, entry, filter):
        # Since the filter text changed, tell the filter to re-determine which rows to display
        filter.refilter()

        if entry.get_text():
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "edit-clear-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)

    def _filter_tree(self, model, iter, filter_entry):
        label = model.get_value(iter, 0)

        if not filter_entry.get_text():
            return True

        return filter_entry.get_text().lower() in label.lower()

    def _on_row_changed(self, liststore, path, iter, widget, *args):
        self.scrolled_set_size_request(widget)

    def scrolled_set_size_request(self, scrolled):
        if not self.scrollable:
            return
        num_rows = max(len(self.available_liststore), len(self.selected_liststore))
        desired_height = num_rows * 25
        if desired_height > self.scroll_hmax:
            desired_height = self.scroll_hmax
        elif desired_height < self.scroll_hmin:
            desired_height = self.scroll_hmin
        scrolled.set_size_request(-1, desired_height)



GObject.signal_new('selected-changed',
    DualListSelector,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    ())
