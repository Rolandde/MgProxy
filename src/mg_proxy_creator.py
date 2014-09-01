import re
import os.path
import sys

from src.create_page import MgImageCreator
from src.get_image import getMgImage
from src.constants import MgException
from src.argv_input import arg_parser

def parseLine(line):
	'''Expects the following format: ['SB:'] int [SET: three char code] card name. Brackets denote optional info.'''
	match = re.match(r'^\s*(?:(SB:)\s+)?(\d+)\s+(?:\[(\w*)\]\s+)?(.*)$', line)

	if match == None:
		raise MgException('Could not parse MWS line')

	parsed = list(match.groups())

	if parsed[1] == None:
		raise MgException('Could not parse integer representing card number')

	if parsed[3] == None:
		raise MgException('Could not parse the card name')

	parsed[1] = int(parsed[1])

	return parsed
	
def parseFile(file_path):
	'''Parses a MWS file, ignoring comment lines. Returns tupple with two elements: a list of valid and invalid lines'''
	valid_list = []
	invalid_lines = []
	f = open(file_path, 'rU')
	
	for line in f:
		try:
			valid_list.append(parseLine(line))
		except MgException as e:
			invalid_lines.append((line, str(e)))
		
	return (valid_list, invalid_lines)

def splitFile(file_path):
	abs_path = os.path.abspath(file_path)
	directory, file_name = os.path.split(file_path)
	file_name = os.path.splitext(file_name)[0]
	return (directory, file_name)

def errorLog(msg):
	'''Prints out error message to the error stream. Expects a list of two element tupples: the offending card/line and the reason'''
	if len(msg) > 0:
		sys.stderr.write('Errors caused certain pictures to be exluded:\n')

	for message in msg:
		to_write = message[0].strip() + ': ' + message[1].strip() + '\n'
		sys.stderr.write(to_write)

def main():
	parsed_input = vars(arg_parser.parse_args())

	try:
		user_input, invalid_lines = parseFile(parsed_input['constructed_deck'])
	except IOError:
		print 'Card file does not exist'
		sys.exit()

	file_path, file_name = splitFile(parsed_input['constructed_deck'])

	creator = MgImageCreator(parsed_input['dpi'], parsed_input['card_dimensions'], parsed_input['card_number'])
	
	invalid_cards = creator.create(user_input, file_path, file_name)

	errorLog(invalid_lines + invalid_cards)