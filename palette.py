import random
from PIL import Image, ImageCms
from main import *

def distance(color_a, color_b):
    return (sum([(a-b)**2 for a, b in zip(color_a, color_b)]))**0.5

def kmeans(bins, means, k, maxiter=1000):
    #init
    record = {}
    for color in bins.keys():
        record[color] = -1

    for _ in range(maxiter):
        done = True
        cluster_sum = [[0, 0, 0] for _ in range(k)]
        cluster_size = [0 for _ in range(k)]
        #assign
        for color, count in bins.items():
            dists = [distance(color, mean) for mean in means]
            cluster = dists.index(min(dists))

            if record[color] != cluster:
                record[color] = cluster
                done = False

            for i in range(3):
                cluster_sum[cluster][i] += color[i] * count
            cluster_size[cluster] += count

        #update
        for i in range(k):
            means[i] = tuple([cluster_sum[i][j] / cluster_size[i] for j in range(3)])

        if done:
            break

    return means

def select(image, k=5):
    colors = image.getcolors(image.width * image.height)
    print('colors num:', len(colors))

    bins = {}
    for count, pixel in colors:
        bins[pixel] = count

    init = random.sample(list(bins), k)
    print('init:', init)

    means = kmeans(bins, init, k)
    means.sort(reverse=True)
    colors = [tuple([int(x) for x in color]) for color in means]
    return colors

def draw_palette(colors, size=100):
    images = []
    for color in colors:
        images.append(Image.new('LAB', (size, size), color))

    width = sum([image.width for image in images])
    height = max([image.height for image in images])

    merge = Image.new('LAB', (width, height))
    offset = 0
    for image in images:
        merge.paste(image, (offset, 0))
        offset += image.width

    image = lab2rgb(merge)
    image.show()

if __name__ == '__main__':
    image = Image.open('input.jpg')
    lab = rgb2lab(image)
    colors = select(lab)
    print('colors', colors)

    draw_palette(colors)
