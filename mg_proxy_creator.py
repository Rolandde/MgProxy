import re
import os.path
import sys

from src.create_page import MgImageCreator
from src.get_image import getMgImage
from src.constants import MgException

def parseLine(line):
	'''Expects the following format: ['SB:'] int [SET: three char code] card name. Brackets denote optional info.'''
	match = re.match(r'^\s*(?:(SB:)\s+)?(\d+)\s+(?:\[(\w*)\]\s+)?(.*)$', line)

	if match == None:
		raise MgException('Invalid MWS line')

	parsed = list(match.groups())
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
		except MgException:
			invalid_lines.append(line)
		
	return (valid_list, invalid_lines)

def createNameList(valid_list):
	result = []
	for line in valid_list:
		result = result + ([line[3]] * line[1])
	return result

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'Please specify a file containing cards'
		sys.exit()

	try:
		user_input = parseFile(sys.argv[1])
	except IOError:
		print 'Card file does not exist'
		sys.exit()

	creator = MgImageCreator()
	creator.create(createNameList(user_input[0]), '/Users/Savo/Desktop/mg')

	# creator.save('/Users/Savo/Desktop/mg', 'test')
