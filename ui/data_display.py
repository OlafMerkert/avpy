#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from common import Unimplemented
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

class IndexNode (QObject):

    def __init__(self, obj, accessors, child, parent):
        QObject.__init__(self)
        self.object    = obj
        self.accessors = accessors
        self.child     = child
        self.parent    = parent

def invalid_index():
    return QtCore.QModelIndex()

class ObjectListModel (QtCore.QAbstractItemModel):
    """
    TODO
    """

    def __init__(self, header, *tree):
        QtCore.QAbstractItemModel.__init__(self)
        self._object_store = []
        self._header = header
        def transform_tree(t):
            if len(t) >= 3:
                return AccessorNode(t[0], t[1], transform_tree(t[2]))
            else:
                return AccessorNode(*t)
        self.accessor_tree = transform_tree(list(tree))

    def _set_by_index(self, obj):
        l = len(self._object_store)
        self._object_store.append(obj)
        return l

    def _get_by_index(self, index):
        nr = index.internalPointer()
        if isinstance(nr, int):
            return self._object_store[nr]
        else:
            return IndexNode(obj=None, accessors=[], child=None, parent=invalid_index())


    def rowCount(self, parent = invalid_index()):
        print "rowcount"
        if not parent.isValid():
            # An der Wurzel
            lst = self.accessor_tree.list(None)
            return len(lst)
        elif parent.child:
            # An einem Knoten mit Kindchen
            node = self._get_by_index(parent)
            lst = node.child.list(node.object)
            return len(lst)
        else:
            return 0

    def columnCount(self, parent = invalid_index()):
        print "colcount"
        if not parent.isValid():
            print "root"
            node = self.accessor_tree
            return len(node.accessors)
        else:
            print "Row", parent.row(), "Col", parent.column()
            print "before intpoint"
            node = self._get_by_index(parent)
            print "after intpoint"
            print node
            print "after print node"
            if node and node.child:
                print "non-root"
                node = self._get_by_index(parent)
                print "node:",
                print node
                return len(node.accessors)
            else:
                return 0

    # @ensureValid(3)
    def index(self, row, column, parent = invalid_index()):
        print "index", row, column
        if not parent.isValid():
            print "invalid"
            # An der Wurzel
            node = self.accessor_tree
            return self.createIndex(row, column,
                                    self._set_by_index(
                                        IndexNode(obj=node.list(True)[row],
                                                  accessors=node.accessors,
                                                  child=node.child,
                                                  parent=parent)))
        else:
            print "valid"
            node = self._get_by_index(parent) # this is an IndexNode
            if node.child and parent.column() == 0: # either is None or an AccessorNode
                return self.createIndex(row, column,
                                        self._set_by_index(
                                            IndexNode(obj=node.child.list(node.object)[row],
                                                      accessors=node.child.accessors,
                                                      child=node.child.child,
                                                      parent=parent)))
            else:
                return invalid_index()
    
    # @ensureValid(1)
    def parent(self, child):
        print "parent"
        if child.isValid():
            return self._get_by_index(child).parent
        else:
            return invalid_index()

    def data(self, index, role = Qt.DisplayRole):
        print "data"
        if index.isValid() and role == Qt.DisplayRole:
            node = self._get_by_index(index)
            return node.accessors[index.column()](node.object)
        else:
            return None

    def data_raw(self, index):
        if index.isValid():
            node = self._get_by_index(index)
            return node.object
        else:
            return None

    def flags(self, index):
        print "flags"
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return 0

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        print "header"
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[section]
        else:
            return None
    # TODO Benachrichtigung über Änderungen

    def attach_collection(self, collector):
        # @pyqtSlot()
        # def update():
        #     self.dataChanged.emit(invalid_index(), invalid_index())
        # collector.change_signal.connect(update)
        pass
    
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

def gt(f, i):
    def g(x):
        if x >= i:
            print "Hallo"
        return f(x)
    return g
