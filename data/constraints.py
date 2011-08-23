#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

"""
Damit die Zuteilung erfolgreich ist, müssen reihenweise Bedingungen
erfüllt sein.  Sie operieren auf einer Liste von Zuweisungen.
"""

import data.daten as daten

class WrongBedarfException (object):
    """
    TODO
    """
    
    def __init__(self, obj, number):
        self._obj = obj
        self._num = number

def zuweisungen_zaehlen(zuweisungen):
    # Zähle Zuweisungen per Assistent, Tätigkeit
    ass  = defaultdict(lambda : 0)
    taet = defaultdict(lambda : 0)
    for z in zuweisungen:
        ass[z._assistent]   += 1
        taet[z._taetigkeit] += 1
    # Prüfe, ob die Zahlen im Rahmen sind
    for a in daten.assistenten:
        if not a._bedarf.within(ass[a]):
            raise WrongBedarfException(a, ass[a])
    for t in daten.taetigkeit:
        if not t._bedarf.within(taet[t]):
            raise WrongBedarfException(t, taet[t])
    # Da wir defaultdict verwenden, wird es keine KeyError's geben
    return True

def zuweisungen_zaehlen_p(zuweisungen):
    try:
        zuweisungen_zaehlen(zuweisungen)
    except WrongBedarfException:
        return False
    return True
