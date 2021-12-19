import pygame

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = (255, 0, 0)

RADIUS = 3
WIDTH = 10
HEIGHT = 10

class Terminal(pygame.sprite.Sprite):
    def __init__(self, component, side):
        super().__init__()
        self.name = 'T' + str(side)
        self.side = side
        self.component = component
        self.image = pygame.Surface([WIDTH, WIDTH])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.circle(self.image, RED, (WIDTH//2, HEIGHT//2), RADIUS)
        self.rect = self.image.get_rect()
        self.cord = []

    def place(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y

