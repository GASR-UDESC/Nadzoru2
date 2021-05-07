#!/usr/bin/python

import sys

import pluggins
from machine.automaton import Automaton
from gui import Application

if __name__ == '__main__':
    application = Application()
    application.run(sys.argv)
    