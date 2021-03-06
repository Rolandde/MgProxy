import re
import os.path
import logging

from src.create_page import MgImageCreator
from src.constants import MgException, ARG_CONST
from src.argv_input import arg_parser
from src.logger_dict import MG_LOGGER_CONST

logger = logging.getLogger(MG_LOGGER_CONST['base_name'])


def parseLine(line):
    '''Parses input lines for card information.
    Expects the following format: ['SB:'] int [SET: three char code] card name.
    Brackets denote optional info. A four element list is returned, with the
    four fields. If the optional ones are not specified, None is the value.

    TODO: Rather then returning a list, it might be better to return a
    dictionary for legibilities sake. DAVE WAS HERE!
    '''
    match = re.match(r'^\s*(?:(SB:)\s+)?(\d+)\s+(?:\[(\w*)\]\s+)?(\S.*)$', line)

    if match is None:
        raise MgException(MG_LOGGER_CONST['bad_parse'] % line.strip())

    # Tupple is immutable, so conversion into a list
    parsed = list(match.groups())

    # These two errors should never happen, as re.match should return None
    if parsed[1] is None:
        raise MgException('Could not parse integer representing card number')

    if parsed[3] is None:
        raise MgException('Could not parse the card name')

    parsed[1] = int(parsed[1])

    return parsed


def parseFile(f):
    '''Takes MWS file object and arses it.

    Returns tupple with two elements: a list of valid lines and
    count of invalid lines
    '''
    valid_list = []
    invalid_lines = 0

    for line in f:
        # Ignore lines that are whitespace only or start with //
        if not (line.isspace() or re.match(r'^\s*//', line)):
            try:
                valid_list.append(parseLine(line))
            except MgException as e:
                invalid_lines += 1
                logger.error(str(e))

    return (valid_list, invalid_lines)


def createMgInstance(parsed_input):
    '''Creates an instance of the MgImageCreator class.'''
    return MgImageCreator(
        parsed_input[ARG_CONST['dpi']],
        parsed_input[ARG_CONST['dimension']],
        parsed_input[ARG_CONST['number']],
        logger
        )


def getFileNamePath(file_path, parsed_args=None):
    '''Returns a tupple containing the file path and file name.

    Parsed_args can be used to over-ride the returned values.
    Relative paths will first be converted to absolute paths.
    The file path is where the files will be saved to with their file name.
    The file_name will be an empty string if only a directory path is given.
    '''
    abs_path = os.path.abspath(file_path)  # In case relative path is provided
    directory, file_name = os.path.split(abs_path)
    # Removes any extension in the filename
    file_name = os.path.splitext(file_name)[0]

    if parsed_args is not None:
        alt_file_name = parsed_args[ARG_CONST['alt_name']]
        if alt_file_name is not None:
            file_name = alt_file_name

        alt_file_path = parsed_args[ARG_CONST['opt_path']]
        if alt_file_path is not None:
            directory = os.path.abspath(alt_file_path)

    return (directory, file_name)


def createFromWebOrLocal(parsed_input):
    '''Takes parsed input from arg_parser and shunts it to function'''
    logger.info(MG_LOGGER_CONST['start_prog'])

    full_path = parsed_input[ARG_CONST['input_file']]
    try:
        with open(full_path, 'r') as f:
            file_path, file_name = getFileNamePath(full_path, parsed_input)
            logger.info(MG_LOGGER_CONST['save_loc'] % file_path)

            user_input, invalid_lines = parseFile(f)

            creator = createMgInstance(parsed_input)

            if parsed_input[ARG_CONST['local']]:
                reporter = creator.createFromLocal(
                    user_input, file_path, file_name
                )
            else:
                reporter = creator.createFromWeb(
                    user_input, file_path, file_name
                )

            errors = invalid_lines + reporter.errors
            logger.info(
                MG_LOGGER_CONST['final_msg'] %
                (reporter.cards, reporter.pages, errors)
            )
    except IOError:
        logger.critical(MG_LOGGER_CONST['bad_input'] % full_path)


def main(args=None):
    '''The first function to be run by the program.

    Runs the program, starts the logger, and parses the user command (argparse).
    By default, args is none and parse_argv will use sys.args.
    '''

    # If there are errors or if -h tag is used, program stops at this line
    parsed_input = vars(arg_parser.parse_args(args))
    createFromWebOrLocal(parsed_input)
