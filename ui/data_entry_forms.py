#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from data_entry import EntryFormDialog
from inputs import StringInput, IntegerInput, SelectInput, generate_labels
from data.models import Assistent, Taetigkeit
from data import daten

class AssistentEntry (EntryFormDialog):

    def __init__(self):
        EntryFormDialog.__init__(self, "Assistent anlegen",
                                 [["Name",      StringInput()],
                                  ["# Gruppen", IntegerInput()]])
        self.new_data_signal.connect(self.new_assistent)

    @pyqtSlot(dict)
    def new_assistent(self, data):
        a = Assistent(
            name   = data["Name"],
            bedarf = data["# Gruppen"],
            )
        daten.assistenten.add(a)
        daten.save() # TODO
        
class TaetigkeitEntry (EntryFormDialog):

    def __init__(self):
        EntryFormDialog.__init__(self, u"Tätigkeit anlegen",
                                 [["Titel", StringInput()],
                                  ["Dozent", StringInput()],
                                  ["# Gruppen", IntegerInput(2)],
                                  ["Bereich", SelectInput(
                                      generate_labels(daten.bereiche))],
                                  ])
        self.new_data_signal.connect(self.new_taetigkeit)

    @pyqtSlot(dict)
    def new_taetigkeit(self, data):
        t = Taetigkeit(
            titel = data["Titel"],
            dozent = data["Dozent"],
            bedarf = data["# Gruppen"],
            bereich = data["Bereich"],
            )
        daten.taetigkeiten.add(t)
        daten.save() # TODO
    
                       
