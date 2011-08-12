#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4 import QtGui
from common import Unimplemented


class InputBase(object):
    """
    Interface für Eingabeelemente in Formularen
    """

    def default_value(self):
        raise Unimplemented
    
    def data(self):
        raise Unimplemented

    def setData(self, value = None):
        if value == None:
            self.setData(self.default_value())
        else:
            self._setData(value)

    def _setData(self, value):
        raise Unimplemented

class StringInput(QtGui.QLineEdit, InputBase):
    """
    Eingabe von Strings mit einem QLineEdit.
    """

    def __init__(self, *parms):
        QtGui.QLineEdit.__init__(self, *parms)

    def default_value(self):
        return ""

    def data(self):
        return str(self.text())

    def _setData(self, value):
        self.setText(value)

class IntegerInput(QtGui.QSpinBox, InputBase):
    """
    Eingabe von ganzen Zahlen mit einer QSpinBox.  Als Parameter kann
    ein Standardwert gegeben werden.
    """

    def __init__(self, default = 1, *parms):
        QtGui.QSpinBox.__init__(self, *parms)
        self._default = default
        self._setData(default)

    def default_value(self):
        return self._default

    def data(self):
        return self.value()

    def _setData(self, value):
        self.setValue(value)

class SelectInput(QtGui.QComboBox, InputBase):
    """
    Auswahl eines Eintrags aus einer Liste.  Als Parameter wird eine
    Liste von Tupeln erwartet, deren erster Eintrag ein String, der
    zweite ein beliebiges Objekt sein kann.  Der ausgewählte Index
    wird transparent zu den jeweiligen Objekten umgewandelt.
    """
    
    def __init__(self, underlying_list = [], *parms):
        QtGui.QComboBox.__init__(self, *parms)
        self._underlying = underlying_list
        for l,i in underlying_list:
            self.addItem(l, i)

    def data(self):
        return self._underlying[self.currentIndex()][1]

    def setData(self, value = None):
        if value == None:
            self.setCurrentIndex(0)
        else:
            i = self.findData(value)
            self.setCurrentIndex(i)

def generate_labels(lst):
    """
    Transformiere eine Liste für die Benutzung mit SelectInput.  Jedem
    Element wird ein Tupel String-Repräsentation, Element zugeordnet.
    """
    return [[str(l), l] for l in lst]
