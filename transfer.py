import copy
import itertools
from util import *

def modify_luminance(original, index, new_l):
    result = copy.deepcopy(original)

    result[index] = new_l
    for i in range(index+1, len(original)):
        result[i] = max(result[i], result[i-1])
    for i in range(index-1, -1, -1):
        result[i] = min(result[i], result[i+1])

    return result

def luminance_transfer(color, original_p, modified_p):
    def interpolation(xa, xb, ya, yb, z):
        return (ya*(xb-z) + yb*(z-xa)) / (xb - xa)

    l = color[0]
    original_l = [0] + [l for l, a, b in original_p] + [255]
    modified_l = [0] + [l for l, a, b in modified_p] + [255]
    for i in range(len(original_l)):
        if original_l[i] == l:
            return modified_l[i]
        elif original_l[i] < l < original_l[i+1]:
            return interpolation(original_l[i], original_l[i+1], modified_l[i], modified_l[i+1], l)

class Vec3:
    def __init__(self, data):
        self.data = copy.deepcopy(data)

    def __add__(self, other):
        return Vec3([x + y for x, y in zip(self.data, other.data)])

    def __sub__(self, other):
        return Vec3([x - y for x, y in zip(self.data, other.data)])

    def __mul__(self, other):
        return Vec3([x * other for x in self.data])

    def __truediv__(self, other):
        return Vec3([x / other for x in self.data])

    def len(self):
        return (sum([x**2 for x in self.data]))**0.5

def single_color_transfer(color, original_c, modified_c):
    def get_boundary(origin, direction, k_min, k_max, iters=100):
        start = origin + direction * k_min
        end = origin + direction * k_max
        for _ in range(iters):
            mid = (start + end) / 2
            if ValidLAB(RegularLAB(mid.data)) and ValidRGB(LABtoRGB(RegularLAB(mid.data))):
                start = mid
            else:
                end = mid
        return (start + end) / 2

    #init
    color = Vec3(color)
    original_c = Vec3(original_c)
    modified_c = Vec3(modified_c)
    offset = modified_c - original_c

    #get boundary
    c_boundary = get_boundary(original_c, offset, 1, 255)
    if ValidLAB(RegularLAB((color + offset).data)) and ValidRGB(LABtoRGB(RegularLAB((color + offset).data))):
        boundary = get_boundary(color, offset, 1, 255)
    else:
        boundary = get_boundary(modified_c, color - original_c, 0, 1)

    #transfer
    if (boundary - color).len() < (c_boundary - original_c).len():
        return color + (boundary - color) * (offset.len() / (c_boundary - original_c).len())
    else:
        return color + offset

def multiple_color_transfer(color, original_p, modified_p):
    def weight(color, original_c):
        #TBD
        if distance(color, original_c) != 0:
            return min(1, 1 / distance(color, original_c))
        else:
            return 1

    #single color transfer
    color_st = []
    for i in range(len(original_p)):
        color_st.append(single_color_transfer(color, original_p[i], modified_p[i]))

    #get weights
    weights = []
    for i in range(len(original_p)):
        weights.append(weight(color, original_p[i]))

    #calc result
    color_mt = Vec3([0, 0, 0])
    for i in range(len(original_p)):
        color_mt = color_mt + color_st[i] * (weights[i] / sum(weights))

    return color_mt.data[-2:]

def sample_color(size=16):
    assert(size >= 2)

    values = [i * (255/(size-1)) for i in range(size)]
    colors = []
    for r, g, b in itertools.product(values, repeat=3):
        colors.append((r, g, b))

    return colors

def image_transfer(image, original_p, modified_p):
    #build color map
    print('build color map')
    color_map = {}
    colors = image.getcolors(image.width * image.height)
    for _, color in colors:
        l = luminance_transfer(color, original_p, modified_p)
        ab = multiple_color_transfer(color, original_p, modified_p)
        color_map[color] = tuple([int(x) for x in [l, *ab]])

    #transfer image
    print('transfer image')
    result = Image.new('LAB', image.size)
    result_pixels = result.load()
    for i in range(image.width):
        for j in range(image.height):
            result_pixels[i, j] = color_map[image.getpixel((i, j))]

    return result
