from PIL import Image
from palette import *
from util import *

if __name__ == '__main__':
    image = Image.open('input.jpg')
    print(image.format, image.size, image.mode)

    lab = rgb2lab(image)
    colors = select(lab, black=True)
    print('colors', colors)
    draw_palette(colors)
    colors = select(lab, black=False)
    print('colors', colors)
    draw_palette(colors)
