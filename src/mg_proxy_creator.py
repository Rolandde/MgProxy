import re
import os.path
import sys

from src.create_page import MgImageCreator
from src.get_image import getMgImage
from src.constants import MgException
from src.argv_input import arg_parser

def parseLine(line):
	'''Expects the following format: ['SB:'] int [SET: three char code] card name. Brackets denote optional info. A four element list is returned, with the four fields. If the optional ones are not specified, None is the value.

	TODO: Rather then returning a list, it might be better to return a dictionary for legibilities sake. DAVE WAS HERE!
	'''
	match = re.match(r'^\s*(?:(SB:)\s+)?(\d+)\s+(?:\[(\w*)\]\s+)?(.*)$', line)

	if match == None:
		raise MgException('Could not parse MWS line')

	parsed = list(match.groups())  #Tupple is immutable, so conversion into a list

	if parsed[1] == None:
		raise MgException('Could not parse integer representing card number')

	if parsed[3] == None:
		raise MgException('Could not parse the card name')

	parsed[1] = int(parsed[1])

	return parsed
	
def parseFile(file_path):
	'''Parses a MWS file, ignoring comment lines. Returns tupple with two elements: a list of valid and invalid lines.'''
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
	'''Takes a file path and returns the two element tupple: the directory and the file name. The second element will be an empty string if only a directory path is given.'''
	abs_path = os.path.abspath(file_path)  #In case relative path is provided
	directory, file_name = os.path.split(file_path)
	file_name = os.path.splitext(file_name)[0] #Removes any extension in the filename
	return (directory, file_name)

def errorLog(msg):
	'''Prints out error message to the error stream. Expects a list of two element tupples: the offending card/line and the reason'''
	if len(msg) > 0:
		sys.stderr.write('Errors caused certain pictures to be exluded:\n')

	for message in msg:
		to_write = message[0].strip() + ': ' + message[1].strip() + '\n'
		sys.stderr.write(to_write)

def main():
	'''Runs the program. Parses the user command (argparse) and shunts the supplied info to the correct function'''
	parsed_input = vars(arg_parser.parse_args())
	file_name = parsed_input['file_name']

	try:
		user_input, invalid_lines = parseFile(file_name)
	except IOError:
		sys.stderr.write('Card file does not exist')
		sys.exit()

	file_path, file_name = splitFile(file_name)

	creator = MgImageCreator(parsed_input['dpi'], parsed_input['card_dimensions'], parsed_input['card_number'])
	
	invalid_cards = creator.createFromWeb(user_input, file_path, file_name)

	errorLog(invalid_lines + invalid_cards)