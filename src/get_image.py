import urllib.request
import urllib.parse
import urllib.error
import sys
import os
import functools
import socket
import random

from io import BytesIO
from contextlib import closing

from src.constants import (
    MgNetworkException, MgImageException, MgLookupException,
    BASE_URL, TIMEOUT, CARD_URLS
)
from src.logger_dict import MG_LOGGER_CONST

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

    Raises exception if data cannot be downloaded or if the
    content_type does not match.

    I've moved the whole code in the try block as urllib2 is known to cause
    leaky exceptions. I've personally seen the read call cause an
    undocumented socket.timeout exception to be thrown.
    '''
    try:
        with closing(
            urllib.request.urlopen(address, timeout=timeout)
        ) as response:
            response_content_type = response.info()['Content-Type']
            if response_content_type != content_type:
                raise MgNetworkException(
                    MG_LOGGER_CONST['ct_error'] %
                    (content_type, response_content_type, address)
                )

            file_size = int(response.info()['Content-Length'])
            return response.read(file_size)

    except urllib.error.HTTPError as e:
        raise MgNetworkException(
            MG_LOGGER_CONST['html_error'] % (e.code, address)
        )
    except (urllib.error.URLError) as e:
        raise MgNetworkException(
            MG_LOGGER_CONST['network_error'] % (address, e.reason)
        )
    except socket.timeout as e:
        raise MgNetworkException(
            MG_LOGGER_CONST['network_error'] % (address, str(e))
        )


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
            elif ADDRESS_ERROR[0] == 'content_type':
                # Returns text/html data rather than jpeg or json
                return 'http://mtgimage.com/'

        # returns unchaged function call if ADDRESS_ERROR is empty
        return f(card_name, set_name, *args, **kwargs)

    return change_address


@addressErrorDecorator
def createAddress(card_name, set_name=None, return_url=BASE_URL):
    '''Creates a URL from a card name and an optional set.
    Correctly escapes characters.'''

    try:
        card_urls = CARD_URLS[card_name]

        if set_name is None:
            url = random.choice(list(card_urls.values()))
        else:
            url = card_urls[set_name]

        # In case there are multiple cards in a set with  same name (basic land)
        url = random.choice(url)
    except KeyError:
        raise MgLookupException(MG_LOGGER_CONST['image_database_error'])

    final_url = BASE_URL + url
    return final_url


def getMgImage(card_name, set_name=None):
    '''Downloads a given card name and returns the Pillow image.

    Note that this function does not check if the downloaded image is a
    valid image file.'''
    address = createAddress(card_name, set_name)
    image_stream = getGenericData(address, 'image/jpeg')
    with closing(BytesIO(image_stream)) as image_stream:
        return openAndValidateImage(image_stream)


def createLocalAddress(directory, card_name):
    '''Create a valid local address from a directory, a card name, extension'''
    return os.path.join(directory, card_name)


def getLocalMgImage(directory, card_name):
    '''Returns an image found on a local disk'''
    address = createLocalAddress(directory, card_name)

    return openAndValidateImage(address)


def openAndValidateImage(image_file):
    '''Opens and checks if PIL image is valid.

    PIL does not provide a good way to test if an image is corrupt.
    The easiest way is to load the image into memory and catch the IOError.
    Inability to open file or corrupt file will raise IOError.
    '''
    try:
        image = Image.open(image_file)
        image.load()
    except IOError as e:
        raise MgImageException(str(e))

    return image
