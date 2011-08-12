#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

__author__ = "Olaf Merkert"


from os.path import exists
import cPickle as pickle
import models

# Listen für die Speicherung der Vorlesungen und Assistenten sowie
# ihrer Wünsche

# TODO Eigene Datenstruktur für diese Listen?
class Collector(object):
    """
    Halte eine Liste/Menge von Objekten vor.
    """
    
    def __init__(self):
        self._list = []

    def add(self, item):
        self._list.append(item)

    def rem(self, item):
        self._list.rem(item)

    def load(self, liste):
        self._list = liste
        
    def clear(self):
        self._list = []

    def __iter__(self):
        return iter(self._list)

    def save(self):
        return self._list

    def __repr__(self):
        return "Collector: " + str(self._list)

taetigkeiten = Collector()
assistenten  = Collector()

# Ein paar hartkodierte Einstellungen
bereiche = [
    "Grundstudium",
    "Aufbaustudium",
    "Master",
    ]

# laden und speichern der daten

default_store = "/tmp/avpy.bin"


def load(store = default_store):
    def get_if_present(key, dct):
        if key in dct:
            return dct[key]
        else:
            return []
    if exists(store):
        with open(store, 'rb') as input:
            data = pickle.load(input)
            taetigkeiten.load(get_if_present("taet", data))
            assistenten.load(get_if_present("ass", data))
    else:
        taetigkeiten.load([])
        assistenten.load([])

def save(store = default_store):
    with open(store, 'wb') as output:
        pickle.dump({"taet" : taetigkeiten.save(),
                     "ass"  : assistenten.save(),
             }, output)
