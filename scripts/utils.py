import os

import pygame

BASE_IMAGE_PATH = 'data/images/'
DEFAULT_COLORKEY = (0, 0, 0)

def load_image(path, colorkey=DEFAULT_COLORKEY):
    img = pygame.image.load(BASE_IMAGE_PATH + path).convert()
    img.set_colorkey(colorkey)
    return img

def load_images(path, colorkey=DEFAULT_COLORKEY):
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name, colorkey))
    return images