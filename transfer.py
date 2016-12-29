import math
import copy
import itertools
import time
import numpy.linalg
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

def calc_weights(color, original_p):
    def mean_distance(original_p):
        dists = []
        for a, b in itertools.combinations(original_p, 2):
            dists.append(distance(a, b))
        return sum(dists) / len(dists)

    def gaussian(r, md):
        return math.exp(((r/md)**2) * -0.5)

    #init
    md = mean_distance(original_p)

    #get phi and lambda
    matrix = []
    for i in range(len(original_p)):
        temp = []
        for j in range(len(original_p)):
            temp.append(gaussian(distance(original_p[j], original_p[i]), md))
        matrix.append(temp)
    phi = numpy.array(matrix)
    lamb = numpy.linalg.inv(phi)

    #calc weights
    weights = [0 for _ in range(len(original_p))]
    for i in range(len(original_p)):
        for j in range(len(original_p)):
            weights[i] += lamb[i][j] * gaussian(distance(color, original_p[j]), md)

    #normalize weights
    weights = [w if w >=0 else 0 for w in weights]
    w_sum = sum(weights)
    weights = [w/w_sum for w in weights]

    return weights

def multiple_color_transfer(color, original_p, modified_p):
    #single color transfer
    color_st = []
    for i in range(len(original_p)):
        color_st.append(single_color_transfer(color, original_p[i], modified_p[i]))

    #get weights
    weights = calc_weights(color, original_p)

    #calc result
    color_mt = Vec3([0, 0, 0])
    for i in range(len(original_p)):
        color_mt = color_mt + color_st[i] * weights[i]

    return color_mt.data[-2:]

def RGB_sample_color(size=16):
    assert(size >= 2)

    levels = [i * (255/(size-1)) for i in range(size)]
    colors = []
    for r, g, b in itertools.product(levels, repeat=3):
        colors.append((r, g, b))

    return colors

def nearest_color(target, level_size):
    levels = [i * (255/(level_size-1)) for i in range(level_size)]
    nearest_level = []
    for ch in target:
        for i in range(len(levels)):
            if levels[i] == ch:
                nearest_level.append((levels[i], levels[i]))
                break
            elif levels[i] < ch < levels[i+1]:
                nearest_level.append((levels[i], levels[i+1]))
                break

    return nearest_level

def trilinear_interpolation(target, sample_color_map):
    #calc rates
    corners = nearest_color(target, round(len(sample_color_map)**(1/3)))
    RGBr = []
    for i in range(3):
        temp = (target[i] - corners[i][0]) / (corners[i][1] - corners[i][0]) if corners[i][0] != corners[i][1] else 0
        RGBr.append((1 - temp, temp))

    rates = []
    for Rr, Gr, Br in itertools.product(*RGBr):
        rates.append(Rr * Gr * Br)

    #calc result
    result = [0, 0, 0]
    for color, rate in zip(itertools.product(*corners), rates):
        sc = sample_color_map[color]
        for i in range(3):
            result[i] += sc[i] * rate

    return result

def image_transfer(image, original_p, modified_p, sample_level=16):
    #build sample color map
    print('Build sample color map')
    t = time.time()
    sample_color_map = {}
    sample_colors = RGB_sample_color(sample_level)
    for color in sample_colors:
        l = luminance_transfer(color, original_p, modified_p)
        ab = multiple_color_transfer(color, original_p, modified_p)
        sample_color_map[color] = tuple([int(x) for x in [l, *ab]])
    print('Build sample color map time', time.time() - t)

    #build color map
    print('Build color map')
    t = time.time()
    color_map = {}
    colors = image.getcolors(image.width * image.height)
    for _, color in colors:
        color_map[color] = tuple([int(x) for x in trilinear_interpolation(color, sample_color_map)])
    print('Build color map time', time.time() - t)

    #transfer image
    print('Transfer image')
    t = time.time()
    result = Image.new('LAB', image.size)
    result_pixels = result.load()
    for i in range(image.width):
        for j in range(image.height):
            result_pixels[i, j] = color_map[image.getpixel((i, j))]
    print('Transfer image time', time.time() - t)

    return result
