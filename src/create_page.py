from PIL import Image
from constants import DPI, WIDTH, HIGHT, PAGE_X, PAGE_Y
import os

from get_image import getMgImage


def createCanvas():
	X = int(DPI * WIDTH * PAGE_X)
	Y = int(DPI * HIGHT * PAGE_Y)

	return Image.new('RGB', (X, Y), 'white')

def resizeImage(image):
	new_x = int(DPI * WIDTH)
	new_y = int(DPI * HIGHT)

	return image.resize((new_x, new_y), Image.ANTIALIAS)

def pasteImage(canvas, image, x, y):
	assert (x >= 0 and x < PAGE_X), 'Invalid image paste position' 
	assert (y >= 0 and y < PAGE_Y), 'Invalid image paste position'

	new_image = resizeImage(image)
	canvas.paste(new_image, (new_image.size[0]*x, new_image.size[1]*y))

	return canvas

class MgImageCreator(object):
	def __init__(self):
		self.pic_count = 0;
		self.page_count = 0;
		self.current_canvas = createCanvas()

	def paste(self, image):
		pasteImage(self.current_canvas, image, self.pic_count%PAGE_X, int(round(self.pic_count/PAGE_X, 0)))
		self.pic_count += 1

	def create(self, name_array, directory, file_name):
		for name in name_array:
			image = getMgImage(name)
			self.paste(image)

			if self.pic_count == PAGE_X * PAGE_Y:
				self.save(directory, file_name)

				self.current_canvas = createCanvas()
				self.pic_count = 0
				self.page_count += 1

		if (self.pic_count > 0):
			self.save(directory, file_name)

	def save(self, directory, file_name):
		new_file_name = str(file_name) + str(self.page_count) + '.jpg'
		file_path = os.path.join(directory, new_file_name)
		self.current_canvas.save(file_path)