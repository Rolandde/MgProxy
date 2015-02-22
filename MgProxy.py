import sys
if sys.version_info[0] != 3:
    sys.stderr.write(
        'MgProxy only works with Python 3\n' +
        'Clone the Py2.7_master branch for Python2 support\n'
    )
    sys.exit()

import logging
import logging.config
from src.logger_dict import MG_LOGGER

from src.mg_proxy_creator import main

if __name__ == "__main__":
    '''Run the main program and initiate the logger.'''
    logging.config.dictConfig(MG_LOGGER)
    main()
