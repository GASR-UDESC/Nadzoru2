import sys
import gi
import os
import logging
from gi.repository import Gdk, Gio, Gtk

from machine.automaton import Automaton
from gui.automaton_editor import AutomatonEditor
from gui.automaton_simulator import AutomatonSimulator
from gui.automaton_manager import AutomatonManager
from gui.automaton_generator import AutomatonGenerator
from gui.statusbar import StatusBar
from gui.tool_palette import ToolPalette
from gui.automaton_operation import AutomatonOperation
from gui.operation_designer import OperationDesigner
from gui.automaton_script_operation import AutomatonScriptOperation
from gui.automaton_multiple_simulator import AutomatonSimulatorController


from machine.automaton_extensions import AutomatonPublic, AutomatonProbabilistic
from gui.automaton_editor_extensions import AutomatonEditorPublic, AutomatonEditorProbabilistic
from gui.parse_argument import Extension

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Select extension to use
        if Extension.mode == 'prob':      # probabilistic events
            self.automaton_class = AutomatonProbabilistic
            self.automaton_editor_class = AutomatonEditorProbabilistic
        elif Extension.mode == 'public':  # public events
            self.automaton_class = AutomatonPublic
            self.automaton_editor_class = AutomatonEditorPublic
        elif Extension.mode == 'probpub': # probabilistic and public events
            pass # 'TODO'
        else:   # no extension
            self.automaton_class = Automaton
            self.automaton_editor_class = AutomatonEditor

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.expander = Gtk.Expander(expanded=True)
        self.statusbar_expander = Gtk.Expander(expanded=True)
        self.toolpallet = ToolPalette(width_request=148, vexpand=True)
        self.note = Gtk.Notebook(group_name='0', scrollable=True)

        self.statusbar = StatusBar()
        self.statusbar_expander.add(self.statusbar)
        self.dialogCurrentFolder = None

        self.vbox.pack_start(self.hbox, True, True, 0)
        self.hbox.pack_start(self.expander, False, False, 0)
        self.expander.add(self.toolpallet)
        self.hbox.pack_start(self.note, True, True, 0)
        self.vbox.pack_start(self.statusbar_expander, False, False, 0)
        self.add(self.vbox)

        self.set_default_size(1000, 800)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.note.popup_disable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)
        
        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_path('gui/style.css') # inicializando cor

        self.note.connect('create-window', self.on_notebook_create_window)
        self.note.connect('page-removed', self.on_notebook_page_removed)
        self.toolpallet.connect('nadzoru-tool-change', self.on_tool_change)


        self._create_action('new-automaton', self.on_new_automaton)
        self._create_action('open-automaton', self.on_open_automaton)
        self._create_action('save-automaton', self.on_save_automaton)
        self._create_action('save-as-automaton', self.on_save_as_automaton)

        self._create_action('import-ides', self.on_import_ides)
        self._create_action('export-ides', self.on_export_ides)
        self._create_action('import-nadzoru', self.on_import_nadzoru)

        self._create_action('edit-automaton', self.on_edit_automaton)
        self._create_action('simulate-automaton', self.on_simulate_automaton)
        self._create_action('operation-automaton', self.on_operation)
        self._create_action('script-operation-automaton', self.on_script_operation)
        self._create_action('simulate-multiple-automata', self.on_simulate_multiple_automata)
        self._create_action('generate-code-automaton', self.on_generate_code)

        self._create_action('close-tab', self.on_close_tab)

        self.toolpallet.add_button('file', label="Save", icon_name='gtk-save', callback=self.on_save_automaton)
        self.toolpallet.add_button('file', label="Save", icon_name='gtk-save-as', callback=self.on_save_as_automaton)
        self.toolpallet.add_button('file', label="Open", icon_name='gtk-open', callback=self.on_open_automaton)

    def _create_action(self, action_name, callback, *args):
        action = Gio.SimpleAction.new(action_name, None)
        if not args:
            action.connect("activate", callback)
            self.add_action(action)
        else:
            action.connect("activate", callback, args)
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
        ''' Checks if automaton is already open in another tab/window.
            creates a new editor instance if it isn't or focus the tab if it is
        '''
        already_open_in = self.get_application().is_automaton_open(automaton, self.automaton_editor_class)
        if already_open_in is None:
            editor = self.automaton_editor_class(automaton)
            editor.connect('nadzoru-editor-change', self.props.application.on_editor_change)
            self.add_tab(editor, label)
        else:
            tab_id, window = already_open_in
            window.note.set_current_page(tab_id)
            window.present()

    def add_tab_operationdesigner(self):
        operation_designer = OperationDesigner()
        self.add_tab(operation_designer, 'Operation Designer')

    def add_tab_simulator(self, automaton, label):
        simulator = AutomatonSimulator(automaton)
        self.add_tab(simulator, label) # Probably OK to have more than 1 simulator instance

    def get_current_tab_widget(self):
        _id = self.note.get_current_page()
        return self.note.get_nth_page(_id)

    def get_tabs_list(self):
        tabs_list = list()
        for tab_id in range(self.note.get_n_pages()):
            tabs_list.append((tab_id, self.note.get_nth_page(tab_id)))
        return tabs_list

    def set_tab_page_title(self, widget, title):
        label = self.note.get_tab_label(widget)
        label.set_text(title)
        self.show_all()

    def add_default_css_provider(self, widget, color):
        
        context = widget.get_style_context()
        context.add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        for style_cls in context.list_classes():
            context.remove_class(style_cls)    
        context.add_class(color)

    def set_tab_label_color(self, widget, color = 'label-black'):
        
        label = self.note.get_tab_label(widget)
        self.add_default_css_provider(label, color)
        
    
        
    #   rgba = Gdk.RGBA(0, 0, 0)
    #   rgba.parse(color)
    #   label.override_color(Gtk.StateFlags.NORMAL, rgba)

    #   self.show_all()

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
            if type(widget) == self.automaton_editor_class:
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
        self.statusbar.push("creating new automaton")
        logging.debug("")
        automaton = self.automaton_class()
        self.get_application().add_to_automatonlist(automaton)
        self.add_tab_editor(automaton, 'Untitled')

    def _add_filefilter(self, name, pattern):
            filefilter = Gtk.FileFilter()
            filefilter.set_name(name)
            filefilter.add_pattern(pattern)
            return filefilter

    def on_open_automaton(self, action, param=None):
        logging.debug("")
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Edit", Gtk.ResponseType.ACCEPT, "_Open", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        dialog.add_filter(self._add_filefilter(".xml files", '*.xml'))
        dialog.add_filter(self._add_filefilter("All files", '*'))
        result = dialog.run()

        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for file_path_name in dialog.get_filenames():
                file_name = os.path.basename(file_path_name)
                automaton = self.automaton_class()
                try:
                    automaton.load(file_path_name)
                except ValueError as e:
                    self.statusbar.push(str(e))  
                    continue  
                except Exception as e:
                    self.statusbar.push(f"Error loading: {e}")
                    continue

                self.get_application().add_to_automatonlist(automaton)
                if result == Gtk.ResponseType.ACCEPT:
                    self.add_tab_editor(automaton, automaton.get_file_name())
                self.statusbar.push(f"Loaded automaton: {file_name}")
        dialog.destroy()

    def _save_dialog(self, widget):
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.SAVE,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Save", Gtk.ResponseType.OK), do_overwrite_confirmation=True)

        dialog.add_filter(self._add_filefilter(".xml files", '*.xml'))
        dialog.add_filter(self._add_filefilter("All files", '*'))
        suggested_name = widget.automaton.get_name()
        if not suggested_name.endswith('.xml'):
            suggested_name = f'{suggested_name}.xml'
        dialog.set_current_name(suggested_name)
        result = dialog.run()

        if result ==  Gtk.ResponseType.OK:
            file_path = (dialog.get_filename())
            dialog.destroy()
            #~ if not(file_path.lower().endswith('.xml')):
                #~ file_path = f'{file_path}.xml'
            return widget.save(file_path)
        dialog.destroy()
        return False

    def on_save_automaton(self, action, param=None):
        logging.debug("")
        widget = self.get_current_tab_widget()
        if (widget is None):
            return

        if isinstance(widget, self.automaton_editor_class):
            automata = widget.automaton
            file_path_name = automata.get_file_path_name()
            if file_path_name == None:
                self._save_dialog(widget)
                self.set_tab_page_title(widget, automata.get_file_name())
            else:
                widget.save(file_path_name)
            self.set_tab_label_color(widget, 'label-black')

        elif isinstance(widget, AutomatonManager):
            widget.on_savebtn(None)
        else:
            return

    def on_save_as_automaton(self, action, param=None):
        logging.debug("")
        widget = self.get_current_tab_widget()
        if (widget is None) or type(widget) != self.automaton_editor_class:
            return
        automata = widget.automaton
        self._save_dialog(widget)
        self.set_tab_page_title(widget, automata.get_file_name())
        self.set_tab_label_color(widget, 'label-black')

    def on_import_ides(self, action, param):
        logging.debug("")
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for full_path_name in dialog.get_filenames():
                file_name = os.path.basename(full_path_name)
                automaton = self.automaton_class()
                automaton.ides_import(full_path_name)
                self.get_application().add_to_automatonlist(automaton)
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
            if type(widget) == self.automaton_editor_class:
                automata = widget.automaton
                automata.ides_export(file_path)
        dialog.destroy()

    def on_import_nadzoru(self, action, param):
        dialog = Gtk.FileChooserDialog("Choose file", self, Gtk.FileChooserAction.OPEN,
            ("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT, "_Edit", Gtk.ResponseType.OK))
        dialog.set_property('select-multiple', True)
        result = dialog.run()
        if result in [Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK]:
            for full_path_name in dialog.get_filenames():
                file_name = os.path.basename(full_path_name)
                automaton = self.automaton_class()
                automaton.legacy_nadzoru_import(full_path_name)
                self.get_application().add_to_automatonlist(automaton)
                if result == Gtk.ResponseType.OK:
                    # self.automaton.get_file_name(automaton,f'{file_name} *')
                    self.add_tab_editor(automaton, f'{file_name} *')
        dialog.destroy()


    def on_edit_automaton(self, action, param):
        logging.debug("")
        manager = AutomatonManager()
        self.add_tab(manager, "Manager")
        self.statusbar.push("Opened Automaton Manager")

    def on_simulate_automaton(self, action, param):
        manager = AutomatonManager()
        self.add_tab(manager, "Manager")
        self.statusbar.push("Opened Automaton Manager")

    def on_close_tab(self, action, param):
        logging.debug("")
        self.remove_current_tab()
        
    def on_operation(self,action, param):
        #app = self.get_application()
        operation = AutomatonOperation()
        self.add_tab(operation, "Operation")
        self.statusbar.push("Opened Operation tab")

    def on_script_operation(self,action, param):
        operation = AutomatonScriptOperation()
        self.add_tab(operation, "Script Operation")
        self.statusbar.push("Opened Script Operation tab")
    
    def on_simulate_multiple_automata(self,action, param):
        operation = AutomatonSimulatorController()
        self.add_tab(operation, "Simulate Automata")
        self.statusbar.push("Opened Simulation tab")
    
    
    def on_generate_code(self, action, param):
        generator = AutomatonGenerator()
        self.add_tab(generator, "Code Generator")
        self.statusbar.push("Opened Code Generator")
    
    def show_status_message(self, message):
        self.statusbar.push(message)
