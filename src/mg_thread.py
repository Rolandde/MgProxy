'''This module houses code that will drive the thread based part of MgProxy'''

from threading import Lock, Thread
import os

from src.get_image import getMgImage, getLocalMgImage
from src.constants import MgNetworkException, MgImageException
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
        self, in_queue, dpi, wh, xy, directory, file_name,
        reporter, logger=None
    ):
        super(MgImageCreateThread, self).__init__()
        self.in_queue = in_queue
        self.dpi = dpi
        self.wh = wh
        self.xy = xy

        self.directory = directory
        self.file_name = file_name

        self.pic_count = 0  # How many pictures on the current page
        self.current_canvas = createCanvas(dpi, wh, xy)

        self.logger = logger
        self.reporter = reporter

        self.save_threads = []

    def run(self):
        '''The main loop of the MgImageCreateThread.

        Takes the image off the queue, pastes it onto the canvas, and
        spawns a save thread when the canvas is full.
        '''
        while True:
            queue_car = self.in_queue.get()
            if queue_car.end_thread:
                if self.pic_count > 0:
                    self.save(self.current_canvas)

                # Wait for all save threads to end
                for save in self.save_threads:
                    save.join()

                self.in_queue.task_done()
                break

            queue_car.image = resizeImage(queue_car.image, self.dpi, self.wh)
            card_tupple = queue_car.input_tupple

            self.pasteMulti(queue_car.image, card_tupple[1])
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

    def pasteMulti(self, image, number):
        '''Pastes the provided image the specified number of times, saving the
        canvas as required.'''
        for _ in xrange(0, number):
            self.paste(image)

            if self.pic_count == self.xy[0] * self.xy[1]:
                self.save(self.current_canvas)

    def save(self, canvas):
        '''Starts a thread to save the images and resets counters and canvas'''
        save_thread = Thread(
            target=self.saveFunc,
            args=(canvas, self.pic_count)
        )
        self.save_threads = [t for t in self.save_threads if t.isAlive()]
        self.save_threads.append(save_thread)
        save_thread.start()

        self.current_canvas = createCanvas(self.dpi, self.wh, self.xy)
        self.pic_count = 0

    def saveFunc(self, canvas, cards_on_page):
        '''Saves the file_name to the directory.

        It is spawned off as a seperate thread due to its I/O nature.
        '''
        page_number = self.reporter.addPage()

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

    def logError(self, message):
        '''Logs an error message if a logger has been provided'''
        if self.logger:
            self.logger.error(message)

    def logInfo(self, message):
        '''Logs an info message if a logger has been provided'''
        if self.logger:
            self.logger.info(message)
