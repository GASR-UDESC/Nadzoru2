from codegen.code_gen import BaseGenerator, ArduinoGenerator, CGenerator, CPPGenerator, KilobotGenerator, PythonGenerator

##### Public events extension #####

class BaseGeneratorPublic(BaseGenerator):

    def add_extra_properties(self, events):
        str_public = ['1' if event.public else '0' for event in events]
        ev_public = self._gen_str(str_public)
        return {'ev_public': ev_public}

class ArduinoGeneratorPublic(BaseGeneratorPublic, ArduinoGenerator):
    templates_name = ['arduino_public.ino', 'generic_mic.h']

class CGeneratorPublic(BaseGeneratorPublic, CGenerator):
    templates_name = ['generic_mic_public.h', 'generic_mic_public.c']

class CPPGeneratorPublic(BaseGeneratorPublic, CPPGenerator):
    templates_name = ['supervisor_public.yaml', 'sct.cpp', 'sct.h']

class KilobotGeneratorPublic(BaseGeneratorPublic, KilobotGenerator):
    templates_name = ['kilobotAtmega328_public.c']

class PythonGeneratorPublic(BaseGeneratorPublic, PythonGenerator):
    templates_name = ['supervisor_public.yaml', 'sct.py']
