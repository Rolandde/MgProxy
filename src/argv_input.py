import argparse
from .constants import DPI, WIDTH, HIGHT, PAGE_X, PAGE_Y

arg_parser = argparse.ArgumentParser(
	description='Create printer friendly constructed decks or random boosters (not implemented yet) for Magic the Gathering',
	epilog='The Pillow module is required for this program to work'
)

arg_parser.add_argument(
	'-c', '--constructed_deck', 
	required=True,
	help = 'File path containing cards in the following format: [SB:] card_number [set] card_name',
	metavar='file_path',
	type=str 
	)
	
arg_parser.add_argument(
	'--dpi',
	help = 'Specify the dpi (pixels per inch) for printing. Default: 300dpi',
	default = DPI,
	type = int
)

arg_parser.add_argument(
	'-x', '--card_dimensions',
	help = 'The dimensions (in inches) of the cards, width by hight. Default: 2.49 3.49.',
	nargs = 2,
	type = int,
	default = [WIDTH, HIGHT],
	metavar = 'inch'
)

arg_parser.add_argument(
	'-n', '--card_number',
	help = 'The number of cards going across and down per page. Default: 4 and 2.',
	nargs = 2,
	type = int,
	default = [PAGE_X, PAGE_Y],
	metavar = 'int'	
)

arg_parser.add_argument