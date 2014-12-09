DPI = 300  # Default DPI
WIDTH, HIGHT = 2.49, 3.48  # Default card width and hight in inches
PAGE_X, PAGE_Y = 4, 2  # Default number of cards per jpg file
BASE_URL = 'http://mtgimage.com/'  # URL of image database
BASE_URL_JSON = 'http://mtgjson.com/'  # URL of JSON database
JSON_EXT = '.json'  # Extension for json files on mtgjson.com
TIMEOUT = 0.5  # Timeout (sec) for urllib2.geturl()


class MgException(Exception):

    '''Base Exception class used for this program'''
    pass
