#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from data_entry import EntryFormDialog
from inputs import StringInput, IntegerInput, SelectInput, generate_labels
from data.models import Assistent, Taetigkeit, Bound
from data import daten

# ----------------------------------------------------------------------

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
        daten.assistenten.notify_changes()
        daten.save() # TODO
        
class AssistentEdit (AssistentEntry):

    def __init__(self, ass):
        AssistentEntry.__init__(self)
        self._ass = ass
        self.setTitle("Assistent bearbeiten")
        self.hide_next()
        self.load({"Name"      : ass._name,
                   "# Gruppen" : ass._bedarf._upper,
                   })

    @pyqtSlot(dict)
    def new_assistent(self, data):
        self._ass._name   = data["Name"]
        self._ass._bedarf = Bound(data["# Gruppen"])
        daten.assistenten.notify_changes()
        daten.save() # TODO

# ----------------------------------------------------------------------

class TaetigkeitEntry (EntryFormDialog):

    def __init__(self):
        EntryFormDialog.__init__(self, u"Tätigkeit anlegen",
                                 [["Titel",     StringInput()],
                                  ["Dozent",    StringInput()],
                                  ["# Gruppen", IntegerInput(2)],
                                  ["Bereich",   SelectInput(
                                    generate_labels(daten.bereiche))],
                                  ])
        self.new_data_signal.connect(self.new_taetigkeit)

    @pyqtSlot(dict)
    def new_taetigkeit(self, data):
        t = Taetigkeit(
            titel   = data["Titel"],
            dozent  = data["Dozent"],
            bedarf  = data["# Gruppen"],
            bereich = data["Bereich"],
            )
        daten.taetigkeiten.add(t)
        daten.taetigkeiten.notify_changes()
        daten.save() # TODO
    
class TaetigkeitEdit (TaetigkeitEntry):

    def __init__(self, taet):
        TaetigkeitEntry.__init__(self)
        self._taet = taet
        self.setTitle(u"Tätigkeit bearbeiten")
        self.hide_next()
        self.load({"Titel"     : taet._titel,
                   "Dozent"    : taet._dozent,
                   "# Gruppen" : taet._bedarf._upper,
                   "Bereich"   : taet._bereich,
                   })

    @pyqtSlot(dict)
    def new_taetigkeit(self, data):
        self._taet._titel   = data["Titel"]
        self._taet._dozent  = data["Dozent"]
        self._taet._bedarf  = Bound(data["# Gruppen"])
        self._taet._bereich = data["Bereich"]
        daten.taetigkeiten.notify_changes()
        daten.save() # TODO
