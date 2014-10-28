'''Tests that the logging calls behave properly'''
import unittest
import logging.config
import os.path

from src.logger_dict import MG_LOGGER, MG_LOGGER_CONST
from src.mg_proxy_creator import main

# If testfixtures in not available, skip these tests
SKIP_TEST = False
try:
    from testfixtures import LogCapture
except ImportError:
    SKIP_TEST = True


@unittest.skipIf(SKIP_TEST, 'Testfixtures module not found')
class LoggerTests(unittest.TestCase):
    '''Test if MgProxy correctly logs messages to console'''

    @classmethod
    def setUpClass(cls):
        '''Sets up the logger once before the test_functions are called'''
        logging.config.dictConfig(MG_LOGGER)

    def setUp(self):
        '''For each test a new LogCapture instance is called'''
        self.log_capt = LogCapture(MG_LOGGER_CONST['base_name'])

    def tearDown(self):
        '''Simply uninstalls the log capture instance (warning otherwise)'''
        self.log_capt.uninstall()

    def test_empty_file(self):
        '''Tests the log output for an empty file'''
        # sys.argv always returns a list, so I need to supply a list
        main([self.helper_file_path('empty_input.txt')])
        self.log_capt.check(
            (MG_LOGGER_CONST['base_name'], 'INFO', 'MgProxy is doing its thing!'),
        )

    def helper_file_path(self, file_name):
        '''Return the relative file path from the module root'''
        base_path = 'test/files'
        return os.path.join(base_path, file_name)

if __name__ == '__main__':
    unittest.main()
