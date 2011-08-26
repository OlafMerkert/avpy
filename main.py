#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

import sys
from PyQt4 import QtGui
import ui.data_entry_forms as forms
import data.models
import data.daten as daten
from ui.data_display import AssistentenTabelle, TaetigkeitenTabelle, AssistentEntryUi, TaetigkeitEntryUi


if __name__ == '__main__':
    app = QtGui.QApplication([])
    daten.load()
    # print daten.assistenten
    m = AssistentEntryUi()
    # m = TaetigkeitEntryUi()
    m.show()
    sys.exit(app.exec_())
