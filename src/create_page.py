from Queue import Queue

from src.mg_thread import (MgReport, MgGetImageThread, MgImageCreateThread,
                           MgQueueCar)
from src.constants import IMAGE_GET_THREAD

# from src.logger_dict import MG_LOGGER_CONST, logCardName


class MgImageCreator(object):

    '''Places MG card images onto a canvas for easy printing and cutting.

    This object takes the canvas DPI, the width/hight of cards, and the number
    of cards on each canvas. The save directory and file_name are also given.
    Lastly, an optional logger object can be provided.
    '''

    def __init__(self, dpi, wh, xy, logger=None):
        self.dpi = dpi
        self.wh = wh
        self.xy = xy
        self.logger = logger

    def create(self, local, input_array, directory, file_name):
        '''Initiates the creation of pictures.

        If local is true, takes pictures from files found in directory.
        Input array is a list of tupples for each card.
        Pages will be saved to directory with file_name
        '''

        # source is an empty string for web, directory for local images
        source = directory if local else ''

        reporter = MgReport()
        inq = Queue()
        outq = Queue()

        # Load the queue for processing
        for card_tupple in input_array:
            inq.put(MgQueueCar(card_tupple))

        # The page creation thread (only one should be created)
        page_thread = MgImageCreateThread(
            outq, self.dpi, self.wh, self.xy, directory,
            file_name, reporter, self.logger
        )
        page_thread.start()

        image_getters = []
        for _ in xrange(IMAGE_GET_THREAD):
            image_thread = MgGetImageThread(
                inq, outq, source, reporter, self.logger
            )
            image_thread.start()
            image_getters.append(image_thread)

            # Add stop signal for each queue created
            inq.put(MgQueueCar())

        self.waitForThread(image_getters)

        # Stop page_thread
        outq.put(MgQueueCar())
        self.waitForThread(page_thread)

    def waitForThread(self, thread):
        '''Blocks until the threads have finished. Takes instance or list.

        I've chosen to wait for the thread to finish, rather than for the queue
        to empty. A thread will finish correctly or if an exception is thrown.
        Unhandled exceptions can easily results in the queue never empying
        and causing the program to stall.'''
        try:
            # Test if list
            iter(thread)
        except TypeError:
            thread.join()
        else:
            for t in thread:
                t.join()

    def createFromWeb(self, input_array, directory, file_name):
        '''Wrapper function to run image creation from web-based image files.'''
        return self.create(False, input_array, directory, file_name)

    def createFromLocal(self, input_array, directory, file_name):
        '''Wrapper function to run image creation from local files.'''
        return self.create(True, input_array, directory, file_name)
