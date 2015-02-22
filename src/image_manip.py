import sys

try:
    from PIL import Image
except ImportError:
    sys.stderr.write(
        'Cannot run program. ' +
        'Python Pillow (preferred) or PIL module is required.'
    )
    sys.exit()


def createCanvas(dpi, wh, xy):
    '''Creates a blank (white) RGB image canvas.
    Takes the dpi, a tuple of the width/hight of the card, and the number
    of cards per image.
    '''
    X = int(dpi * wh[0] * xy[0])
    Y = int(dpi * wh[1] * xy[1])

    return Image.new('RGB', (X, Y), 'white')


def resizeImage(image, dpi, wh):
    '''Resize an image to have the given width/hight (wh) given the dpi.'''
    new_x = int(dpi * wh[0])
    new_y = int(dpi * wh[1])

    return image.resize((new_x, new_y), Image.ANTIALIAS)


def pasteImage(canvas, image, xy):
    '''Paste an image onto a canvas at specific position.

    XY coordinates are given by increasing positives integers. For
    example (2, 3) would mean the image would be in the second column,
    third row. Correct spacing between the images is guaranteed if the
    pasted images are identical size.
    '''
    canvas.paste(image, (image.size[0]*xy[0], image.size[1]*xy[1]))

    return canvas
