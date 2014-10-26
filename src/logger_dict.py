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
    'base_name': 'mg_logger'
}
