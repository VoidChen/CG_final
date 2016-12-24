from PIL import Image, ImageCms

def rgb2lab(image):
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, RGB_p, LAB_p, outputMode='LAB')

def lab2rgb(image):
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, LAB_p, RGB_p, outputMode='RGB')

def LABtoXYZ(LAB):
    def f(n):
        return n**3 if n > 6/29 else 3 * ((6/29)**2) * (n - 4/29)

    L, a, b = LAB
    assert(0 <= L <= 100 and -128 <= a <= 127 and -128 <= b <= 127)

    X = 95.047 * f((L+16)/116 + a/500)
    Y = 100.000 * f((L+16)/116)
    Z = 108.883 * f((L+16)/116  - b/200)
    return (X, Y, Z)

def XYZtoRGB(XYZ):
    def f(n):
        return n*12.92 if n <= 0.0031308 else (n**(1/2.4)) * 1.055 - 0.055

    X, Y, Z = [x/100 for x in XYZ]
    R = f(3.2406*X + -1.5372*Y + -0.4986*Z) * 255
    G = f(-0.9689*X + 1.8758*Y + 0.0415*Z) * 255
    B = f(0.0557*X + -0.2040*Y + 1.0570*Z) * 255
    return (R, G, B)

def LABtoRGB(LAB):
    return XYZtosRGB(LABtoXYZ(LAB))

def ValidRGB(RGB):
    return False not in [0 <= x <= 255 for x in RGB]

def compare(image_a, image_b):
    print('compare', list(image_a.getdata()) == list(image_b.getdata()))

def h_merge(images):
    width = sum([image.width for image in images])
    height = max([image.height for image in images])

    merge = Image.new(images[0].mode, (width, height))
    offset = 0
    for image in images:
        merge.paste(image, (offset, 0))
        offset += image.width

    return merge

def v_merge(images):
    width = max([image.width for image in images])
    height = sum([image.height for image in images])

    merge = Image.new(images[0].mode, (width, height))
    offset = 0
    for image in images:
        merge.paste(image, (0, offset))
        offset += image.height

    return merge
