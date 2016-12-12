import random
import itertools
from PIL import Image, ImageCms
from main import *

def distance(color_a, color_b):
    return (sum([(a-b)**2 for a, b in zip(color_a, color_b)]))**0.5

def kmeans(bins, means, k, maxiter=1000, black=True):
    #init
    record = {}
    for color in bins.keys():
        record[color] = -1

    if black:
        means.append((0, 128, 128))

    for _ in range(maxiter):
        done = True
        cluster_sum = [[0, 0, 0] for _ in range(len(means))]
        cluster_size = [0 for _ in range(len(means))]

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

    print(cluster_size)
    return means[:k]

def simple_bins(bins, size=16):
    level = 256//size
    temp = {}
    for x in itertools.product(range(size), repeat=3):
        temp[x] = {'size': 0, 'sum': [0, 0, 0]}

    for color, count in bins.items():
        index = tuple([c//level for c in color])
        for i in range(3):
            temp[index]['sum'][i] += color[i] * count
        temp[index]['size'] += count

    result = {}
    for color in temp.values():
        if color['size'] != 0:
            result[tuple([color['sum'][j] / color['size'] for j in range(3)])] = color['size']

    return result

def select(image, k=5, black=True):
    colors = image.getcolors(image.width * image.height)
    print('colors num:', len(colors))

    bins = {}
    for count, pixel in colors:
        bins[pixel] = count
    bins = simple_bins(bins)

    init = random.sample(list(bins), k)
    print('init:', init)

    means = kmeans(bins, init, k, black=black)
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
    colors = select(lab, black=True)
    print('colors', colors)
    draw_palette(colors)
    colors = select(lab, black=False)
    print('colors', colors)
    draw_palette(colors)
