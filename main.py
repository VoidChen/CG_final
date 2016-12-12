import itertools
from PIL import Image
from palette import *
from util import *

if __name__ == '__main__':
    image = Image.open('input.jpg')
    print(image.format, image.size, image.mode)

    lab = rgb2lab(image)

    tests = []
    for random_init, black in itertools.product([True, False], repeat=2):
        print('random_init: {}, black: {}'.format(random_init, black))
        colors = select(lab, random_init=random_init, black=black)
        print('colors', colors)
        tests.append(draw_palette(colors))

    v_merge(tests).show()
