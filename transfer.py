import copy
from util import *

def modify_luminance(original, index, new_l):
    result = copy.deepcopy(original)

    result[index] = new_l
    for i in range(index+1, len(original)):
        result[i] = max(result[i], result[i-1])
    for i in range(index-1, -1, -1):
        result[i] = min(result[i], result[i+1])

    return result

def luminance_transfer(l, original_p, modified_p):
    def interpolation(xa, xb, ya, yb, z):
        return (ya*(xb-z) + yb*(z-xa)) / (xb - xa)

    assert(0 <= l <= 255)

    original_p = [0] + original_p + [255]
    modified_p = [0] + modified_p + [255]
    for i in range(len(original_p)):
        if original_p[i] == l:
            return modified_p[i]
        elif original_p[i] < l < original_p[i+1]:
            return interpolation(original_p[i], original_p[i+1], modified_p[i], modified_p[i+1], l)

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
        return (color + (boundary - color) * (offset.len() / (c_boundary - original_c).len())).data
    else:
        return (color + offset).data
