import urllib
from StringIO import StringIO
from PIL import Image
from constants import MgException, BASE_URL

def createAddress(card_name):
	return BASE_URL + urllib.quote(card_name) + '.hq.jpg'

def getMgImage(card_name):
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