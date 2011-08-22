#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

__author__ = "Olaf Merkert"

from os.path import exists
import cPickle as pickle
import models
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal

# Listen für die Speicherung der Vorlesungen und Assistenten sowie
# ihrer Wünsche

# TODO Versehe dieses mit Signalen und Slots, um Änderungen in der Datenstruktur vermelden zu können.
class Collector(object):
    """
    Halte eine Liste/Menge von Objekten vor.  Die Schnittstelle nach
    außen ist wesentlich die einer normalen Liste.
    """
    
    def __init__(self):
        self._list = []

    def add(self, item):
        self._list.append(item)

    def remove(self, item):
        self._list.remove(item)

    def load(self, liste):
        self._list = liste
        
    def clear(self):
        self._list = []

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]

    def save(self):
        return self._list

    def __repr__(self):
        return "Collector: " + str(self._list)

    # Verarbeitung von Änderungen an den Daten/Struktur des Collectors
    def listener(self):
        return listeners[self]

    def changed(self):
        self.listener().changed()

    def add_changed_slot(self, slot):
        self.listener().add_changed_slot(slot)

class ChangeListener (QObject):

    change_signal = pyqtSignal()

    def __init__(self, acro, collector):
        QObject.__init__(self)
        self.acro      = acro
        self.collector = collector

    def changed(self):
        self.change_signal.emit()

    def add_changed_slot(self, slot):
        self.change_signal.connect(slot)

taetigkeiten = Collector()
assistenten  = Collector()

listeners = {
    taetigkeiten : ChangeListener("taet", taetigkeiten),
    assistenten  : ChangeListener("ass",  assistenten),
    }

# Ein paar hartkodierte Einstellungen
bereiche = [
    "Grundstudium",
    "Aufbaustudium",
    "Master",
    ]

# laden und speichern der daten

default_store = "/tmp/avpy.bin"

# TODO Abspeichern sollte auf transparente Art von der Anwendung her
# passieren können.  Wenn explizite Aufrufe irgendwo mitten im Code
# passieren, ist das etwas suboptimal.
def load(store = default_store):
    def get_if_present(key, dct):
        if key in dct:
            return dct[key]
        else:
            return []
    if exists(store):
        with open(store, 'rb') as input:
            data = pickle.load(input)
            for coll, ch_slot in listeners.iteritems():
                coll.load(get_if_present(ch_slot.acro, data))
    else:
        for coll, ch_slot in listeners.iteritems():
            coll.load([])

def save(store = default_store):
    with open(store, 'wb') as output:
        pickle.dump(
            dict([(ch_slot.acro, coll.save())
                  for coll, ch_slot in listeners.iteritems()]),
            output)

@pyqtSlot()
def on_changed():
    save()

taetigkeiten.add_changed_slot(on_changed)
assistenten.add_changed_slot(on_changed)
