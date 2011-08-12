#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from common import Unimplemented
import data.daten as daten
from data.models import Assistent, Taetigkeit

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

                          
