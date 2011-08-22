#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from common import Unimplemented, LockableRingBuffer
import data.daten as daten
from data.models import Assistent, Taetigkeit, Wunsch
import ui.data_entry_forms as forms
from collections import namedtuple

class InvalidTreeAdress:
    pass

class AccessorNode (QObject):

    def __init__(self, lst, accessors, child=None):
        QObject.__init__(self)
        self.list      = lst
        self.accessors = accessors
        self.child     = child

class CustomModelIndex (object):

    def __init__(self, index, obj, accessors, child, parent):
        self.index     = index
        self.object    = obj
        self.accessors = accessors
        self.child     = child
        self.parent    = parent
        self.level     = 0

    def isValid(self):
        return self.index.isValid()

    def row(self):
        return self.index.row()

    def column(self):
        return self.index.column()

empty_accessor = lambda x: ""

def to_length(lst, length, fill=None):
    l = length - len(lst)
    if l < 0:
        return lst[:length]
    else:
        new_lst = lst[:]
        for i in xrange(l):
            new_lst.append(fill)
        return new_lst

class ObjectListModel (QtCore.QAbstractItemModel):
    """
    TODO
    """

    def __init__(self, header, *tree):
        QtCore.QAbstractItemModel.__init__(self)
        self._buffer = LockableRingBuffer()
        self._header = header
        l = len(tree[1])
        def transform_tree(t):
            # Die Accessorenlisten sollten immmer die selbe Länge haben.
            a = to_length(t[1], length=l, fill=empty_accessor)
            if len(t) >= 3:
                return AccessorNode(t[0], a, transform_tree(t[2]))
            else:
                return AccessorNode(t[0], a)
        self.accessor_tree = transform_tree(list(tree))

    
    def invalid_index(self, custom = True, index = QtCore.QModelIndex()):
        if custom:
            index = CustomModelIndex(index     = index,
                                     obj       = None,
                                     accessors = [],
                                     child     = self.accessor_tree,
                                     parent    = None)
            index.parent = index 
        return index

    def valid_index(self, row, column, obj, accessors, child, parent):
        i = self._buffer.reserve()
        mindex = self.createIndex(row, column, i)
        index = CustomModelIndex(index     = mindex,
                                 obj       = obj,
                                 accessors = accessors,
                                 child     = child,
                                 parent    = parent)
        index.level = 1 + parent.level
        self._buffer[i] = index
        return index

    def _data2index(self, data):
        pass

    def _index2data(self, index):
        pass

    def ensure_nice_index(self, index):
        if index.isValid():
            i = index.internalId()
            return self._buffer[i]
        else:
            return self.invalid_index(index=index)

    def rowCount(self, parent = QtCore.QModelIndex()):
        parent = self.ensure_nice_index(parent)
        if parent.child:
            return len(parent.child.list(parent.object))
        else:
            return 0
        
    def columnCount(self, parent = QtCore.QModelIndex()):
        parent = self.ensure_nice_index(parent)
        if parent.child:
            return len(parent.child.accessors)
        else:
            return 0
    
    def parent(self, child):
        child = self.ensure_nice_index(child)
        if child.parent:
            return child.parent.index
        else:
            return self.invalid_index(False)
        
    def data(self, index, role = Qt.DisplayRole):
        index = self.ensure_nice_index(index)
        if index.isValid() and role == Qt.DisplayRole:
            d = index.accessors[index.column()](index.object)
            return d
        else:
            return None

    def data_raw(self, index):
        index = self.ensure_nice_index(index)
        if index.isValid():
            return index.object
        else:
            return None

    def index(self, row, column, parent = QtCore.QModelIndex()):
        parent = self.ensure_nice_index(parent)
        if parent.child:
            lst = parent.child.list(parent.object)
            index = self.valid_index(row       = row,
                                     column    = column,
                                     obj       = lst[row],
                                     accessors = parent.child.accessors,
                                     child     = parent.child.child,
                                     parent    = parent)
            return index.index
        else:
            raise InvalidTreeAdress

    def flags(self, index):
        # TODO invalid results ?
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

    def attach_collection(self, collector):
        @pyqtSlot()
        def update():
            self.reset()
        collector.add_changed_slot(update)
    
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
                ["Name", "# Gruppen"],
                lambda x: daten.assistenten,
                [Assistent.get_name,
                 Assistent.get_bedarf],
                [Assistent.get_wuensche,
                 [Wunsch.get_taetigkeit]]
                )
            )
        self.model().attach_collection(daten.assistenten)

class TaetigkeitenTabelle (EinfacheTabelle):

    # TODO Ordne nach Bereichen

    def __init__(self):
        EinfacheTabelle.__init__(
            self,
            ObjectListModel(
                ["Titel", "Dozent", "# Gruppen"],
                lambda x: daten.taetigkeiten,
                [Taetigkeit.get_titel,
                 Taetigkeit.get_dozent,
                 Taetigkeit.get_bedarf],
                )
            )
        self.model().attach_collection(daten.taetigkeiten)

                          
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
            self.collector.changed()
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

# TODO Fokusoptimierung beim Aufrufen der Dialoge
# TODO Fokusoptimierung innerhalb der Dialoge
