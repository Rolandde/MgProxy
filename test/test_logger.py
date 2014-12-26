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

    def testEmptyFile(self):
        '''Tests the log output for an empty file'''
        file_path = self.helperFilePath('empty_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helperLogTemplate(file_path, 0, 0)
        self.log_capt.check(*log_list)

    def testCorrectFile(self):
        '''Tests syntatically correct files where all cards exist'''
        file_path = self.helperFilePath('good_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helperLogTemplate(
            file_path, 4, 1,
            self.logCardPaste((None, 2, None, 'Swamp')),
            self.logCardPaste((None, 2, 'M10', 'Forest'))
        )

        self.log_capt.check(*log_list)

    def testBadParse(self):
        '''Test various versions of bad parse'''
        file_path = self.helperFilePath('bad_parse_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helperLogTemplate(
            file_path, 4, 1,
            self.logBadParse('Forest'),
            self.logBadParse('[M10] Forest'),
            self.logBadParse('SB: Forest'),
            self.logBadParse('A Forest'),
            self.logBadParse('2'),
            self.logBadParse('SB: 2'),
            self.logBadParse('2Forest'),
            self.logBadParse('SB: 1[M10] Forest'),
            self.logCardPaste((None, 2, None, 'Swamp')),
            self.logCardPaste((None, 2, 'M10', 'Forest'))
        )

        self.log_capt.check(*log_list)

    def testBadFile(self):
        '''Test logging when input file cannot be accessed'''
        file_path = '/file/does/not/exist'

        main([file_path])
        self.log_capt.check(
            self.logStart(),
            self.logBadFile(file_path)
        )

    def testNetworkError(self):
        '''Test that a timeout is correctly logged'''

        # Set timeout flag (will be reset in setUp)
        ADDRESS_ERROR.append('timeout')

        file_path = self.helperFilePath('good_input.txt')

        main([file_path])
        log_list = self.helperLogTemplate(
            file_path, 0, 0,
            self.logNetworkError(
                (None, 2, None, 'Swamp'),
                createAddress('Swamp', None)
            ),
            self.logNetworkError(
                (None, 2, 'M10', 'Forest'),
                createAddress('Forest', 'M10')
            )
        )

        self.log_capt.check(*log_list)

    def testCard404(self):
        '''Test for non-existant cards'''
        file_path = self.helperFilePath('card_error.txt')
        main([file_path])

        log_list = self.helperLogTemplate(
            file_path, 5, 1,
            self.logCardPaste((None, 3, None, 'Swamp')),
            self.logCardPaste((None, 2, 'M10', 'Forest')),
            self.logCard404((None, 4, None, 'SwampX'))
        )

        self.log_capt.check(*log_list)

    def testBadContentType(self):
        '''Tests logging for bad content type'''
        file_path = self.helperFilePath('good_input.txt')

        # Causes the content type error by returning html address
        ADDRESS_ERROR.append('content_type')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helperLogTemplate(
            file_path, 0, 0,
            self.logBadTypeContent(
                (None, 2, None, 'Swamp'),
                'image/jpeg', 'text/html; charset=utf-8'
            ),
            self.logBadTypeContent(
                (None, 2, 'M10', 'Forest'),
                'image/jpeg', 'text/html; charset=utf-8'
            )
        )

        self.log_capt.check(*log_list)

    def helperFilePath(self, file_name):
        '''Return the relative file path from the module root'''
        base_path = 'test/files'
        return os.path.join(base_path, file_name)

    def helperLogTemplate(self, file_path, cards, pages, *args):
        '''Creates the boiler blate logging calls'''
        log_list = [self.logStart()]

        if file_path:
            log_list.append(self.logSave(file_path))

        if args:
            log_list = log_list + list(args)

        log_list.append(self.logTotal(cards, pages))

        return log_list

    def logStart(self):
        '''Returns program start log message tuple for testing purposes'''
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['start_prog']
        )

    def logCardPaste(self, card_input):
        '''Returns log message when a card is succesfully pasted'''
        card_name = logCardName(card_input)
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['good_paste'] % (card_input[1], card_name)
        )

    def logSave(self, file_path):
        '''Returns log message stating the save directory'''
        directory, file_name = splitFile(file_path)
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['save_loc'] % directory
        )

    def logTotal(self, card_numb, page_numb):
        '''Returns log message stating card number pasted across numb pages'''
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['final_msg'] % (card_numb, page_numb)
        )

    def logBadParse(self, line):
        '''Error message when input line cannot be parsed'''
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['bad_parse'] % line
        )

    def logBadFile(self, file_path):
        '''Error log when input file does not exist or could not be accessed'''
        return (
            MG_LOGGER_CONST['base_name'], 'CRITICAL',
            MG_LOGGER_CONST['bad_input'] % file_path
        )

    def logNetworkError(self, card_input, address):
        '''Error log when website access times out'''
        card_name = logCardName(card_input)
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['card_error'] % (
                card_name,
                MG_LOGGER_CONST['network_error'] % (
                    address,
                    '[Errno 111] Connection refused'
                )
            )
        )

    def logCard404(self, card_input):
        '''Error logged when card cannot be downloaded'''
        card_name = logCardName(card_input)
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['card_error'] % (
                card_name,
                MG_LOGGER_CONST['html_error'] % (
                    404,
                    createAddress(card_input[3], card_input[2]))
            )
        )

    def logBadTypeContent(self, card_input, expected, received):
        '''Error logged when file content type is unexpected'''
        card_name = logCardName(card_input)
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['card_error'] % (
                card_name,
                MG_LOGGER_CONST['ct_error'] % (
                    expected, received,
                    createAddress(card_input[3], card_input[2])
                )
            )
        )

if __name__ == '__main__':
    unittest.main()
