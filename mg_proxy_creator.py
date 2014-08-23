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

	return match.groups()
	
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

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'Please specify a file containing cards'
		sys.exit()

	try:
		user_input = parseFile(sys.argv[1])
	except IOError:
		print 'Card file does not exist'
		sys.exit()

	print user_input[1]
	creator = MgImageCreator()

	for card_tupple in user_input[0]:
		card_numb, card_name = card_tupple[1], card_tupple[3]
		im = getMgImage(card_name)
		for _ in xrange(int(card_numb)):
			creator.paste(im)

	creator.save('/Users/Savo/Desktop/mg', 'test')
