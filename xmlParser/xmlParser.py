from xml.dom.minidom import parse
import os
import sys
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)
from machine.automaton import Automaton

def xmlParser(path):
    arquivo = path

    doc = parse(arquivo)
    xml = doc.documentElement

    data = xml.getElementsByTagName('data')

    for info in data:
        states = info.getElementsByTagName('state')
        events = info.getElementsByTagName('event')
        transitions = info.getElementsByTagName('transition')

    G = Automaton()
    stateDict = dict()
    eventDict = dict()

    for state in states:
        name = state.getElementsByTagName('name')[0].childNodes[0].data
        id = state.getAttribute('id')
        isInitial = False
        try:
            properties = state.getElementsByTagName("properties")[0]
            if(properties.getElementsByTagName("initial")[0]):
                isInitial = True
        except:
            pass
        isMarked = False
        try:
            properties = state.getElementsByTagName("properties")[0]
            if(properties.getElementsByTagName("marked")[0]):
                isMarked = True
        except:
            pass
        s = G.state_add(name, marked=isMarked, initial=isInitial)
        stateDict[id] = s

    for event in events:
        name = event.getElementsByTagName('name')[0].childNodes[0].data
        id = event.getAttribute('id')
        isObservable = False
        try:
            properties = event.getElementsByTagName("properties")[0]
            if(properties.getElementsByTagName("observable")[0]):
                observable = True
        except:
            pass
        isControllable = False
        try:
            properties = event.getElementsByTagName("properties")[0]
            if(properties.getElementsByTagName("controllable")[0]):
                controllable = True
        except:
            pass
        ev = G.event_add(name,observable=isObservable, controllable=isControllable)
        eventDict[id] = ev
    for transition in transitions:
        tEvent = transition.getAttribute('event')
        tSource = transition.getAttribute('source')
        tTarget = transition.getAttribute('target')
        ev = eventDict[tEvent]
        ss = stateDict[tSource]
        st = stateDict[tTarget]
        G.transition_add(ss, st, ev)



    return G

