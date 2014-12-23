import urllib
import urllib2
import sys
import os
import functools

from StringIO import StringIO
from src.constants import MgException, MgNetworkException, TIMEOUT
from src.constants import BASE_URL
from src.logger_dict import MG_LOGGER_CONST
from urlparse import urljoin

# See create address for reason for duplicate import
import src.constants

try:
    from PIL import Image
except ImportError:
    sys.stderr.write(
        'Cannot run program. ' +
        'Python Pillow (preferred) or PIL module is required.'
    )
    sys.exit()


'''This is a module specific constant used for testing purposes.

It can be passed specific keywords to cause different addresses to be returned
by createAddress function (through the AddressErrorDecorator. See the
decorator for specific strings that can be supplied. It is a list as I want
a mutable object that can be easily changed in the test module.
'''
ADDRESS_ERROR = []


def getGenericData(address, content_type, timeout=TIMEOUT):
    '''Get data of content_type from address.

    Raises MgNetworkException is data cannot be downloaded or if the
    content_type does not match.
    '''
    try:
        response = urllib2.urlopen(address, timeout=timeout)
    except urllib2.HTTPError as e:
        raise MgNetworkException(
            MG_LOGGER_CONST['html_error'] % (e.code, address)
        )
    except urllib2.URLError as e:
        raise MgNetworkException(
            MG_LOGGER_CONST['network_error'] % (address, e.reason)
        )

    response_content_type = response.info().getheader('Content-Type')
    if response_content_type != content_type:
        raise MgNetworkException(
            MG_LOGGER_CONST['ct_error'] %
            (content_type, response_content_type, address)
        )

    file_size = int(response.info().getheader('Content-Length'))
    return response.read(file_size)


def addressErrorDecorator(f):
    '''Decorates the createAddress function and causes errors for testing.

    It takes the module constant ADDRESS_ERROR and if the list has one element
    this decorator returns an address that will cause a loggable error.
    '''

    @functools.wraps(f)
    def change_address(card_name, set_name=None, *args, **kwargs):
        '''Here we decorate the function to return invalid addresses'''
        if ADDRESS_ERROR:
            if ADDRESS_ERROR[0] == 'timeout':
                # Cause a timeout address by adding port 81
                timeout_address = 'http://mtgimage.com:81/'
                return f(card_name, set_name, timeout_address)

        # returns unchaged function call if ADDRESS_ERROR is empty
        return f(card_name, set_name, *args, **kwargs)

    return change_address


@addressErrorDecorator
def createAddress(card_name, set_name=None, return_url=BASE_URL):
    '''Creates a URL from a card name and an optional set.
    Correctly escapes characters.'''

    if set_name:
        if len(set_name) < 4:
            set_url_dir = 'set/'
        else:
            set_url_dir = 'setname/'

        return_url = urljoin(return_url, set_url_dir)

        set_name = set_name + '/'
        return_url = urljoin(return_url, set_name)
    else:
        return_url = urljoin(return_url, 'card/')

    # CARD_EXT can be changed (important for test_logging)
    hq_card_name = urllib.quote(card_name + src.constants.CARD_EXT)
    return urljoin(return_url, hq_card_name)


def getMgImage(card_name, set_name=None):
    '''Downloads a given card name and returns the Pillow image.

    Note that this function does not check if the downloaded image is a
    valid image file.'''
    address = createAddress(card_name, set_name)
    image_stream = getGenericData(address, 'image/jpeg')
    image_stream = StringIO(image_stream)

    return Image.open(image_stream)


def createLocalAddress(directory, card_name):
    '''Create a valid local address from a directory, a card name, extension'''
    return os.path.join(directory, card_name)


def getLocalMgImage(directory, card_name):
    address = createLocalAddress(directory, card_name)

    try:
        card_image = Image.open(address)
    except IOError:
        raise MgException('Cannot open local card image file')
    else:
        return card_image


def validateImage(image):
    '''Checks if PIL image is valid.

    PIL does not provide a good way to test if an image is corrupt.
    The easiest way is to load the image into memory and catch the IOError'''
    try:
        image.load()
    except IOError:
        raise MgException('Image file is corrupt')
