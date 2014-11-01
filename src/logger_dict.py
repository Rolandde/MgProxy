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

    # Final message summarizing number of images paster and files created
    'final_msg': 'Summary: %d card(s) pasted across %d page(s).',

    # Info message that card has been successfully added
    'good_paste': '%d copies of %s successfully added.'
}
