'''Specifies the logger and logger functions used for this application'''
import inspect

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


def getLoggerName(function):
    '''Takes a function and returns the logger name for this function.

    Combined the name of the base logger, the module, and the function name
    (seperated by dots) to get the logger name.
    '''
    name = (
        MG_LOGGER_CONST['base_name'] + '.' +
        inspect.getmodule(function).__name__ + '.' + function.__name__
    )

    return name
