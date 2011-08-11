#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

import sys
from PyQt4 import QtGui
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
        QtGui.QDialog.__init__(self)
        self.setupUi()
        self.setup_buttons()

    def setupUi(self):
        pass
        
    def setup_buttons(self):
        _next   = QtGui.QPushButton(text="Speichern && Weiter")
        _save   = QtGui.QPushButton(text="Speichern")
        _cancel = QtGui.QPushButton(text="Abbrechen")
        # Gruppiere die Knöpfe in einer HBox
        self._button_box = QtGui.QHBoxLayout()
        # self._button_box.layout.addStretch()
        self._button_box.layout.addWidget(_next)
        self._button_box.layout.addWidget(_save)
        self._button_box.layout.addWidget(_cancel)
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
        self.layout.addWidget(self._button_box)

def run_widget(w):
    app = QtGui.QApplication([])
    i = w()
    i.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_widget(SaveNextDialog)
