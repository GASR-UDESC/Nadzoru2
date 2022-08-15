#!/usr/bin/python

import sys

# import pluggins # this causes errors in python 3.8.9+
from machine.automaton import Automaton
from gui import Application

if __name__ == '__main__':
    application = Application()
    application.run(sys.argv)

