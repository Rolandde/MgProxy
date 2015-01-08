'''This module houses code that will drive the thread based part of MgProxy'''

from threading import Lock, Thread
import os

from src.get_image import getMgImage, getLocalMgImage
from src.constants import MgNetworkException, MgImageException
from src.logger_dict import MG_LOGGER_CONST, logCardName
from src.image_manip import createCanvas

# Can be passed to the queue loop to break out of it
THREAD_END = None


class MgReport(object):

    '''A thread-safe container for information producer by MgProxy.

    Not all information during a threaded run of MgProxy can be logged right
    away. This container will provide a thread-safe way to store this
    information across threads till it can be printed at the end of the program
    '''

    def __init__(self):
        self._lock = Lock()
        self._pages = 0  # Number of pages successfully pasted
        self._cards = 0  # Number of cards successfully pasted
        self._errors = 0  # The number of errors encountered by program

    def addPage(self):
        with self._lock:
            self._pages += 1

    def addCards(self, card_number):
        with self._lock:
            self._cards += card_number

    def addError(self):
        with self._lock:
            self._errors += 1

    @property
    def pages(self):
        with self._lock:
            return self._pages


class MgGetImageThread(Thread):

    '''A queue based thread for downloading and passing on MG images.

    The In-Queue accepts the standard parsed tupple (SB, Card#, Set, Name),
    downloads the image and passes it off to the Out-Queue. In addition,
    optional thread-safe logging and report objects can be passed to init.
    By default, gets the images from the web. Provide directory of local images
    to get images from local folder.
    '''

    def __init__(
        self, in_queue, out_queue, local='', logger=None, reporter=None
    ):
        # Call init of Thread before doing anything else
        super(MgGetImageThread, self).__init__()

        self.in_queue = in_queue
        self.out_queue = out_queue
        self.local = local
        self.logger = logger
        self.reporter = reporter

    def run(self):
        '''The main loop of the MgGetImageThread.

        Takes items off the In-Queue and passes them off to be processed.
        The loop can be interrupted by the THREAD_END constant.
        '''
        while True:
            card_item = self.in_queue.get()
            if card_item is THREAD_END:
                self.in_queue.task_done()
                break

            if self.local:
                self.getImageFromDisk(self.local, card_item)
            else:
                self.getMgImageFromWeb(card_item)

            self.in_queue.task_done()

    def getMgImageFromWeb(self, card_tupple):
        '''Download the image from the web and puts it in Out-Queue.'''
        card_name = card_tupple[3]
        set_name = card_tupple[2]

        try:
            image = getMgImage(card_name, set_name)
        except MgNetworkException as reason:
            self.logError(
                MG_LOGGER_CONST['card_error'] % (
                    # logCardName expects a tupple of card info
                    logCardName(card_tupple),
                    reason
                )
            )
        except MgImageException as reason:
            self.logError(MG_LOGGER_CONST['image_file_error'] % (
                logCardName(card_tupple),
                reason
            ))
        else:
            self.out_queue.put(image)

    def getImageFromDisk(self, directory, card_tupple):
        '''Get image from local disk and put it in the Out-Queue.'''
        card_name = card_tupple[3]

        try:
            image = getLocalMgImage(directory, card_name)
        except MgImageException as reason:
            self.logError(MG_LOGGER_CONST['image_file_error'] % (
                logCardName(card_tupple),
                reason
            ))
        else:
            self.out_queue(image)

    def logError(self, message):
        '''Logs an error message if a logger has been provided.

        Also counts up the error in the reporter.
        '''
        if self.logger:
            self.logger.error(message)

        if self.reporter:
            self.reporter.addError()


class MgImageCreateThread(Thread):

    '''A queue based thread that crates a page from individual images.

    As the operations are CPU bound, only one thread of this class should be
    used. It has been written with that limitation in mind. It spawns threads
    to save the pages as that is the limiting I/O step in the process.
    '''

    def __init__(
        self, dpi, wh, xy, directory, file_name, logger=None, reporter=None
    ):
        super(MgImageCreateThread, self).__init__()
        self.dpi = dpi
        self.wh = wh
        self.xy = xy

        self.directory = directory
        self.file_name = file_name

        self.pic_count = 0  # How many pictures on the current page
        self.current_page = 0  # How many pages have been created so far
        self.current_canvas = createCanvas(dpi, wh, xy)

        self.logger = logger
        self.reporter = reporter

    def save(self, canvas):
        '''Saves the file_name to the directory.

        It is spawned off as a seperate thread due to its I/O nature.
        '''
        new_file_name = str(self.file_name) + str(self.reporter.pages) + '.jpg'
        file_path = os.path.join(self.directory, new_file_name)

        try:
            canvas.save(file_path)
        except IOError as e:
            self.logError(MG_LOGGER_CONST['save_fail'] % (
                e.filename, e.strerror
            ))
        else:
            if self.reporter:
                self.reporter.addPage()

    def logError(self, message):
        '''Logs an error message if a logger has been provided'''
        if self.logger:
            self.logger.error(message)
