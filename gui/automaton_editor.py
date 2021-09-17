#~ import os
import sys
import gi
from gi.repository import GLib, Gio, Gtk

from renderer import AutomatonRenderer


class AutomatonEditor(Gtk.Box):
    def __init__(self, automaton, application, *args, **kwargs):
        if 'spacing' not in kwargs:
            kwargs['spacing'] = 2
        super().__init__(*args, **kwargs)

        self.automaton = automaton
        self.application = application
        self.selected_state = None

        self.paned = Gtk.Paned()
        self.scrolled = Gtk.ScrolledWindow.new()
        self.automaton_render = AutomatonRenderer(self.automaton)





        self.pack_start(self.paned, True, True, 0)
        self.paned.pack1(self.scrolled, True, True)
        self.scrolled.add(self.automaton_render)

        self.automaton_render.connect("draw", self.on_draw)
        self.automaton_render.connect("motion-notify-event", self.on_motion_notify)
        self.automaton_render.connect("button-press-event", self.on_button_press)



        # TreeView: checkboxes 

        self.liststore = Gtk.ListStore(str, bool, bool)
        self.liststore.append(["A", False, False])
        self.liststore.append(["B", False, False])
        self.liststore.append(["C", False, False])

        treeview = Gtk.TreeView(model=self.liststore)


        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)

        column_editabletext = Gtk.TreeViewColumn("A", renderer_editabletext, text=0)
        treeview.append_column(column_editabletext)

        renderer_editabletext.connect("edited", self.text_edited)

        # It would be nice to create a class for Toggle Buttons. For now, it works 
        
        # Toggle 1
        renderer_toggle_1 = Gtk.CellRendererToggle()
        renderer_toggle_1.connect("toggled", self.on_cell_toggled_1)
        column_toggle_1 = Gtk.TreeViewColumn("B", renderer_toggle_1, active=1)
        treeview.append_column(column_toggle_1)

        # Toggle 2
        renderer_toggle_2 = Gtk.CellRendererToggle()
        renderer_toggle_2.connect("toggled", self.on_cell_toggled_2)
        column_toggle_2 = Gtk.TreeViewColumn("C", renderer_toggle_2, active=2)
        treeview.append_column(column_toggle_2)

        self.add(treeview)

        self.grid = Gtk.Grid()
        self.add(self.grid)
		#Add and Delete Cell buttons
		
        self.add_button = Gtk.Button(label = 'Add Cell')
        self.add_button.connect("clicked", self.ativo)
        self.grid.attach(self.add_button, 0, 0, 2, 1)	
        
        self.delete_button = Gtk.Button(label = 'Delete Cell')
        self.grid.attach(self.delete_button, 0, 2, 2, 1)

    def text_edited(self, widget, path, text):
        self.liststore[path][0] = text
    def on_cell_toggled_1(self, widget, path):
        self.liststore[path][1] = not self.liststore[path][1]
    def on_cell_toggled_2(self, widget, path):
        self.liststore[path][2] = not self.liststore[path][2]
    def ativo(self, widget):
        self.liststore.append(["A", False, False])
        
	# unfinished. Lacking a way to determine which cells are to be removed
    
    def delete_cell(self, widget, path):
        pass

    def on_draw(self, automaton_render, cr):
        self.automaton_render.draw(cr)

    def on_motion_notify(self, automaton_render, event):
        pass

    def on_button_press(self, automaton_render, event):
        x, y = event.get_coords()
        tool_name = self.application.window.toolpallet.get_selected_tool()

        if tool_name == 'state_add':
            self.automaton.state_add(None, x=x, y=y)

        self.automaton_render.queue_draw()


