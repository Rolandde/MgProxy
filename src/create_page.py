import os, sys

try:
	from PIL import Image
except ImportError:
	sys.stderr.write('Cannot run program. Python Pillow (preferred) or PIL module is required.')
	sys.exit()

from get_image import getMgImage, validateImage
from constants import MgException


def createCanvas(dpi, wh, xy):
	X = int(dpi * wh[0] * xy[0])
	Y = int(dpi * wh[1] * xy[1])

	return Image.new('RGB', (X, Y), 'white')

def resizeImage(image, dpi, wh):
	new_x = int(dpi * wh[0])
	new_y = int(dpi * wh[1])

	return image.resize((new_x, new_y), Image.ANTIALIAS)

def pasteImage(canvas, image, dpi, wh, xy):
	new_image = resizeImage(image, dpi, wh)
	canvas.paste(new_image, (new_image.size[0]*xy[0], new_image.size[1]*xy[1]))

	return canvas

class MgImageCreator(object):
	def __init__(self, dpi, wh, xy):
		self.dpi = dpi
		self.wh = wh
		self.xy = xy

		self.pic_count = 0;
		self.page_count = 0;
		self.current_canvas = createCanvas(dpi, wh, xy)

	def paste(self, image):
		xy = (self.pic_count%self.xy[0], int(round(self.pic_count/self.xy[0], 0)))
		pasteImage(self.current_canvas, image, self.dpi, self.wh, xy)
		self.pic_count += 1

	def create(self, name_array, directory, file_name):
		invalid_names = []

		for number_name in name_array:
			number, card_name = number_name[1], number_name[3]

			try:
				image = getMgImage(card_name)
				validateImage(image)
			except MgException as e:
				invalid_names.append((card_name, str(e)))
			else:
				for _ in xrange(0, number):
					self.paste(image)

					if self.pic_count == self.xy[0] * self.xy[1]:
						self.save(directory, file_name)

						self.current_canvas = createCanvas(self.dpi, self.wh, self.xy)
						self.pic_count = 0
						self.page_count += 1

		if (self.pic_count > 0):
			self.save(directory, file_name)

		return invalid_names

	def save(self, directory, file_name):
		new_file_name = str(file_name) + str(self.page_count) + '.jpg'
		file_path = os.path.join(directory, new_file_name)
		self.current_canvas.save(file_path)