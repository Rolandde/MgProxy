import re
import os.path
import sys

from .create_page import MgImageCreator
from .constants import MgException
from .argv_input import arg_parser

import logging
import logging.config
from .logger_dict import MG_LOGGER


def parseLine(line):
    '''Parses input lines for card information.
    Expects the following format: ['SB:'] int [SET: three char code] card name.
    Brackets denote optional info. A four element list is returned, with the
    four fields. If the optional ones are not specified, None is the value.

    TODO: Rather then returning a list, it might be better to return a
    dictionary for legibilities sake. DAVE WAS HERE!
    '''
    match = re.match(r'^\s*(?:(SB:)\s+)?(\d+)\s+(?:\[(\w*)\]\s+)?(.*)$', line)

    if match is None:
        raise MgException('Could not parse MWS line')

    # Tupple is immutable, so conversion into a list
    parsed = list(match.groups())

    if parsed[1] is None:
        raise MgException('Could not parse integer representing card number')

    if parsed[3] is None:
        raise MgException('Could not parse the card name')

    parsed[1] = int(parsed[1])

    return parsed


def parseFile(file_path):
    '''Parses a MWS file, ignoring comment and empty lines. Returns tupple with
    two elements: a list of valid and invalid lines.'''
    valid_list = []
    invalid_lines = []
    f = open(file_path, 'rU')

    for line in f:
        # Ignore lines that are whitespace only or start with //
        if not (line.isspace() or re.match(r'^\s*//', line)):
            try:
                valid_list.append(parseLine(line))
            except MgException as e:
                invalid_lines.append((line, str(e)))

    return (valid_list, invalid_lines)


def splitFile(file_path):
    '''Takes a file path and returns (directory, file_name) tupple.
    The file_name will be an empty string if only a directory path is given.'''
    abs_path = os.path.abspath(file_path)  # In case relative path is provided
    directory, file_name = os.path.split(abs_path)
    # Removes any extension in the filename
    file_name = os.path.splitext(file_name)[0]
    return (directory, file_name)


def errorLog(msg):
    '''Prints out error message to the error stream.
    Expects a list of two element tupples: the offending line and the reason'''
    if len(msg) > 0:
        sys.stderr.write('Errors caused certain pictures to be exluded:\n')

    for message in msg:
        to_write = message[0].strip() + ': ' + message[1].strip() + '\n'
        sys.stderr.write(to_write)


def createMainLogger():
    '''Creates the main logger used in MgProxy'''
    logging.config.dictConfig(MG_LOGGER)


def createFromWebOrLocal(parsed_input):
    '''Takes parsed input from arg_parser and shunts it to function'''
    logger = logging.getLogger(
        'mg_logger.mg_proxy_creator.createFromWeborLocal'
    )
    logger.info('MgProxy is doing its thing!')

    file_name = parsed_input['file_name']

    try:
        user_input, invalid_lines = parseFile(file_name)
    except IOError:
        sys.stderr.write('Card file does not exist')
        sys.exit()

    file_path, file_name = splitFile(file_name)

    creator = MgImageCreator(
        parsed_input['dpi'],
        parsed_input['card_dimensions'],
        parsed_input['card_number'])

    if parsed_input['local_file']:
        invalid_cards = creator.createFromLocal(
            user_input,
            file_path,
            file_name)
    else:
        invalid_cards = creator.createFromWeb(user_input, file_path, file_name)

    errorLog(invalid_lines + invalid_cards)


def main(args=None):
    '''The first function to be run by the program.

    Runs the program, starts the logger, and parses the user command (argparse).
    By default, args is none and parse_argv will use sys.args.
    '''

    # If there are errors or if -h tag is used, program stops at this line
    parsed_input = vars(arg_parser.parse_args(args))
    createMainLogger()
    createFromWebOrLocal(parsed_input)
