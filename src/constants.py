import sys
import json


class MgException(Exception):
    '''Base Exception class used for this program'''
    pass


class MgNetworkException(MgException):
    '''Thrown if the website cannot be reached.'''
    pass


class MgImageException(MgException):
    '''Thrown if image cannot be opened or manipulated'''
    pass


class MgLookupException(MgException):
    '''Thrown if card cannot be found in local database'''
    pass


DPI = 300  # Default DPI
WIDTH, HIGHT = 2.49, 3.48  # Default card width and hight in inches
PAGE_X, PAGE_Y = 4, 2  # Default number of cards per jpg file
BASE_URL = 'http://magiccards.info/scans/en'  # URL of image database
BASE_URL_JSON = 'http://mtgjson.com/'  # URL of JSON database
JSON_EXT = '.json'  # Extension for json files on mtgjson.com
TIMEOUT = 5  # Timeout (sec) for urllib2.geturl()
IMAGE_GET_THREAD = 3  # Number of threads created to fetch images
PAGE_SAVE_THREAD = 2  # Number of threads created to save pages
MAX_IMAGE_QUEUE = 20  # Max number of images that can be stored in a Queue
MAX_PAGE_QUEUE = 5  # Max number of pages held in Queue

# The options used for args parsing (see src/argv_input)
ARG_CONST = {
    # Input file name
    'input_file': 'input_file',

    # Get images from the web
    'web': 'web_based',

    # Get images from local file
    'local': 'local_file',

    # Specify the DPI
    'dpi': 'dpi',

    # Card dimensions
    'dimension': 'card_dimensions',

    # Card number
    'number': 'card_number',

    # Different file name
    'alt_name': 'opt_file_name',

    # Different file path
    'opt_path': 'opt_file_path'
}

try:
    CARD_URLS = json.load(open('master.json', 'r'))
except IOError:
    sys.stderr.write('Cannot open master.json lookup\n')
    sys.exit()
