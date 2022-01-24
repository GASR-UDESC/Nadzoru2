import gi
import logging
from gi.repository import GLib, Gio, Gtk, GObject

class PropertyBox(Gtk.ListBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def add_checkbutton(self, label, value, data=None, callback=None):
        pass

    def add_switch(self, label, value, data=None, callback=None):
        pass

    def add_entry(self, label, value, data=None, callback=None):
        widget = Gtk.Entry(text=str(value), xalign=1, width_chars=10, has_frame=False)
        widget.connect('activate', self.prop_edited, None, data, callback)
        self._add_row(label, widget)

    def add_spinbutton(self, label, value, data=None, callback=None, lower=0, upper=1000, step_increment=1, page_increment=100, width_chars=4):
        adjustment = Gtk.Adjustment(value=value, lower=lower, upper=upper, step_increment=step_increment, page_increment=page_increment)
        widget = Gtk.SpinButton(adjustment=adjustment, width_chars=width_chars)
        widget.connect('value-changed', self.prop_edited, None, data, callback)
        self._add_row(label, widget)

    def prop_edited(self, widget, gparam, data, callback):
        if type(widget) == Gtk.CheckButton:
            value = widget.get_active()
        elif type(widget) == Gtk.Switch:
            value = widget.get_active()
        elif type(widget) == Gtk.Entry:
            value = widget.get_text()
        elif type(widget) == Gtk.SpinButton:
            value = widget.get_value_as_int()
        else:
            value = None

        self.emit('nadzoru-property-change', value, data)
        if callback is not None:
            callback(value, data)


GObject.signal_new('nadzoru-property-change',
    PropertyBox,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,))

#~ if __name__ == '__main__':
    #~ gi.require_version("Gtk", "3.0")  # TEST
    #~ def cbk(prop, *args, **kwargs):
        #~ print(args)
        #~ print(kwargs)

    #~ win = Gtk.Window()
    #~ box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
    #~ prop = PropertyBox()
    #~ prop.add_entry("Valor de X", 100, 'x')
    #~ prop.add_entry("Valor de y", 200, 'y')
    #~ prop.add_spinbutton("Valor do fator", 1, 'fator')
    #~ prop.connect('nadzoru-property-change', cbk)

    #~ def rebuild(*args, **kwargs):
        #~ prop.clear()
        #~ prop.add_entry("Valor de X2", 100, 'x')
        #~ prop.add_entry("Valor de y2", 200, 'y')
        #~ prop.add_spinbutton("Valor do fatorx", 1, 'fator')
        #~ prop.show_all()

    #~ btn = Gtk.Button(label = "Rebuild props")
    #~ btn.connect('clicked', rebuild)

    #~ box.pack_start(prop, True, True, 0)
    #~ box.pack_start(btn, True, True, 0)

    #~ win.add(box)

    #~ win.show_all()
    #~ Gtk.main()
