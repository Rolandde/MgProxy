from PIL import Image
from constants import DPI, WIDTH, HIGHT, PAGE_X, PAGE_Y
import os

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
		self.current_canvas = createCanvas()
		self.canvas_list = []

	def paste(self, image):
		pasteImage(self.current_canvas, image, self.pic_count%PAGE_X, int(round(self.pic_count/PAGE_X, 0)))
		self.pic_count += 1

		if self.pic_count == PAGE_X * PAGE_Y:
			self.canvas_list.append(self.current_canvas)
			self.current_canvas = createCanvas()
			self.pic_count = 0

	def save(self, directory, file_name):
		if self.pic_count != 0:
			self.canvas_list.append(self.current_canvas)

		for i, canvas in enumerate(self.canvas_list):
			new_file_name = file_name + str(i) + '.jpg'
			file_path = os.path.join(directory, new_file_name)
			canvas.save(file_path)