import urllib
import sys
import os

from StringIO import StringIO
from .constants import MgException, BASE_URL
from urlparse import urljoin

try:
	from PIL import Image
except ImportError:
	sys.stderr.write('Cannot run program. Python Pillow (preferred) or PIL module is required.')
	sys.exit()

def createAddress(card_name, set_name=None):
	'''Creates a URL from a card name and an optional set, correctly escaping characters.'''
	return_url = BASE_URL

	if set_name:
		if len(set_name) < 4:
			set_url_dir = 'set'
		else:
			set_url_dir = 'setname'

		return_url = urljoin(return_url, set_url_dir)
		return_url = urljoin(return_url, set_name)

	hq_card_name = urllib.quote(card_name + '.hq.jpg')
	return urljoin(return_url, hq_card_name)

def getMgImage(card_name, set_name=None):
	'''Downloads a given card name and returns the Pillow image. Note that this function does not check if the downloaded image is a valid image file.'''
	address = createAddress(card_name, set_name)
	response = urllib.urlopen(address)

	if response.getcode() != 200:
		raise MgException('Card URL does not exist. Error code: ' + str(response.getcode()) + ': ' + address)

	if response.info()['Content-Type'] != 'image/jpeg':
		raise MgException('Expected image file jpeg, instead received: ' + response.info()['Content-Type'] + ': ' + address)

	image_size = int(response.info()['Content-Length'])
	image_stream = response.read(image_size)
	image_stream = StringIO(image_stream)

	return Image.open(image_stream)

def createLocalAddress(directory, card_name):
	'''Create a valid local address from a directory and a card name (including extension)'''
	return os.path.join(directory, card_name)

def getLocalMgImage(directory, card_name):
	address = createLocalAddress(directory, card_name)

	try:
		card_image = Image.open(address)
	except IOError:
		raise MgException('Cannot open local card image file')
	else:
		return card_image

def validateImage(image):     
	'''PIL does not provide a good way to test if an image is corrupt. The easiest way is to load the image into memory and catch the IOError'''
	try:
		image.load()
	except IOError:
		raise MgException('Image file is corrupt')
