#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Olaf Merkert"

from PyQt4.QtCore import QReadWriteLock

class Unimplemented (object):
    pass

class LockableRingBuffer (object):

    """
    Ein Ring Buffer mittels einfacher Liste, der Lese- und
    Schreibzugriffe nicht simultan überwacht.  Lesezugriff ist
    wahlfrei mit buffer[i], Schreibzugriff geht nur über
    buffer.append(item), welches den Index des gespeicherten Objekts
    zurückgibt.
    """

    def __init__(self, size = 10000):
        self.size         = size
        self.fill_pointer = 0
        self.ring         = [None] * size
        self.lock         = QReadWriteLock()

    def __getitem__(self, index):
        self.lock.lockForRead()
        item = self.ring[index % self.size]
        self.lock.unlock()
        return item

    def __setitem__(self, index, item):
        self.lock.lockForWrite()
        self.ring[index % self.size] = item
        self.lock.unlock()

    def __len__(self):
        return self.size

    def append(self, item):
        self.lock.lockForWrite()
        i = self.fill_pointer
        self.ring[i] = item
        self.fill_pointer = (i + 1) % self.size
        self.lock.unlock()
        return i

    def reserve(self):
        self.lock.lockForWrite()
        i = self.fill_pointer
        self.fill_pointer = (i + 1) % self.size
        self.lock.unlock()
        return i
