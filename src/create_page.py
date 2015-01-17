from Queue import Queue

from src.mg_thread import (MgReport, MgGetImageThread, MgImageCreateThread,
                           MgSaveThread, MgQueueCar)
from src.constants import (IMAGE_GET_THREAD, PAGE_SAVE_THREAD, MAX_IMAGE_QUEUE,
                           MAX_PAGE_QUEUE)

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
        Pages will be saved to directory with file_name.

        Creates three serial Queue chains linking the three created thread
        groups. First thread group downloads the images from the web,
        passed them to the thread that creates the printable page, which
        in turn is passed to the thread group that saves the page to hard disk.
        '''

        # source is an empty string for web, directory for local images
        source = directory if local else ''

        reporter = MgReport()
        card_input = Queue()
        image_queue = Queue(MAX_IMAGE_QUEUE)
        canvas_queue = Queue(MAX_PAGE_QUEUE)

        # Create the threads responsible for saving pages
        save_thread = self.startThread(
            MgSaveThread, PAGE_SAVE_THREAD,
            canvas_queue, directory, file_name, reporter, self.logger
        )

        # The page creation thread (only one should be created)
        page_thread = self.startThread(
            MgImageCreateThread, 1,
            image_queue, canvas_queue, self.dpi, self.wh, self.xy,
            reporter, self.logger
        )

        # The image getter threads are started (the first step in the queue)
        image_getters = self.startThread(
            MgGetImageThread, IMAGE_GET_THREAD,
            card_input, image_queue, source, reporter, self.logger
        )

        # Load the first queue for processing. Initiates the Queue chain.
        for card_tupple in input_array:
            card_input.put(MgQueueCar(card_tupple))

        # Once the Queue chain has been started, the stop signals can be sent
        # Stop the image_getter threads (once all images have been downloaded)
        self.stopAndWaitForThread(image_getters, card_input)

        # Stop and wait for page_thread to finish
        self.stopAndWaitForThread(page_thread, image_queue)

        # Stop and wait for save_threads to finish
        self.stopAndWaitForThread(save_thread, canvas_queue)

    def startThread(self, thread, number, *args, **kwargs):
        '''Starts a defined number of threads and returns list

        Arguements to thread instance can be passed via args and kwargs.
        '''
        threads_started = []
        for _ in xrange(number):
            new_thread = thread(*args, **kwargs)
            new_thread.start()
            threads_started.append(new_thread)

        return threads_started

    def stopAndWaitForThread(self, thread_list, thread_queue):
        '''Stops the threads in the list and waits for them to finish.

        Note that is does not mattr if any of the threads have unexpectatly
        ended, as waitForThread accounts for that.
        '''
        for thread in thread_list:
            thread_queue.put(MgQueueCar())

        self.waitForThread(thread_list)

    def waitForThread(self, thread):
        '''Blocks until the threads have finished. Takes instance or list.

        I've chosen to wait for the thread to finish, rather than for the queue
        to empty. A thread will finish correctly or if an exception is thrown.
        Unhandled exceptions can easily results in the queue never empying
        and causing the program to stall.'''
        try:
            # Test if list of threads
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
