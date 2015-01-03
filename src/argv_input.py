import argparse
from src.constants import DPI, WIDTH, HIGHT, PAGE_X, PAGE_Y, ARG_CONST


def addFlag(name):
    '''Adds '--' to name.

    This creates the optional arguments necessary for arg_parse without
    resorting to magical strings.
    '''
    return '--' + name

arg_parser = argparse.ArgumentParser(
    description=('Create printer friendly constructed decks or random ' +
                 'boosters (not implemented yet) for Magic the Gathering'),
    epilog='The Pillow module is required for this program to work')

# Required file name
arg_parser.add_argument(
    ARG_CONST['input_file'],
    help=('File path containing cards in the following format: ' +
          '[SB:] card_number [set] card_name'),
    metavar='input file',
    type=str
    )

# Mutually exclusive arguements
source_of_image = arg_parser.add_mutually_exclusive_group()

source_of_image.add_argument(
    '-w', addFlag(ARG_CONST['web']),
    help='Obtain image from web (Default)',
    action='store_true'
)

source_of_image.add_argument(
    '-l', addFlag(ARG_CONST['local']),
    help='Obtain local image from directory containing file_name',
    action='store_true'
)

# Optional arguements
arg_parser.add_argument(
    '-r', addFlag(ARG_CONST['dpi']),
    help='Specify the dpi (pixels per inch) for printing. Default: 300dpi',
    default=DPI,
    type=int
)

arg_parser.add_argument(
    '-x', addFlag(ARG_CONST['dimension']),
    help=('The dimensions (in inches) of the cards, width by hight. ' +
          'Default: 2.49 3.49.'),
    nargs=2,
    type=int,
    default=[WIDTH, HIGHT],
    metavar=('width', 'hight')
)

arg_parser.add_argument(
    '-n', addFlag(ARG_CONST['number']),
    help='The number of cards going across and down a page. Default: 4 and 2.',
    nargs=2,
    type=int,
    default=[PAGE_X, PAGE_Y],
    metavar=('across', 'down')
)

arg_parser.add_argument(
    '-f', addFlag(ARG_CONST['alt_name']),
    help=(
        'Specify the file names of the saved pages. Default is the file name' +
        ' of the input file.'
    ),
    type=str,
    metavar='optional_file_name'
)

arg_parser.add_argument(
    '-p', addFlag(ARG_CONST['opt_path']),
    help=(
        'Specify file path for saved pages. Default is the file path of' +
        ' input file.'
    ),
    type=str,
    metavar='optional_file_path'
)
