#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from common import Unimplemented
import data.daten as daten
from data.models import Assistent, Taetigkeit
import ui.data_entry_forms as forms

class ObjectListModel (QtCore.QAbstractItemModel):
    """
    Die Zeilen entsprechen den Einträgen von lst, die Spalten
    Accessor-Funktionen für Objekte.
    """

    def __init__(self, lst, accessors):
        QtCore.QAbstractItemModel.__init__(self)
        self._lst       = lst
        self._header    = [a[0] for a in accessors]
        self._accessors = [a[1] for a in accessors]

    def rowCount(self, parent = QtCore.QModelIndex()):
        if not parent.isValid():
            return len(self._lst)
        else:
            return 0

    def columnCount(self, parent = QtCore.QModelIndex()):
        if not parent.isValid():
            return len(self._accessors)
        else:
            return 0

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if (0 <= row < len(self._lst) and
            0 <= column < len(self._accessors)):
            return self.createIndex(row, column, self._lst[row])
        else:
            return QtCore.QModelIndex()

    def parent(self, child):
        return QtCore.QModelIndex()

    def data(self, index, role = Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            return self._accessors[j](self._lst[i])
        else:
            return None

    def data_raw(self, index):
        if index.isValid():
            i = index.row()
            return self._lst[i]
        else:
            return None

    

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return 0

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[section]
        else:
            return None
    # TODO Benachrichtigung über Änderungen

# TODO Das hier sollte noch verbessert werden können (Zeige
# Assistenten zu Vorlesungen und umgekehrt ...)



class EinfacheTabelle (QtGui.QTreeView):

    def __init__(self, model):
        QtGui.QTreeView.__init__(self)
        self.setModel(model)
        self.setupUi()

    def setupUi(self):
        self.setHeaderHidden(False)
        for i in range(self.model().columnCount()):
            self.resizeColumnToContents(i)


class AssistentenTabelle (EinfacheTabelle):

    def __init__(self):
        EinfacheTabelle.__init__(
            self,
            ObjectListModel(
                daten.assistenten,
                [["Name", Assistent.get_name],
                 ["# Gruppen", Assistent.get_bedarf],
                 ]))

class TaetigkeitenTabelle (EinfacheTabelle):

    # TODO Ordne nach Bereichen

    def __init__(self):
        EinfacheTabelle.__init__(
            self,
            ObjectListModel(
                daten.taetigkeiten,
                [["Titel", Taetigkeit.get_titel],
                 ["Dozent", Taetigkeit.get_dozent],
                 ["# Gruppen", Taetigkeit.get_bedarf],
                 ]))

                          
# Datenerfassungsansicht

class EntryUi (QtGui.QWidget):

    """
    Zeige am oberen Rand drei Knöpfe zum Hinzufügen, Ändern und
    Löschen von Einträgen aus irgendeiner Liste.  Vor dem Löschen wird
    automatisch nachgefragt, ob die Aktion wirklich ausgeführt werden
    soll.  Außerdem wird geprüft, ob tatsächlich eine Auswahl
    vorgenommen wurde.
    """

    # Signale für Erstellen von neuem Eintrag, Löschen von einem Eintrag, sowie Bearbeiten
    neu_signal  = pyqtSignal()
    edit_signal = pyqtSignal(object)
    del_signal  = pyqtSignal(object)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi()

    def get_selected(self):
        raise Unimplemented

    def setupUi(self):
        # Toolbar mit Buttons Neu, Bearbeiten, Löschen
        neu_button  = QtGui.QPushButton("Neu")
        edit_button = QtGui.QPushButton("Bearbeiten")
        del_button  = QtGui.QPushButton(u"Löschen")
        # Mache die Buttons funktionsfähig
        @pyqtSlot()
        def neu_clicked():
            # Einfach Signal senden
            self.neu_signal.emit()
        @pyqtSlot()
        def edit_clicked():
            sel = self.get_selected()
            if sel == None:
                show_message(u"Kein Eintrag zum Bearbeiten ausgewählt!")
            else:
                self.edit_signal.emit(sel)
        @pyqtSlot()
        def del_clicked():
            sel = self.get_selected()
            if sel == None:
                show_message(u"Kein Eintrag zum Löschen ausgewählt!")
            else:
                # Erzeuge schnell Dialog, um Bestätigung zu erfragen
                box = QtGui.QMessageBox()
                box.setWindowTitle(u"Eintrag löschen")
                box.setText(u"Soll der Eintrag {0} wirklich entfernt werden?".format(sel))
                box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                outcome = box.exec_()
                # Lösch-Signal nur, falls bestätigt wurde.
                if outcome == QtGui.QMessageBox.Yes:
                    self.del_signal.emit(sel)
        # connects
        neu_button.clicked.connect(neu_clicked)
        edit_button.clicked.connect(edit_clicked)
        del_button.clicked.connect(del_clicked)

        # richte Layouts ein
        main_layout = QtGui.QVBoxLayout()
        button_layout = QtGui.QHBoxLayout()
        for b in [neu_button, edit_button, del_button]:
            button_layout.addWidget(b)
        button_layout.addStretch()
        # TODO Speichern/Laden Knöpfe ?
        button_box = QtGui.QWidget()
        button_box.setLayout(button_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)


def show_modal(widget):
    """
    Zeige ein Fenster als Dialog an, so dass keine Eingabe in den
    anderen Fenstern mehr möglich ist.
    """
    #widget.setParent(parent)
    widget.setWindowModality(Qt.ApplicationModal)
    widget.show()

def show_message(text):
    box = QtGui.QMessageBox()
    box.setWindowTitle("Nachricht")
    box.setText(text)
    box.setStandardButtons(QtGui.QMessageBox.Ok)
    box.exec_()


class ModelEntryUi (EntryUi):
    """
    Benutze (implizit) ein TreeView, um die Daten eines Models
    anzuzeigen und Einträge zum Bearbeiten und Löschen selektieren zu
    können.
    """

    def __init__(self, collector, tabelle, entry_form, edit_form):
        EntryUi.__init__(self)
        self.tabelle = tabelle()
        self.collector = collector
        self.layout().addWidget(self.tabelle)
        # richte slots ein
        @pyqtSlot()
        def show_new():
            show_modal(entry_form())
            print self.collector # TODO
        @pyqtSlot(object)
        def show_edit(obj):
            show_modal(edit_form(obj))
            print self.collector # TODO
        @pyqtSlot(object)
        def do_delete(obj):
            self.collector.remove(obj)
            daten.save() # TODO
            print self.collector # TODO
        self.neu_signal.connect(show_new)
        self.edit_signal.connect(show_edit)
        self.del_signal.connect(do_delete)
        
    def get_selected(self):
        smodel  = self.tabelle.selectionModel()
        model = self.tabelle.model()
        return model.data_raw(smodel.currentIndex())
        
class AssistentEntryUi (ModelEntryUi):

    def __init__(self):
        ModelEntryUi.__init__(self, daten.assistenten, AssistentenTabelle,
                              forms.AssistentEntry, forms.AssistentEdit)

class TaetigkeitEntryUi (ModelEntryUi):

    def __init__(self):
        ModelEntryUi.__init__(self, daten.taetigkeiten, TaetigkeitenTabelle,
                              forms.TaetigkeitEntry, forms.TaetigkeitEdit)

