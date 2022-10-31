from gi.repository import Gtk
from datetime import datetime

class StatusBar(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, *args, **kwargs)
        self.set_size_request(-1, 100)
        self.set_property('margin', 10)
        # box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # self.add(box)
        self.listbox = Gtk.ListBox()    # orientation=Gtk.Orientation.HORIZONTAL)
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.listbox)
        self.listbox.connect('size-allocate', self.listbox_changed, scrolled)
        header = self.build_header()
        header.set_margin_bottom(5)
        self.pack_start(header, False, False, 0)
        self.pack_start(scrolled, True, True, 0)

    # def _add_row(self, widget):
    #     row = Gtk.ListBoxRow()
    #     hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    #     row.add(hbox)
    #     self.listbox.add(row)
    #     hbox.pack_start(widget, True, True, 5)

    def build_header(self):

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        label = Gtk.Label(label="Messages", xalign=0)
        button = Gtk.Button(label="Clear")
        button.connect('clicked', self.on_clear_clicked)
        # button.set_relief(Gtk.ReliefStyle.NONE)
        hbox.pack_start(label, True, True, 10)
        hbox.pack_start(button, False, False, 10)

        return hbox

    def listbox_changed(self, widget, allocation, scrolled):
        adj = scrolled.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def push(self, text):
        time_str = datetime.now().strftime('%H:%M:%S')
        text = f'{time_str}\t {text}'
        label = Gtk.Label(label=text, xalign=0)
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row.add(hbox)
        self.listbox.add(row)
        hbox.pack_start(label, True, True, 5)
        self.show_all()

    def clear(self):
        for row in self.listbox:
            row.destroy()

    def on_clear_clicked(self, widget):
        self.clear()