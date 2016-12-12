from PIL import Image, ImageCms

def rgb2lab(image):
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, RGB_p, LAB_p, outputMode='LAB')

def lab2rgb(image):
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, LAB_p, RGB_p, outputMode='RGB')

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
