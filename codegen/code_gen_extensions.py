from codegen.code_gen import ArduinoGenerator

class ArduinoGeneratorPublic(ArduinoGenerator):
    templates_name = ['arduino_public.ino', 'generic_mic.h']

    def add_extra_properties(self, events):
        str_public = ['1' if event.public else '0' for event in events]
        ev_public = self._gen_str(str_public)
        return {'ev_public': ev_public}
