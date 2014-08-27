import argparse

parser = argparse.ArgumentParser(
	description='Create printer friendly constructed decks or random boosters (not implemented yet) for Magic the Gathering',
	epilog='The Pillow module is required for this program to work'
)

parser.add_argument(
	'-c', '--constructed_deck', 
	required=True,
	help = 'File path containing cards in the following format: [SB:] card_number [set] card_name',
	metavar='file_path',
	type=str 
	)
	
parser.add_argument(
	'--dpi',
	help = 'Specify the dpi (pixels per inch) for printing. Default: 300dpi',
	default = 300,
	type = int
)

parser.add_argument(
	'-x', '--card_dimensions',
	help = 'The dimensions (in inches) of the cards, width by hight. Default: 2.49 3.49.',
	nargs = 2,
	type = int,
	default = [2.49, 3.49],
	metavar = 'inch'
)

parser.add_argument
	

print vars(parser.parse_args())