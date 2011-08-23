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

    def within(self, number):
        return (self._lower <= number <= self._upper)

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

    def __repr__(self):
        return "{0} - {1} [{2}]".format(self._titel, self._dozent, self._bedarf._upper)
    
class Wunsch(object):
    """
    Mit verschiedenem Nachdruck kann man die gewuenschten
    Veranstaltungen sortieren.
    """
    
    def __init__(self, assistent, taetigkeit, staerke):
        self._assistent = assistent
        self._taetigkeit = taetigkeit
        self._staerke = staerke

    def __repr__(self):
        return "{0} : {1} : W{2}".format(self._assistent.get_name(),
                                         self._taetigkeit.get_titel(),
                                         self._staerke)

    def __eq__(self, other):
        return (isinstance(other, Wunsch) and
                self._assistent == other._assistent and
                self._taetigkeit == other._taetigkeit)

    def __hash__(self):
        return (self._assistent.__hash__() ^ # xor
                self._taetigkeit.__hash__())

    def __ne__(self, other):
        return not self.__eq__(other)

    def zuweisen(self, tabelle):
        z = Zuweisung(self._assistent,
                      self._taetigkeit,
                      self.score())
        tabelle.add(z)
        return z

    def score(self):
        return (4 - self._staerke)**2


    def get_assistant(self):
        return self._assistant.get_name()

    def get_taetigkeit(self):
        return self._taetigkeit.get_titel()

    def get_staerke(self):
        return "W{0}".format(self._staerke)
    

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

    def get_wuensche(self):
        # sortiere nach staerke
        return sorted(self._wuensche, key=lambda w: w._staerke)

    def wuensche(self):
        return [w._taetigkeit for w in self._wuensche]
    

class Zuweisung(object):
    """
    Gebe einem Assistenten eine bestimmte Vorlesung.
    """
    
    def __init__(self, assistent, taetigkeit, score = 0, fest = False):
        self._assistent = assistent
        self._taetigkeit = taetigkeit
        self._score = score
        self._fest = fest
        

