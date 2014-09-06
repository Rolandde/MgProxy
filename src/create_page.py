import os, sys

try:
	from PIL import Image
except ImportError:
	sys.stderr.write('Cannot run program. Python Pillow (preferred) or PIL module is required.')
	sys.exit()

from .get_image import getMgImage, getLocalMgImage, validateImage
from .constants import MgException


def createCanvas(dpi, wh, xy):
	'''Creates a blank (white) RGB image canvas. Takes the dpi, a tuple of the width/hight of the card, and the number of cards per image.'''
	X = int(dpi * wh[0] * xy[0])
	Y = int(dpi * wh[1] * xy[1])

	return Image.new('RGB', (X, Y), 'white')

def resizeImage(image, dpi, wh):
	'''Resize an image to have the given width/hight (wh) given the dpi.'''
	new_x = int(dpi * wh[0])
	new_y = int(dpi * wh[1])

	return image.resize((new_x, new_y), Image.ANTIALIAS)

def pasteImage(canvas, image, dpi, wh, xy):
	'''Paste an image onto a canvas. Provide desired dpi and width/hight of image. XY coordinates are given by increasing positives integers. For example (2, 3) would mean the image would be in the second column, third row. Correct spacing between the images is guaranteed if the wh and dpi values do not change.'''
	new_image = resizeImage(image, dpi, wh)
	canvas.paste(new_image, (new_image.size[0]*xy[0], new_image.size[1]*xy[1]))

	return canvas

class MgImageCreator(object):
	'''An instance of this object is given the dpi, the width/hight of the cards, and the max number of cards in the xy directions.

	Once an object of this class is initialized, the create functions can be called to create jpgs with the provided cards.
	'''
	def __init__(self, dpi, wh, xy):
		self.dpi = dpi
		self.wh = wh
		self.xy = xy

		self.pic_count = 0  #How many pictures have been pasted
		self.page_count = 0 #How many pages have been saved

		self.current_canvas = createCanvas(dpi, wh, xy)
		self.invalid_names = []  #Holds a list of two element tupples: the name of invalid cards and the reason.

	def paste(self, image):
		'''Pastes the image into the next slot on the canvas.
		TODO: This should throw an exception if there are no more free spaces.
		TODO: Make the xy variable calculation a lot more readable.
		'''
		xy = (self.pic_count%self.xy[0], int(round(self.pic_count/self.xy[0], 0)))
		pasteImage(self.current_canvas, image, self.dpi, self.wh, xy)
		self.pic_count += 1

	def pasteMulti(self, image, number, directory, file_name):
		'''Pastes the provided image the specified number of times, saving the canvas as required.'''
		for _ in xrange(0, number):
			self.paste(image)

			if self.pic_count == self.xy[0] * self.xy[1]:
				self.save(directory, file_name)

				self.current_canvas = createCanvas(self.dpi, self.wh, self.xy)
				self.pic_count = 0
				self.page_count += 1

	def reset(self):
		'''Returns the instance to the initial state and returns any errors that have occured since the last reset.'''

		#This assigns the invalid_names by value (default is reference), as the init function will be called to reset the instance
		invalid_names = list(self.invalid_names)

		#Correctly reset the object so that the instance can be called anew
		self.__init__(self.dpi, self.wh, self.xy)

		return invalid_names

	def create(self, local, name_array, directory, file_name):
		'''Takes a name_array containing the number and name of cards and creates images of those cards. Local is a boolean specifying if the cards are local or online.
		Returns a list of two element tupples: the name and reason of any cards that could not be successfully pasted.

		TODO: Include the option of specifying sets.
		'''
		for number_name in name_array:
			number, card_name = number_name[1], number_name[3]

			try:
				if local:
					image = getLocalMgImage(directory, card_name)
				else:
					image = getMgImage(card_name)
				validateImage(image)
			except MgException as e:
				self.invalid_names.append((card_name, str(e)))
			else:
				self.pasteMulti(image, number, directory, file_name)

		if (self.pic_count > 0):
			self.save(directory, file_name)

		return self.reset()

	def save(self, directory, file_name):
		'''Saves the file_name to the directory. It will alwasy save as a jpg. To prevent overwriting previously saved pages, a integer counter is appended at the end of the filename.
		TODO: Maybe give the user the option of specifying the image format.
		'''
		new_file_name = str(file_name) + str(self.page_count) + '.jpg'
		file_path = os.path.join(directory, new_file_name)

		try:
			self.current_canvas.save(file_path)
		except IOError as e:
			error_msg = (file_name, 'Could not save final image - ' + e.strerror + ' - ' + e.filename)
			self.invalid_names.append(error_msg)

	def createFromWeb(self, name_array, directory, file_name):
		'''Wrapper function to run image creation from web-based image files.'''
		return self.create(False, name_array, directory, file_name)

	def createFromLocal(self, name_array, directory, file_name):
		'''Wrapper function to run image creation from local files.'''
		return self.create(True, name_array, directory, file_name)