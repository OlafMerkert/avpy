#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

# Modelle für die Arbeitsverteilung-Anwendung

class Bound(object):
    def __init__(self, lower, upper=None):
        self._lower = lower
        if upper:
            self._upper = upper
        else:
            self._upper = lower

class Taetigkeit(object):
    """
    Jede Vorlesung und jedes Seminar benötigt eine gewisse Anzahl von
    Assistenten.
    """
    
    def __init__(self, titel, bedarf, dozent = "", bereich = "", termin = "", bemerkung = ""):
        self._titel = titel
        self._bedarf = Bound(bedarf)
        self._dozent = dozent
        self._bereich = bereich
        self._termin = termin
        self._bemerkung = bemerkung

    def get_titel(self):
        return self._titel

    def get_dozent(self):
        return self._dozent

    def get_bedarf(self):
        return self._bedarf._upper
    
class Wunsch(object):
    """
    Mit verschiedenem Nachdruck kann man die gewuenschten
    Veranstaltungen sortieren.
    """
    
    def __init__(self, assistent, taetigkeit, staerke):
        self._assistent = assistent
        self._taetigkeit = taetigkeit
        self._staerke = staerke

    def zuweisen(self, tabelle):
        z = Zuweisung(self._assistent,
                      self._taetigkeit,
                      self.score())
        tabelle.add(z)
        return z

    def score(self):
        return (4 - self._staerke)**2



class Assistent(object):
    """
    Jeder Assistent hat 1 oder mehr Übungsstunden zu halten.  Vor der
    Verteilung dürfen mehrere Wünsche geäußert werden.
    """
    
    def __init__(self, name, bedarf = 1):
        self._name = name
        self._bedarf = Bound(bedarf)
        self._wuensche = set()

    def wuenschen(self, taetigkeit, staerke):
        self._wuensche.add(
            Wunsch(self, taetigkeit, staerke))

    def __repr__(self):
        return "{0} [{1}]".format(self._name, self._bedarf._upper)

    # Accessors
    def get_name(self):
        return self._name
    def get_bedarf(self):
        return self._bedarf._upper
    

class Zuweisung(object):
    """
    Gebe einem Assistenten eine bestimmte Vorlesung.
    """
    
    def __init__(self, assistent, taetigkeit, score = 0, fest = False):
        self._assistent = assistent
        self._taetigkeit = taetigkeit
        self._score = score
        self._fest = fest
        

