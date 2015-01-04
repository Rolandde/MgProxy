import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.stderr.write(
        'Cannot run program. ' +
        'Python Pillow (preferred) or PIL module is required.'
    )
    sys.exit()

from src.get_image import getMgImage, getLocalMgImage, validateImage
from src.constants import MgNetworkException

from src.logger_dict import MG_LOGGER_CONST, logCardName


def createCanvas(dpi, wh, xy):
    '''Creates a blank (white) RGB image canvas.
    Takes the dpi, a tuple of the width/hight of the card, and the number
    of cards per image.
    '''
    X = int(dpi * wh[0] * xy[0])
    Y = int(dpi * wh[1] * xy[1])

    return Image.new('RGB', (X, Y), 'white')


def resizeImage(image, dpi, wh):
    '''Resize an image to have the given width/hight (wh) given the dpi.'''
    new_x = int(dpi * wh[0])
    new_y = int(dpi * wh[1])

    return image.resize((new_x, new_y), Image.ANTIALIAS)


def pasteImage(canvas, image, xy):
    '''Paste an image onto a canvas at specific position.

    XY coordinates are given by increasing positives integers. For
    example (2, 3) would mean the image would be in the second column,
    third row. Correct spacing between the images is guaranteed if the
    pasted images are identical size.
    '''
    canvas.paste(image, (image.size[0]*xy[0], image.size[1]*xy[1]))

    return canvas


class MgImageCreator(object):

    '''Place images onto an object in a regular and cuttable manner.

    An instance of this object is given the dpi, the width/hight of the cards,
    the max number of cards in the xy directions, and an optional logger. Once
    an object of this class is initialized, the create functions can be called
    to create jpgs with the provided cards.
    '''

    def __init__(self, dpi, wh, xy, logger=None):
        self.dpi = dpi
        self.wh = wh
        self.xy = xy

        self.pic_count = 0  # How many pictures on the current page
        self.total_pic = 0  # Total number of pictures pasted
        self.page_count = 0  # How many pages have been saved

        self.current_canvas = createCanvas(dpi, wh, xy)
        self.image = None

        # Store logger is specified (None otherwise)
        self.logger = logger

    def paste(self):
        '''Pastes the image into the next slot on the canvas.
        TODO: This should throw an exception if there are no more free spaces.
        TODO: Make the xy variable calculation a lot more readable.
        '''
        xy = (
            self.pic_count %
            self.xy[0], int(
                round(
                    self.pic_count/self.xy[0], 0)))
        pasteImage(self.current_canvas, self.image, xy)
        self.pic_count += 1

    def pasteMulti(self, number, directory, file_name):
        '''Pastes the provided image the specified number of times, saving the
        canvas as required.'''
        for _ in xrange(0, number):
            self.paste()

            if self.pic_count == self.xy[0] * self.xy[1]:
                self.save(directory, file_name)

    def startNextPage(self, save_success):
        '''Prepares a new blank page for pasting of images.

        It clears the current canvas. If the save was successful,
        updates total pics, resets the pic counter and increases the page count.
        If save fails, resets pic count, but does not count the failed pics.
        '''
        self.current_canvas = createCanvas(self.dpi, self.wh, self.xy)

        if save_success:
            self.total_pic += self.pic_count
            self.page_count += 1

        self.pic_count = 0

    def reset(self):
        '''Returns the instance to the initial state.'''
        # Correctly reset the object so that the instance can be called anew
        self.__init__(self.dpi, self.wh, self.xy, self.logger)

    def create(self, local, name_array, directory, file_name):
        '''Takes a name_array containing the number and name of cards and
        creates images of those cards. Local is a boolean specifying if the
        cards are local or online.

        Returns a list of two element tupples: the name and reason of any cards
        that could not be successfully pasted.
        '''
        for number_name in name_array:
            number, set_name, card_name = number_name[
                1], number_name[2], number_name[3]

            if local:
                success = self.getImageFromDisk(directory, card_name)
            else:
                success = self.getMgImageFromWeb(card_name, set_name)

            if success:
                validateImage(self.image)

            if success:
                self.image = resizeImage(self.image, self.dpi, self.wh)
                self.pasteMulti(number, directory, file_name)
                log_msg = logCardName(number_name)
                self.logInfo(
                    MG_LOGGER_CONST['good_paste'] % (number_name[1], log_msg)
                )

            self.image = None

        if (self.pic_count > 0):
            self.save(directory, file_name)

        self.logInfo(
            MG_LOGGER_CONST['final_msg'] % (self.total_pic, self.page_count)
        )

        return self.reset()

    def getMgImageFromWeb(self, card_name, set_name):
        '''Download the image from the web.

        Return true if no errors were encountered, otherwise returns false
        and logs the errors.
        '''
        try:
            self.image = getMgImage(card_name, set_name)
        except MgNetworkException as reason:
            self.logError(
                MG_LOGGER_CONST['card_error'] % (
                    # logCardName expects a tupple of card info
                    logCardName((None, None, set_name, card_name)),
                    reason
                )
            )
            return False
        else:
            return True

    def getImageFromDisk(self, directory, card_name):
        self.image = getLocalMgImage(directory, card_name)
        return True

    def save(self, directory, file_name):
        '''Saves the file_name to the directory.
        It will alwasy save as a jpg. To prevent overwriting previously saved
        pages, a integer counter is appended at the end of the filename.
        TODO: Maybe give the user the option of specifying the image format.
        '''
        new_file_name = str(file_name) + str(self.page_count) + '.jpg'
        file_path = os.path.join(directory, new_file_name)

        try:
            self.current_canvas.save(file_path)
        except IOError as e:
            self.logError(MG_LOGGER_CONST['save_fail'] % (
                e.filename, e.strerror
            ))
            self.startNextPage(False)
        else:
            self.startNextPage(True)

    def logInfo(self, message):
        '''Logs an info message if a logger has been provided'''
        if self.logger:
            self.logger.info(message)

    def logError(self, message):
        '''Logs an error message if a logger has been provided'''
        if self.logger:
            self.logger.error(message)

    def createFromWeb(self, name_array, directory, file_name):
        '''Wrapper function to run image creation from web-based image files.'''
        return self.create(False, name_array, directory, file_name)

    def createFromLocal(self, name_array, directory, file_name):
        '''Wrapper function to run image creation from local files.'''
        return self.create(True, name_array, directory, file_name)
