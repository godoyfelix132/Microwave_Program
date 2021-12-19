import pygame

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]


class R_Port(pygame.sprite.Sprite):
    name = 'P'
    value = 1000

    def __init__(self, name='P', value=1000):
        super().__init__()
        self.name = name
        self.value = value
        self.image = pygame.image.load('rsc/r_port.png').convert()
        self.orig_image = self.image
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.horizontal = True

    def rotate(self):
        self.angle += 90
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.horizontal = not self.horizontal

    def place(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y