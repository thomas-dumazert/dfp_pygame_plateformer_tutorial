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

class Animation:
    def __init__(self, images, img_dur=5, loop=True) -> None:
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % \
                (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, 
                             self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]