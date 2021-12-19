import pygame

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = (255, 0, 0)

RADIUS = 3
WIDTH = 10
HEIGHT = 10


class Label(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = str(name)
        self.myfont = pygame.font.SysFont("monospace", 18)
        self.image = self.myfont.render(name, 1, BLACK)
        self.rect = self.image.get_rect()

    def place(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y

    def update(self, *args, **kwargs) -> None:
        self.image = self.myfont.render(self.name, 1, BLACK)