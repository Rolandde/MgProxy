'''Specifies the logger and logger functions used for this application'''

MG_LOGGER = {
    'version': 1,
    'disable_existing_loggers': True,

    'handlers': {
        'info_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            # See https://docs.python.org/2/library/
            # logging.config.html#logging-config-dict-externalobj
            'stream': 'ext://sys.stdout'
        }
    },

    'loggers': {
        'mg_logger': {
            'handlers': ['info_console'],
            'level': 'INFO'
        }
    }
}


MG_LOGGER_CONST = {
    # The name of the default logger
    'base_name': 'mg_logger',

    # The program has started
    'start_prog': 'MgProxy is doing its thing!',

    # The directory where the files are saved to
    'save_loc': 'Files will be saved in %s',

    # Final message summarizing number of cards, pages, and errors
    'final_msg': (
        'Summary: %d card(s) pasted across %d page(s) with %d error(s).'
    ),

    # Info message that card has been successfully added
    'good_paste': '%d repeat(s) of %s successfully added.',

    # Failed to parse input line
    'bad_parse': 'Could not parse MWS line: %s',

    # Cannot open input file
    'bad_input': 'Could not open input file: %s',

    # Timeout error getting a card from the network
    'network_error': (
        'Could not connect to %s. Reason: %s.'),

    # Error message for HTML code when it is not 200
    'html_error': 'Unexpected HTML status code %d for %s',

    # Error message for unexpected content type of HTML response
    'ct_error': 'Expected Content-Type %s. Received %s instead from %s',

    # Failed card download (second placeholder is the reason)
    'card_error': 'Could not download %s. %s',

    # Failed to open image file
    'image_file_error': 'Could not open image for card %s. Reason: %s.',

    # Local database copy could not be found
    'image_database_error': 'Card could not be found in local database',

    # Failed to save file to specified path
    'save_fail': 'Could not save page as %s. Reason: %s.'
}


def logCardName(card_input):
    '''Takes a tuple of card_input and returns a stardard string for logging'''
    if card_input[2]:
        return '[%s] %s' % (card_input[2], card_input[3])
    else:
        return card_input[3]
