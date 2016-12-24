import copy

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
