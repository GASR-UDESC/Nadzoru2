import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, GObject

from gui.property_box import PropertyBox

class PropertyBoxProbabilistic(PropertyBox):
    def add_entry(self, label, value, data=None, callback=None, placeholder=None, event_name=None):
        widget = Gtk.Entry(text=str(value), xalign=1, width_chars=10, has_frame=False)
        widget.connect('activate', self.prop_edited, None, data, callback, None)
        if placeholder is not None:
            widget.set_placeholder_text(placeholder)
        if event_name is not None:
            widget.set_name(event_name)
        self._add_row(label, widget)
        return widget
    
    def emit_nadzoru_property_change(self, value, data, name=None):
        self.emit('nadzoru-property-change-with-event', value, data, name)
    
GObject.signal_new('nadzoru-property-change-with-event',
    PropertyBoxProbabilistic,
    GObject.SignalFlags.RUN_LAST,
    GObject.TYPE_PYOBJECT,
    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, ))