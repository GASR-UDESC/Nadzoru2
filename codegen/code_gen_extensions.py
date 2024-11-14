from codegen.code_gen import BaseGenerator, ArduinoGenerator, CPPGenerator, PythonGenerator

##### Public events extension #####

class BaseGeneratorPublic(BaseGenerator):

    def add_extra_properties(self, events):
        str_public = ['1' if event.public else '0' for event in events]
        ev_public = self._gen_str(str_public)
        return {'ev_public': ev_public}

class ArduinoGeneratorPublic(BaseGeneratorPublic, ArduinoGenerator):
    templates_name = ['arduino_public.ino', 'generic_mic.h']

class CPPGeneratorPublic(BaseGeneratorPublic, CPPGenerator):
    templates_name = ['supervisor_public.yaml', 'sct.cpp', 'sct.h']

class PythonGeneratorPublic(BaseGeneratorPublic, PythonGenerator):
    templates_name = ['supervisor_public.yaml', 'sct.py']
