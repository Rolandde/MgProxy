'''Tests that the logging calls behave properly'''
import unittest
from .src.logger_dict import MG_LOGGER, MG_LOGGER_CONST, getLoggerName

# If testfixtures in not available, skip these tests
SKIP_TEST = False
try:
    from testfixtures import LogCapture
except ImportError:
    SKIP_TEST = True


@unittest.skipIf(SKIP_TEST, 'Testfixtures module not found')
class LoggerTests(unittest.TestCase):
    '''Test if MgProxy correctly logs messages to console'''

    def setUp(self):
        self.log_capt = LogCapture(MG_LOGGER_CONST['base_name'])


    def test_delete(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
