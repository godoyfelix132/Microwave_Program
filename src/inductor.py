import pygame
from src.label import *

WHITE = [255, 255, 255]


class Inductor(pygame.sprite.Sprite):
    name = 'I'
    value = 0.001

    def __init__(self, name='L', value=0.001):
        super().__init__()
        self.name = name
        self.value = float(value)
        self.image = pygame.image.load('rsc/ind.png').convert()
        self.orig_image = self.image
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.horizontal = True
        self.label_name = name
        self.label_value = value


    def place(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y
        self.label_list = pygame.sprite.Group()
        if self.horizontal:
            self.label_name = Label(self.name)
            self.label_name.place(self.rect.x + 30, self.rect.y - 10)
            self.label_list.add(self.label_name)
            self.label_value = Label(str(self.value * (10**9)) + 'nH')
            self.label_value.place(self.rect.x + 30, self.rect.y + 30)
            self.label_list.add(self.label_value)
        else:
            self.label_name = Label(self.name)
            self.label_name.place(self.rect.x + 35, self.rect.y + 15)
            self.label_list.add(self.label_name)
            self.label_value = Label(str(self.value * (10**9)) + 'nH')
            self.label_value.place(self.rect.x + 35, self.rect.y + 30)
            self.label_list.add(self.label_value)

    def rotate(self):
        self.angle += 90
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.horizontal = not self.horizontal

    def update(self, *args, **kwargs) -> None:
        self.label_name.name = self.name
        self.label_name.update()
        self.label_value.name = str(self.value * (10**9)) + 'nH'
        self.label_value.update()
