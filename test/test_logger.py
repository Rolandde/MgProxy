'''Tests that the logging calls behave properly'''
import unittest
import logging
import logging.config
import os.path

from src.logger_dict import MG_LOGGER, MG_LOGGER_CONST, logCardName
from src.mg_proxy_creator import main, getFileNamePath, parseFile
from src.get_image import createAddress, ADDRESS_ERROR
from src.create_page import MgImageCreator
from src.mg_thread import MgQueueCar, MgGetImageThread
import src.constants as CON

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
        # The logger itself
        self.logger = logging.getLogger(MG_LOGGER_CONST['base_name'])

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
            if f.startswith('delete'):
                os.remove(os.path.join(base_path, f))

    def testEmptyFile(self):
        '''Tests the log output for an empty file'''
        file_path = self.helperFilePath('empty_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        main([file_path])
        log_list = self.helperLogTemplate(file_path, 0, 0, 0)
        self.log_capt.check(*log_list)

    def testCorrectFile(self):
        '''Tests syntatically correct files where all cards exist'''
        file_path = self.helperFilePath('good_input.txt')

        # sys.argv always returns a list, so I need to supply a list
        # The saved jpgs will be called delete.jpg (deleted by tearDown)
        main([file_path, '-f', 'delete'])
        log_list = self.helperLogTemplate(
            file_path, 4, 1, 0,
            self.logCardPaste((None, 2, None, 'Swamp')),
            self.logCardPaste((None, 2, 'M10', 'Forest'))
        )

        self.log_capt.check(*log_list)

    def testBadParse(self):
        '''Test various versions of bad parse'''
        file_path = self.helperFilePath('bad_parse_input.txt')
        f = open(file_path, 'rU')
        parseFile(f)

        self.log_capt.check(
            self.logBadParse('Forest'),
            self.logBadParse('[M10] Forest'),
            self.logBadParse('SB: Forest'),
            self.logBadParse('A Forest'),
            self.logBadParse('2'),
            self.logBadParse('SB: 2'),
            self.logBadParse('2Forest'),
            self.logBadParse('SB: 1[M10] Forest'),
        )

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

        creator = self.helperInitGetImage()
        creator.getMgImageFromWeb(MgQueueCar((None, 10, None, 'Swamp')))
        creator.getMgImageFromWeb(MgQueueCar(('SB:', '1', 'M10',  'Forest')))

        self.log_capt.check(
            self.logNetworkError(
                (None, 10, None, 'Swamp'),
                createAddress('Swamp', None)
            ),
            self.logNetworkError(
                ('SB:', 1, 'M10', 'Forest'),
                createAddress('Forest', 'M10')
            )
        )

    def testCard404(self):
        '''Test for non-existant cards'''
        creator = self.helperInitGetImage()
        creator.getMgImageFromWeb(MgQueueCar((None, 10, None, 'ForestXXX')))
        creator.getMgImageFromWeb(MgQueueCar(('SB:', 1, 'XXX', 'Swamp')))

        self.log_capt.check(
            self.logCard404((None, 10, None, 'ForestXXX')),
            self.logCard404(('SB:', 1, 'XXX', 'Swamp'))
        )

    def testBadContentType(self):
        '''Tests logging for bad content type'''
        # Causes the content type error by returning html address
        ADDRESS_ERROR.append('content_type')

        creator = self.helperInitGetImage()
        creator.getMgImageFromWeb(MgQueueCar((None, 10, None, 'Swamp')))
        creator.getMgImageFromWeb(MgQueueCar(('SB:', '1', 'M10',  'Forest')))

        self.log_capt.check(
            self.logBadTypeContent(
                (None, 10, None, 'Swamp'),
                'image/jpeg', 'text/html; charset=utf-8'
            ),
            self.logBadTypeContent(
                ('SB:', 1, 'M10', 'Forest'),
                'image/jpeg', 'text/html; charset=utf-8'
            )
        )

    def testBadSave(self):
        '''Test logging of save location that does not exist'''
        creator = self.helperInitMgCreator()
        bad_path = '/does/not/exist'
        file_name = 'page'
        saved_file_name = 'page0.jpg'

        creator.save(bad_path, file_name)
        self.log_capt.check(
            self.logBadSave(bad_path, saved_file_name)
        )

    def helperInitMgCreator(self):
        '''Creates an instance of the MgImageCreator class'''
        return MgImageCreator(
            CON.DPI, (CON.WIDTH, CON.HIGHT),
            (CON.PAGE_X, CON.PAGE_Y), self.logger
        )

    def helperInitGetImage(self):
        '''Creates an instance of the MgGetImageThread class.

        As the thread will never be run and only used to call
        getMgImageFromWeb, none of the init variables except the logger
        need to be supplied.
        '''
        return MgGetImageThread(None, None, None, None, self.logger)

    def helperFilePath(self, file_name):
        '''Return the relative file path from the module root'''
        base_path = 'test/files'
        return os.path.join(base_path, file_name)

    def helperLogTemplate(self, file_path, cards, pages, errors, *args):
        '''Creates the boiler blate logging calls'''
        log_list = [self.logStart()]

        if file_path:
            log_list.append(self.logSave(file_path))

        if args:
            log_list = log_list + list(args)

        log_list.append(self.logTotal(cards, pages, errors))

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
        directory, file_name = getFileNamePath(file_path)
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['save_loc'] % directory
        )

    def logBadSave(self, invalid_path, file_name):
        full_path = os.path.join(invalid_path, file_name)
        return (
            MG_LOGGER_CONST['base_name'], 'ERROR',
            MG_LOGGER_CONST['save_fail'] % (
                full_path,
                'No such file or directory'
            )
        )

    def logTotal(self, card_numb, page_numb, errors):
        '''Returns log message stating card number pasted across numb pages'''
        return (
            MG_LOGGER_CONST['base_name'], 'INFO',
            MG_LOGGER_CONST['final_msg'] % (card_numb, page_numb, errors)
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
