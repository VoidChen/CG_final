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

if __name__ == '__main__':
    image = Image.open('input.jpg')
    print(image.format, image.size, image.mode)

    lab = rgb2lab(image)
    rgb = lab2rgb(lab)
    rgb.save('rgb.jpg')
    compare(rgb, image)
