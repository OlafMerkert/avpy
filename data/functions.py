#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

import daten

def wuensche_t(taetigkeit):
    """Alle Assistenten, die sich die gegebene Vorlesunge wuenschen."""
    return [ass for ass in daten.assistenten
            if taetigkeit in ass.wuensche()]
