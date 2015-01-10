from Queue import Queue

from src.mg_thread import MgReport, MgGetImageThread, MgImageCreateThread

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

        # source is an empty string for web, otherwise directory
        source = directory if local else ''

        reporter = MgReport()
        inq = Queue()
        outq = Queue()

        # The page creation thread (only one should be created)
        page_thread = MgImageCreateThread(
            outq, self.dpi, self.wh, self.xy, directory,
            file_name, reporter, self.logger
        )
        page_thread.start()

        for _ in xrange(5):
            image_thread = MgGetImageThread(
                inq, outq, source, reporter, self.logger
            )
            image_thread.start()

        for card_tupple in input_array:
            inq.put(card_tupple)

        for _ in xrange(5):
            inq.put(None)
        inq.join()

        outq.put(None)
        outq.join()

    def createFromWeb(self, input_array, directory, file_name):
        '''Wrapper function to run image creation from web-based image files.'''
        return self.create(False, input_array, directory, file_name)

    def createFromLocal(self, input_array, directory, file_name):
        '''Wrapper function to run image creation from local files.'''
        return self.create(True, input_array, directory, file_name)
