'''This module houses code that will drive the thread based part of MgProxy'''

from threading import Lock


class MgInfo(object):

    '''A thread-safe container for information producer by MgProxy.

    Not all information during a threaded run of MgProxy can be logged right
    away. This container will provide a thread-safe way to store this
    information across threads till it can be printed at the end of the program
    '''

    def __init__(self):
        self._lock = Lock()
        self._pages = 0  # Number of pages successfully pasted
        self._cards = 0  # Number of cards successfully pasted
        self._bad_parse = []  # Input lines that could not be parsed
        self._bad_card = []  # Cards that could not be retrieved

    def addPage(self):
        with self._lock:
            self._pages += 1

    def addCards(self, card_number):
        with self._lock:
            self._cards += card_number

    def addBadParse(self, bad):
        with self._lock:
            self._bad_parse.append(bad)

    def addBadCard(self, bad):
        with self._lock:
            self._bad_card.append(bad)
