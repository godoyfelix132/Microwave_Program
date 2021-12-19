import pygame as pg
from src.button import *
import re

pg.init()
# screen1 = pg.display.set_mode((300, 125))
COLOR_INACTIVE = pg.Color('white')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 25)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, 0, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, 'black')
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen1):
        # Blit the text.
        screen1.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen1, self.color, self.rect, 2)


class TextBox:
    def __init__(self, screen1,name, value):
        clock = pg.time.Clock()
        num = re.findall(r'\d+', name)
        self.component = re.findall("[A-Za-z]", name)
        self.new_name = name
        self.new_value = value
        self.input_box1 = InputBox(50, 10, 1, 30, text= str(num[0]))
        self.input_box2 = InputBox(50, 50, 1, 30, text= str(1000))
        self.done2 = False
        btn1 = Button('Accept', 100, 90, 100, 25, self.btn1_action)

        input_boxes = [self.input_box1, self.input_box2]
        done = False

        while not done and not self.done2:
            for event in pg.event.get():
                btn1.handle_event(event)
                if event.type == pg.QUIT:
                    done = True
                for box in input_boxes:
                    box.handle_event(event)

            for box in input_boxes:
                box.update()

            screen1.fill((255, 255, 255))
            for box in input_boxes:
                box.draw(screen1)
                btn1.draw(screen1)

            pg.display.flip()
            clock.tick(30)
        pg.quit()

    def btn1_action(self):
        try:
            num_temp = int(self.input_box1.text)
            self.new_name = str(self.component[0]+str(num_temp))
            self.new_value = int(self.input_box2.text)
            print(self.new_value)
            self.done2 = True
        except:
            self.done2 = False


if __name__ == '__main__':
    screen1 = pg.display.set_mode((300, 125))
    a = TextBox(screen1,'R11', 500)
    print(a.new_name)
    print(a.new_value)