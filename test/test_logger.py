'''Tests that the logging calls behave properly'''
import unittest
import logging.config
import os.path

from src.logger_dict import MG_LOGGER, MG_LOGGER_CONST, logCardName
from src.mg_proxy_creator import main, splitFile

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
        file_path = self.helper_file_path('empty_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        self.log_capt.check(
            self.log_start(),
            self.log_save(file_path),
            self.log_total(0, 0)
        )

    def test_correct_file(self):
        '''Tests syntatically correct files where all cards exist'''
        file_path = self.helper_file_path('good_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        self.log_capt.check(
            self.log_start(),
            self.log_save(file_path),
            self.log_card_paste((None, 2, None, 'Swamp')),
            self.log_card_paste((None, 2, 'M10', 'Forest')),
            self.log_total(4, 1)
        )

    def helper_file_path(self, file_name):
        '''Return the relative file path from the module root'''
        base_path = 'test/files'
        return os.path.join(base_path, file_name)

    def log_start(self):
        '''Returns program start log message tuple for testing purposes'''
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['start_prog']
        )

    def log_card_paste(self, card_input):
        '''Returns log message when a card is succesfully pasted'''
        card_name = logCardName(card_input)
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['good_paste'] % (card_input[1], card_name)
        )

    def log_save(self, file_path):
        '''Returns log message stating the save directory'''
        directory, file_name = splitFile(file_path)
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['save_loc'] % directory
        )

    def log_total(self, card_numb, page_numb):
        '''Returns log message stating card number pasted across numb pages'''
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['final_msg'] % (card_numb, page_numb)
        )


if __name__ == '__main__':
    unittest.main()
