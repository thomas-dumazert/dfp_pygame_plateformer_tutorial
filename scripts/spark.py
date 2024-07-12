import math

import pygame

class Spark:
    def __init__(self, pos, angle, speed) -> None:
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

        self.color = (255, 255, 255)
        self.length = 3
        self.width = 0.5

    def update(self) -> bool:
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.speed = max(self.speed - 0.1, 0)

        return not self.speed

    def render(self, surf, offset=(0, 0)):
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * self.length - offset[0], 
             self.pos[1] + math.sin(self.angle) * self.speed * self.length - offset[1]), 
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * self.width - offset[0], 
             self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * self.width - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * self.length - offset[0], 
             self.pos[1] + math.sin(self.angle + math.pi) * self.speed * self.length - offset[1]), 
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * self.width - offset[0], 
             self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * self.width - offset[1]),
        ]

        pygame.draw.polygon(surf, self.color, render_points)