'''Tests that the logging calls behave properly'''
import unittest
import logging.config
import os.path

from src.logger_dict import MG_LOGGER, MG_LOGGER_CONST, logCardName
from src.mg_proxy_creator import main, splitFile
from src.get_image import createAddress
from src.get_image import ADDRESS_ERROR

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
        # For each test a new LogCapture instance is called
        self.log_capt = LogCapture(MG_LOGGER_CONST['base_name'])

        # Empties the list (do not want to assign a new empty list)
        del ADDRESS_ERROR[:]

    def tearDown(self):
        # Simply uninstalls the log capture instance (warning otherwise)
        self.log_capt.uninstall()

        # Remove the created jpeg files from the files folder
        base_path = 'test/files'

        filelist = [f for f in os.listdir(base_path) if f.endswith(".jpg")]
        for f in filelist:
            os.remove(os.path.join(base_path, f))

    def test_empty_file(self):
        '''Tests the log output for an empty file'''
        file_path = self.helper_file_path('empty_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helper_log_template(file_path, 0, 0)
        self.log_capt.check(*log_list)

    def test_correct_file(self):
        '''Tests syntatically correct files where all cards exist'''
        file_path = self.helper_file_path('good_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helper_log_template(
            file_path, 4, 1,
            self.log_card_paste((None, 2, None, 'Swamp')),
            self.log_card_paste((None, 2, 'M10', 'Forest'))
        )

        self.log_capt.check(*log_list)

    def test_bad_parse(self):
        '''Test various versions of bad parse'''
        file_path = self.helper_file_path('bad_parse_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helper_log_template(
            file_path, 4, 1,
            self.log_bad_parse('Forest'),
            self.log_bad_parse('[M10] Forest'),
            self.log_bad_parse('SB: Forest'),
            self.log_bad_parse('A Forest'),
            self.log_bad_parse('2'),
            self.log_bad_parse('SB: 2'),
            self.log_bad_parse('2Forest'),
            self.log_bad_parse('SB: 1[M10] Forest'),
            self.log_card_paste((None, 2, None, 'Swamp')),
            self.log_card_paste((None, 2, 'M10', 'Forest'))
        )

        self.log_capt.check(*log_list)

    def test_bad_file(self):
        '''Test logging when input file cannot be accessed'''
        file_path = '/file/does/not/exist'

        main([file_path])
        self.log_capt.check(
            self.log_start(),
            self.log_bad_file(file_path)
        )

    def test_timeout(self):
        '''Test that a timeout is correctly logged'''

        # Set timeout flag (will be reset in setUp)
        ADDRESS_ERROR.append('timeout')

        file_path = self.helper_file_path('good_input.txt')

        main([file_path])
        log_list = self.helper_log_template(
            file_path, 0, 0,
            self.log_timeout(
                (None, 2, None, 'Swamp'),
                createAddress('Swamp', None)
            ),
            self.log_timeout(
                (None, 2, 'M10', 'Forest'),
                createAddress('Forest', 'M10')
            )
        )

        self.log_capt.check(*log_list)

    def helper_file_path(self, file_name):
        '''Return the relative file path from the module root'''
        base_path = 'test/files'
        return os.path.join(base_path, file_name)

    def helper_log_template(self, file_path, cards, pages, *args):
        '''Creates the boiler blate logging calls'''
        log_list = [self.log_start()]

        if file_path:
            log_list.append(self.log_save(file_path))

        if args:
            log_list = log_list + list(args)

        log_list.append(self.log_total(cards, pages))

        return log_list

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

    def log_bad_parse(self, line):
        '''Error message when input line cannot be parsed'''
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['bad_parse'] % line
        )

    def log_bad_file(self, file_path):
        '''Error log when input file does not exist or could not be accessed'''
        return (
            MG_LOGGER_CONST['base_name'], 'CRITICAL',
            MG_LOGGER_CONST['bad_input'] % file_path
        )

    def log_timeout(self, card_input, address):
        '''Error log when website access times out'''
        card_name = logCardName(card_input)
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['timeout_error'] % (card_name, address)
        )

if __name__ == '__main__':
    unittest.main()
