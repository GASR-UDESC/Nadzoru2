import sys
import gi
from gi.repository import GLib, Gio, Gtk


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.tab = letk.List.new()
        self.window     = Gtk.Window(Gtk.WindowType.TOPLEVEL, title="Nadzoru")
        self.vbox       = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.menubar    = Gtk.MenuBar()
        self.note       = Gtk.Notebook()
        self.statusbar  = Gtk.Statusbar()

        self.actions   = {}

        # Menu
        self.menu      = {}
        self.menu_item = {}

        self.append_menu('file', "_File")
        self.append_menu_item('file', "_Close Tab", "Close The Active Tab", 'gtk-delete', self.remove_current_tab, self )
        self.append_menu_separator('file')
        self.append_menu_item('file', "_Quit nadzoru", "Quit nadzoru", 'gtk-quit', Gtk.main_quit, self )
        
        
        self.dialogCurrentFolder = None 

        self.vbox.pack_start(self.menubar, False, False, 0)
        self.vbox.pack_start(self.note   , True, True, 0)
        self.window.add(self.vbox)

        self.window.set_default_size(1000, 800)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete-event", Gtk.main_quit)
        
        self.note.popup_enable()
        self.note.set_scrollable(True)
        self.note.set_show_border(True)

        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(Gtk.Label(label="Default Page!"))
        self.note.append_page(self.page1, Gtk.Label(label="Current tab"))

        self.window.show_all()


    def gui(self):
         self.window.show_all()


    def append_menu(self, name, caption):
        self.menu[name] = Gtk.Menu()
        menu_item = Gtk.MenuItem.new_with_mnemonic( caption )
        menu_item.set_submenu( self.menu[name] )
        self.menubar.append( menu_item )
        self.window.show_all()

        self.menu_item[name] = {}

        return menu_item

    
    def prepend_menu(self, name, caption):
        self.menu[name] = Gtk.Menu.new()
        menu_item = Gtk.MenuItem.new_with_mnemonic( caption )
        menu_item.set_submenu( self.menu[name] )
        self.menubar.prepend( menu_item )
        self.window.show_all()

        self.menu_item[name] = {}

        return menu_item
    

    def append_sub_menu( self, parent, name, caption ):
        self.menu[name] = Gtk.Menu.new()
        menu_item = Gtk.MenuItem.new_with_mnemonic( caption )
        menu_item.set_submenu( self.menu[name] )
        self.menu[parent].append( menu_item )
        self.window.show_all()

        self.menu_item[name] = {}

        return menu_item

    
    def prepend_sub_menu( self, parent, name, caption ):
        self.menu[name] = Gtk.Menu.new()
        menu_item = Gtk.MenuItem.new_with_mnemonic( caption )
        menu_item.set_submenu( self.menu[name] )
        self.menu[parent].prepend( menu_item )
        self.window.show_all()

        self.menu_item[name] = {}

        return menu_item


    def append_menu_separator( self, name ):
        separator = Gtk.SeparatorMenuItem.new()
        self.menu[name].append( separator )


    def prepend_menu_separator( self, name ):
        separator = Gtk.SeparatorMenuItem.new()
        self.menu[name].prepend( separator )

    
    def remove_menu( self, name ):
            self.menubar.remove( name )
            self.menu_item[name] = None

            
    def getImage( self, name ):
        try:
            f = open( name, 'r' )
            return Gtk.Image.new_from_file( name )
        except:   
            return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)


    def append_menu_item( self, menu_name, caption, hint, icon, callback, param,  ):
        menu_item = None
        if icon:
            box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            image = self.getImage( icon )
            label = Gtk.Label()
            label.set_markup_with_mnemonic( caption )
            label.set_justify( Gtk.Justification.LEFT )
            box.pack_start( image, False, False, 0 )
            box.pack_start( label, False, False, 5 )
            menu_item   = Gtk.MenuItem.new()
            menu_item.add( box )
        else:
            menu_item = Gtk.MenuItem.new_with_mnemonic( caption )
            menu_item.connect('activate', callback, param )

        self.window.show_all()

        if self.menu[menu_name]:
            self.menu[menu_name].append( menu_item )
            self.menu_item[menu_name][ len(self.menu_item[menu_name]) + 1] = menu_item
            self.window.show_all()
        
        # Variadic, *args or **kwargs
        # if args:
        #     return menu_item, self.append_menu_item( menu_name, args )
        
        return menu_item


    def prepend_menu_item( self, menu_name, caption, hint, icon, callback, param ):
        menu_item = None
        if icon:
            box = Gtk.Box()
            image = self.getImage( icon )
            label = Gtk.Label.new()
            label.set_markup_with_mnemonic( caption )
            label.set_justify( Gtk.JUSTIFY_LEFT )
            box.pack_start( image, False, False, 0 )
            box.pack_start( label, False, False, 5 )
            menu_item   = Gtk.MenuItem.new()
            menu_item.add( box )
        else:
            menu_item = Gtk.MenuItem.new_with_mnemonic( caption )
            menu_item.connect('activate', callback, param )
    

        if self.menu[menu_name]:
            self.menu[menu_name].prepend( menu_item )
            self.menu_item[menu_name][ len(self.menu_item[menu_name]) + 1] = menu_item
            self.window.show_all()
        
        # Variadic
        # if args:
        #     return menu_item, self.append_menu_item( menu_name, args )
        
        return menu_item


    def remove_menu_item(self, menu_name, menu_item ):
        self.menu[menu_name].remove( menu_item )
        pos = None
        for ch, val in enumerate( self.menu_item[menu_name] ):
            if val == menu_item:
                pos = ch
    
        if pos:
            last = self.menu_item[menu_name]
            self.menu_item[menu_name][pos] = None
            self.menu_item[menu_name][pos] = self.menu_item[menu_name][last]


    def add_tab( self, widget, title, destroy_callback, param ):
        note =  self.note.insert_page( widget, Gtk.Label.new(title), -1)
        # self.tab.add({ destroy_callback = destroy_callback, param = param, widget = widget }, note + 1)
        self.window.show_all()
        self.note.set_current_page(note)

        return note

    
    def remove_current_tab(self, *args):
        id = self.note.get_current_page()
        print(id)
        self.remove_tab(id)

    def remove_tab(self, id ):
        if id:
            self.note.remove_page( id )
            destroy = self.tab.remove( id + 1 )
            if destroy and destroy.destroy_callback:
                destroy.destroy_callback( destroy.param )
        
        self.window.show_all()    


    def set_tab_page_title( self, widget, title ):
        page_label = self.note.get_tab_label( widget )
        page_label.set_text( title )

        self.window.show_all()

        # This will be in the windows group and have the "win" prefix
        max_action = Gio.SimpleAction.new_stateful("maximize", None, GLib.Variant.new_boolean(False))
        max_action.connect("change-state", self.on_maximize_toggle)
        self.add_action(max_action)

        # Keep it in sync with the actual state
        self.connect("notify::is-maximized",
            lambda obj, pspec: max_action.set_state(
                GLib.Variant.new_boolean(obj.props.is_maximized)
            ),
        )

    def on_maximize_toggle(self, action, value):
        action.set_state(value)
        if value.get_boolean():
            self.maximize()
        else:
            self.unmaximize()
    
        
class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.nadzoru2.application",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None,)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application, when the last one is closed the application shuts down
            self.window = MainWindow(application=self, title="Nadzoru 2")

        self.window.present()
        

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()  # convert GVariantDict -> GVariant -> dict

        if "test" in options:
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0

    def on_quit(self, action, param):
        self.quit()