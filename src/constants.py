DPI = 300  # Default DPI
WIDTH, HIGHT = 2.49, 3.48  # Default card width and hight in inches
PAGE_X, PAGE_Y = 4, 2  # Default number of cards per jpg file
BASE_URL = 'http://mtgimage.com/'  # URL of image database
BASE_URL_JSON = 'http://mtgjson.com/'  # URL of JSON database
JSON_EXT = '.json'  # Extension for json files on mtgjson.com
TIMEOUT = 0.5  # Timeout (sec) for urllib2.geturl()
CARD_EXT = '.hq.jpg'  # Extension to add to card html address

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


class MgException(Exception):
    '''Base Exception class used for this program'''
    pass


class MgNetworkException(MgException):
    '''Thrown if the website cannot be reached.'''
    pass
