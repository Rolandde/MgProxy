'''This module houses code that will drive the thread based part of MgProxy'''

from threading import Lock, Thread
import os

from src.get_image import getMgImage, getLocalMgImage
from src.constants import (
    MgNetworkException, MgImageException, MgLookupException
)
from src.logger_dict import MG_LOGGER_CONST, logCardName
from src.image_manip import createCanvas, pasteImage, resizeImage


class MgQueueCar(object):

    '''This object is passed between the various queues.

    This allows for a standardized way of accessing objects passed by queues.
    '''

    def __init__(self, input_tupple=None):
        self.input_tupple = input_tupple

        # If no input_tupple is supplied, the thread should end
        self.end_thread = True if input_tupple is None else False

        # The image to be pasted
        self.image = None

        # How many cards are on the image to be saved
        self.card_number = None


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
        '''Adds a page and returns the page count before addition'''
        with self._lock:
            past_page = self._pages
            self._pages += 1
            return past_page

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

    @property
    def cards(self):
        with self._lock:
            return self._cards

    @property
    def errors(self):
        with self._lock:
            return self._errors


class MgGetImageThread(Thread):

    '''A queue based thread for downloading and passing on MG images.

    The In-Queue accepts the standard parsed tupple (SB, Card#, Set, Name),
    downloads the image and passes it off to the Out-Queue. In addition,
    optional thread-safe logging and report objects can be passed to init.
    By default, gets the images from the web. Provide directory of local images
    to get images from local folder.
    '''

    def __init__(
        self, in_queue, out_queue, local, reporter, logger=None
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
            queue_car = self.in_queue.get()
            if queue_car.end_thread:
                self.in_queue.task_done()
                break

            if self.local:
                self.getImageFromDisk(self.local, queue_car)
            else:
                self.getMgImageFromWeb(queue_car)

            self.in_queue.task_done()

    def getMgImageFromWeb(self, queue_car):
        '''Download the image from the web and puts it in Out-Queue.'''
        card_tupple = queue_car.input_tupple
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
        except MgLookupException as reason:
            self.logError(str(reason) + ': ' + logCardName(card_tupple))
        else:
            queue_car.image = image
            self.out_queue.put(queue_car)

    def getImageFromDisk(self, directory, queue_car):
        '''Get image from local disk and put it in the Out-Queue.'''
        card_tupple = queue_car.input_tupple
        card_name = card_tupple[3]

        try:
            image = getLocalMgImage(directory, card_name)
        except MgImageException as reason:
            self.logError(MG_LOGGER_CONST['image_file_error'] % (
                logCardName(card_tupple),
                reason
            ))
        else:
            queue_car.image = image
            self.out_queue(queue_car)

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
        self, in_queue, out_queue, dpi, wh, xy, reporter, logger=None
    ):
        super(MgImageCreateThread, self).__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.dpi = dpi
        self.wh = wh
        self.xy = xy

        self.pic_count = 0  # How many pictures on the current page
        self.current_canvas = createCanvas(dpi, wh, xy)

        self.logger = logger
        self.reporter = reporter

    def run(self):
        '''The main loop of the MgImageCreateThread.

        Takes the image off the queue, pastes it onto the canvas, and
        spawns a save thread when the canvas is full.
        '''
        while True:
            queue_car = self.in_queue.get()
            if queue_car.end_thread:
                if self.pic_count > 0:
                    # Stop signals should not be passed down the queue
                    queue_car.end_thread = False
                    self.save(queue_car, self.current_canvas)

                self.in_queue.task_done()
                break

            resized_image = resizeImage(queue_car.image, self.dpi, self.wh)

            # Explicitly close original image to release memory
            queue_car.image.close()
            queue_car.image = resized_image

            card_tupple = queue_car.input_tupple

            self.pasteMulti(queue_car)
            log_msg = logCardName(card_tupple)
            self.logInfo(
                MG_LOGGER_CONST['good_paste'] % (card_tupple[1], log_msg)
            )

            self.in_queue.task_done()

    def paste(self, image):
        '''Pastes the image into the next slot on the canvas.
        TODO: This should throw an exception if there are no more free spaces.
        TODO: Make the xy variable calculation a lot more readable.
        '''
        xy = (
            self.pic_count % self.xy[0],
            int(round(self.pic_count/self.xy[0], 0))
        )
        pasteImage(self.current_canvas, image, xy)
        self.pic_count += 1

    def pasteMulti(self, queue_car):
        '''Pastes the provided image the specified number of times, saving the
        canvas as required.'''
        image = queue_car.image
        number = queue_car.input_tupple[1]

        for _ in range(0, number):
            self.paste(image)

            if self.pic_count == self.xy[0] * self.xy[1]:
                self.save(queue_car, self.current_canvas)

        # Explicitly close image after it has been pasted
        image.close()

    def save(self, queue_car, canvas):
        '''Put the newly created canvas on the output Queue.'''
        queue_car.image = canvas
        queue_car.card_number = self.pic_count

        self.out_queue.put(queue_car)

        self.current_canvas = createCanvas(self.dpi, self.wh, self.xy)
        self.pic_count = 0

    def logInfo(self, message):
        '''Logs an info message if a logger has been provided'''
        if self.logger:
            self.logger.info(message)


class MgSaveThread(Thread):

    '''Saves the final page to a specific directory with the given filename.

    Saving is the slowest step in the program, due to the slow I/O nature
    of hard drives. Threading should greatly increase the speed.
    '''

    def __init__(self, in_queue, directory, file_name, reporter, logger=None):
        super(MgSaveThread, self).__init__()
        self.in_queue = in_queue
        self.directory = directory
        self.file_name = file_name
        self.reporter = reporter
        self.logger = logger

    def run(self):
        while True:
            queue_car = self.in_queue.get()
            if queue_car.end_thread:
                self.in_queue.task_done()
                break

            self.saveFunc(queue_car)
            self.in_queue.task_done()

    def saveFunc(self, queue_car):
        '''Saves the file_name to the directory.'''
        page_number = self.reporter.addPage()
        canvas = queue_car.image
        cards_on_page = queue_car.card_number

        new_file_name = str(self.file_name) + str(page_number) + '.jpg'
        file_path = os.path.join(self.directory, new_file_name)
        try:
            canvas.save(file_path)
        except IOError as e:
            self.logError(MG_LOGGER_CONST['save_fail'] % (
                e.filename, e.strerror
            ))
            self.reporter.addError()
        else:
            self.reporter.addCards(cards_on_page)
        finally:
            # Explicitly close image
            canvas.close()

    def logError(self, message):
        '''Logs an error message if a logger has been provided'''
        if self.logger:
            self.logger.error(message)
