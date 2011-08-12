#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

# import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
 
# Ein paar spezielle Funktionen und Dialoge, die speziell für die
# Dateneingabe angepasst sind.

class SaveNextDialog (QtGui.QWidget):
    """
    Ein Dialog mit einer Gruppe von Buttons, die zum effizienten
    Erfassen einen Knopf zum `Speichern + nächste Eingabe', einen
    Knopf zum `Speichern + Schließen' und einen Knopf zum `Abbrechen
    und Schließen' bereitstellen.
    """
    save_signal  = pyqtSignal()
    close_signal = pyqtSignal()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QVBoxLayout())
        self.setupUi()
        self.setup_buttons()

    def setupUi(self):
        pass
        
    def setup_buttons(self):
        _next   = QtGui.QPushButton(text="Speichern && Weiter")
        _save   = QtGui.QPushButton(text="Speichern")
        _cancel = QtGui.QPushButton(text="Abbrechen")
        # Gruppiere die Knöpfe in einer HBox
        self._button_box = QtGui.QWidget()
        self._button_box.setLayout(QtGui.QHBoxLayout())
        self._button_box.layout().addStretch()
        self._button_box.layout().addWidget(_next)
        self._button_box.layout().addWidget(_save)
        self._button_box.layout().addWidget(_cancel)
        # Lasse Signale erzeugen
        @pyqtSlot()
        def next_clicked():
            self.save_signal.emit()
        @pyqtSlot()
        def save_clicked():
            self.save_signal.emit()
            self.close_signal.emit()
        @pyqtSlot()
        def cancel_clicked():
            self.close_signal.emit()
        # Verbinde mit den Signalen der Buttons
        _next.clicked.connect(next_clicked)
        _save.clicked.connect(save_clicked)
        _cancel.clicked.connect(cancel_clicked)
        # Stecke die Box ans Ende
        self.layout().addStretch()
        self.layout().addWidget(self._button_box)

class EntryFormDialog (SaveNextDialog):
    """
    Erzeuge ein Eingabeformular durch Angeben eines Titel und
    """

    new_data_signal = pyqtSignal(dict)

    def __init__(self, title, form_elements):
        SaveNextDialog.__init__(self)
        self.setWindowTitle(title)
        self._form.setTitle(title)
        self.setup_inputs(form_elements)
        self.save_signal.connect(self.on_save)
        self.close_signal.connect(self.on_close)
        # Damit der Dialog nicht geschlossen wird, bevor alle Daten
        # ausgelesen sind, brauchen wir ein kleines Lock.
        self.close_lock = QtCore.QMutex()

    def setupUi(self):
        # Die Eingabefelder kommen in eine GroupBox.  Der Titel wird
        # später gesetzt.
        self._form = QtGui.QGroupBox()
        self._form.setLayout(QtGui.QFormLayout())
        self.layout().addWidget(self._form)

    def setup_inputs(self, form_elements):
        self._inputs = {}
        for label, widget in form_elements:
            l = QtGui.QLabel(label)
            i = widget
            # Die Inputs halten wir in einem dict vor
            self._inputs[label] = i
            self._form.layout().addRow(l, i)

    def load(self, data):
        """
        Fülle die Formularfelder mit Werten aus dem gegebenen dict,
        oder setze zurück, falls kein Wert gegbenen ist.
        """
        for l,i in self._inputs.iteritems():
            if l in data:
                i.setData(data[l])
            else:
                i.setData()
                
    @pyqtSlot()
    def on_save(self):
        self.close_lock.lock()
        # Hole alle Daten aus den Eingabefeldern
        data = {}
        for l,i in self._inputs.iteritems():
            data[l] = i.data()
        # Setze alle Eingabefelder zurück
        self.load({})
        self.new_data_signal.emit(data)
        self.close_lock.unlock()

    @pyqtSlot()
    def on_close(self):
        self.close_lock.lock()
        # Schließe das Fenster
        self.close()
        self.close_lock.unlock()
        
