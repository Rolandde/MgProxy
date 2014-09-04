import urllib, sys
from StringIO import StringIO
from .constants import MgException, BASE_URL

try:
	from PIL import Image
except ImportError:
	sys.stderr.write('Cannot run program. Python Pillow (preferred) or PIL module is required.')
	sys.exit()

def createAddress(card_name):
	'''Creates a URL from a card name, correctly escaping characters.
	TODO: This can be easily expanded to allow specific sets to be downloaded.
	'''
	return BASE_URL + urllib.quote(card_name) + '.hq.jpg'

def getMgImage(card_name):
	'''Downloads a given card name and returns the Pillow image. Note that this function does not check if the downloaded image is a valid image file.'''
	address = createAddress(card_name)
	response = urllib.urlopen(address)

	if response.getcode() != 200:
		raise MgException('Card URL does not exist. Error code: ' + str(response.getcode()) + ': ' + address)

	if response.info()['Content-Type'] != 'image/jpeg':
		raise MgException('Expected image file jpeg, instead received: ' + response.info()['Content-Type'] + ': ' + address)

	image_size = int(response.info()['Content-Length'])
	image_stream = response.read(image_size)
	image_stream = StringIO(image_stream)

	return Image.open(image_stream)

def validateImage(image):     
	'''PIL does not provide a good way to test if an image is corrupt. The easiest way is to load the image into memory and catch the IOError'''
	try:
		image.load()
	except IOError:
		raise MgException('Image file is corrupt')
