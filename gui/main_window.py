import sys
import gi
import os
import logging
from gi.repository import Gdk, Gio, Gtk

from machine.automaton import Automaton
from gui.automaton_editor import AutomatonEditor
from gui.automaton_simulator import AutomatonSimulator
from gui.tool_palette import ToolPalette
from gui.automaton_operation import AutomatonOperation


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.expander = Gtk.Expander(expanded=True)
        self.toolpallet = ToolPalette(width_request=148, vexpand=True)
        self.note = Gtk.Notebook(group_name='0', scrollable=True)
        self.statusbar = Gtk.Statusbar()

        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.hbox, True, True, 0)
        self.hbox.pack_start(self.expander, False, False, 0)
        self.expander.add(self.toolpallet)
        self.hbox.pack_start(self.note, True, True, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.note.popup_disable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

        self.note.connect('create-window', self.on_notebook_create_window)
        self.note.connect('page-removed', self.on_notebook_page_removed)
        self.toolpallet.connect('nadzoru-tool-change', self.on_tool_change)

        self._create_action('new-automaton', self.on_new_automaton)
        self._create_action('open-automaton', self.on_open_automaton)
        self._create_action('save-automaton', self.on_save_automaton)
        self._create_action('save-as-automaton', self.on_save_as_automaton)
        self._create_action('operation-automaton', self.on_operation)

        self._create_action('import-ides', self.on_import_ides)
        self._create_action('export-ides', self.on_export_ides)

        self._create_action('edit-automaton', self.on_edit_automaton)
        self._create_action('simulate-automaton', self.on_simulate_automaton)

        self._create_action('close-tab', self.on_close_tab)

        self.toolpallet.add_button('file', label="Save", icon_name='gtk-save', callback=self.on_save_automaton)
        self.toolpallet.add_button('file', label="Save", icon_name='gtk-save-as', callback=self.on_save_as_automaton)
        self.toolpallet.add_button('file', label="Open", icon_name='gtk-open', callback=self.on_open_automaton)

    def _create_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)

    #~ def _get_image(self, name):
        #~ try:
            #~ f = open(name, 'r')
            #~ return Gtk.Image.new_from_file(name)
        #~ except:
            #~ return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)

    def add_tab(self, widget, title):
        note = self.note.insert_page(widget, Gtk.Label.new(title), -1)
        self.show_all()
        self.note.set_current_page(note)
        self.note.set_tab_detachable(widget, True)

        return note

    def remove_tab(self, _id):
        if _id < 0:
            return False

        self.note.set_current_page(_id)

        widget = self.note.get_nth_page(_id)
        if widget.has_changes_to_save():
            result = self._popup(widget.get_tab_name())
            if result == Gtk.ResponseType.CANCEL:
                return False
            elif result == Gtk.ResponseType.APPLY:  # save
                # if widget.has_file_path_name():
                if not widget.save():
                    if  not self._save_dialog(widget):
                        return False
        self.note.remove_page(_id)
        return True

    def remove_current_tab(self, *args):
        _id = self.note.get_current_page()
        self.remove_tab(_id)

    def remove_tabs(self):
        while self.note.get_n_pages() > 0:
            if self.remove_tab(0) == False:
                return False  # at least one tab canceled
        return True  # was able to close all tabs

    def add_tab_editor(self, automaton, label): 
        editor = AutomatonEditor(automaton)
        editor.connect('nadzoru-editor-change', self.props.application.on_editor_change)
        self.add_tab(editor, label)

    def get_current_tab_widget(self):
        _id = self.note.get_current_page()
        return self.note.get_nth_page(_id)

    def set_tab_page_title(self, widget, title):
        label = self.note.get_tab_label(widget)
        label.set_text(title)
        self.show_all()

    def set_tab_label_color(self, widget, color="#000000"):
        label = self.note.get_tab_label(widget)

        rgba = Gdk.RGBA(0, 0, 0)
        rgba.parse(color)
        label.override_color(Gtk.StateFlags.NORMAL, rgba)

        self.show_all()

    def do_delete_event(self, event):
        logging.debug("")
        if self.remove_tabs() == False:
            return True  # Cancel default handler (do NOT close window)
        else:
            return False  # Execute the default handler, on_notebook_page_removed will trigger self.destroy() but it doesn't seem to be a problem. Must return False to close a window without tabs


    def on_notebook_create_window(self,notebook,widget,x,y): #is widget a automaton Editor?? is  Notebook a page??
        # handler for dropping outside of notebook
        logging.debug("")
        new_window = self.props.application.add_window()

        new_window.move(x, y)
        new_window.show_all()
        new_window.present()
        return new_window.note

    def on_notebook_page_removed(self, notebook, child, page):
        logging.debug("")
        if notebook.get_n_pages() == 0:
            self.destroy()
        return True

    def on_tool_change(self, toolpallet, tool_id):
        logging.debug("")
        for page_num in range(self.note.get_n_pages()):
            widget = self.note.get_nth_page(page_num)
            if type(widget) == AutomatonEditor:
                widget.reset_selection()

    def _popup(self, tab_name):
        dialog = Gtk.Dialog("Nadzoru 2", self)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_DISCARD, Gtk.ResponseType.YES, Gtk.STOCK_SAVE, Gtk.ResponseType.APPLY)
        dialog.set_default_size(150, 100)

        label = Gtk.Label()
        label.set_text(f"{tab_name} is not saved")
        label.set_justify(Gtk.Justification.LEFT)

        box_dialog = dialog.get_content_area()
        box_dialog.add(label)
        box_dialog.show_all()

        result = dialog.run()
        dialog.destroy()

        return result

    def on_new_automaton(self, action, param=None):
        logging.debug("")
        automaton = Automaton()
        self.add_to_automatonlist(automaton)
        self.add_tab_editor(automaton, 'Untitled')

    def on_open_automaton(self, action, param=None):
        logging.debug("")
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Edit", Gtk.ResponseType.ACCEPT, "_Open", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for file_path_name in dialog.get_filenames():
                file_name = os.path.basename(file_path_name)
                automaton = Automaton()
                try:
                    automaton.load(file_path_name)
                except error:
                    print("Fail to load", error)
                    dialog.destroy()
                    return
                self.add_to_automatonlist(automaton)
                if result == Gtk.ResponseType.ACCEPT:
                    self.add_tab_editor(automaton, automaton.get_file_name())
                dialog.destroy()

           

    def _save_dialog(self, widget):
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK), do_overwrite_confirmation=True)
        result = dialog.run()
        if result ==  Gtk.ResponseType.OK:
            file_path = (dialog.get_filename())
            dialog.destroy()
            if not(file_path.lower().endswith('.xml')):
                file_path = f'{file_path}.xml'
            return widget.save(file_path)
        dialog.destroy()
        return False

    def on_save_automaton(self, action, param=None):
        logging.debug("")
        widget = self.get_current_tab_widget()
        if (widget is None) or type(widget) != AutomatonEditor:
            return
        automata = widget.automaton

        file_path_name = automata.get_file_path_name()
        if file_path_name == None:
            self._save_dialog(widget)
            self.set_tab_page_title(widget, automata.get_file_name())
        else:
            widget.save(file_path_name)
        self.set_tab_label_color(widget, '#000')

    def on_save_as_automaton(self, action, param=None):
        logging.debug("")
        widget = self.get_current_tab_widget()
        if (widget is None) or type(widget) != AutomatonEditor:
            return
        automata = widget.automaton
        self._save_dialog(widget)
        self.set_tab_page_title(widget, automata.get_file_name())
        self.set_tab_label_color(widget, '#000')

    def on_import_ides(self, action, param):
        logging.debug("")
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for full_path_name in dialog.get_filenames():
                file_name = os.path.basename(full_path_name)
                automaton = Automaton()
                automaton.ides_import(full_path_name)
                self.add_to_automatonlist(automaton)
                if result == Gtk.ResponseType.OK:
                    self.automaton.get_file_name(automaton,f'{file_name} *')
        dialog.destroy()

    def on_export_ides(self, action, param):
        logging.debug("")
        dialog = Gtk.FileChooserDialog("Choose File", self, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Export", Gtk.ResponseType.OK))
        result = dialog.run()
        if result == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            file_path = f'{file_path}.xmd'
            widget = self.get_current_tab_widget()
            if type(widget) == AutomatonEditor:
                automata = widget.automaton
                automata.ides_export(file_path)
        dialog.destroy()

    def on_edit_automaton(self, action, param):
        logging.debug("")

    def on_simulate_automaton(self, action, param):
        logging.debug("")
        # TODO: open dialog to select from self.props.application.elements
        from test_automata import automata_01  # For testing
        automaton = Automaton()
        automata_01(automaton)  # For testing
        simulator = AutomatonSimulator(automaton)
        self.add_tab(simulator, "Simulator")

    def on_close_tab(self, action, param):
        logging.debug("")
        self.remove_current_tab()

    def on_operation(self,action, param):
        operation = AutomatonOperation(self.props.application.elements)
        self.add_tab(operation,'Operation')

    def add_to_automatonlist(self, automaton):  # maybe should be moved to application?
        self.props.application.elements.append(automaton)
        self.update_menubar()

    def update_menubar(self): # For now, only adds the name of the automaton name in the edit submenu. It isn't linking to any action yet
        menubar = self.props.application.menubar
        menu = self._get_menu(menubar, 'Automata', submenu_text='Edit')
        if menu.get_n_items() > 1:
            menu.remove(1)      # maybe write a function to verify the correct position to remove
        if len(self.props.application.elements) > 0:
            edit_menu = Gio.Menu()
            section = Gio.MenuItem.new()
            section.set_section(edit_menu)
            
            for automaton in self.props.application.elements: # aut.get_name isn't working if the automaton doesn't have a name
                try:
                    name = automaton.get_name()
                except:
                    name = 'Untitled'
                menuitem = Gio.MenuItem.new(name)
                edit_menu.append_item(menuitem)
            
            menu.append_item(section)

    def _get_menu(self, menu, menu_text, submenu_text=None, action_name=None):  # this could be better by scanning all menuitems 
        n_items = menu.get_n_items()                                            # so it wouldn't be needed to specify a menu, eg: 'Automata'
        
        for item_n in range(n_items):
            item_att_iter = menu.iterate_item_attributes(item_n)
            item_link_iter = menu.iterate_item_links(item_n)
            _, _type, value = item_att_iter.get_next()
            _, _link, menumodel = item_link_iter.get_next()

            if _link == 'submenu':
                if value.get_string() == menu_text:
                    r_menu = self._get_menu(menumodel, menu_text, submenu_text, action_name)
                    if r_menu is not None:
                        return r_menu
                elif value.get_string() == submenu_text:
                    return menumodel

            elif _link == 'section':
                r_menu = self._get_menu(menumodel, menu_text, submenu_text, action_name)
                if r_menu is not None:
                    return r_menu
            elif _type == 'action' and value.get_string() == action_name:
                return menu
