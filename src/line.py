import pygame
import sys

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = (255, 0, 0)



class Line(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(x=0, y=0)
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        self.cord = []

    def patch(self, surface):
        self.image.blit(surface, (self.rect.x, self.rect.y))

    def set_cord(self, cord):
        self.cord = cord

    def get_cord(self):
        return self.cord