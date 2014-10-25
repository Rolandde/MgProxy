'''Tests that the logging calls behave properly'''
import unittest

# If testfixtures in not available, skip these tests
SKIP_TEST = False
try:
    import testfixtures
except ImportError:
    SKIP_TEST = True


@unittest.skipIf(SKIP_TEST, 'Testfixtures module not found')
class LoggerTests(unittest.TestCase):
    '''Test if MgProxy correctly logs messages to console'''

    def test_delete(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
