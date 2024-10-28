#!/usr/bin/python

import sys

# import pluggins # this causes errors in python 3.8.9+
from machine.automaton import Automaton
from gui import Application
from gui.parse_argument import Extension

if __name__ == '__main__':
    Extension.parse_arguments(sys.argv[1:])
    filtered_args = [arg for arg in sys.argv if arg.startswith('--') and arg not in ['--mode']]

    application = Application()
    application.run(filtered_args)
