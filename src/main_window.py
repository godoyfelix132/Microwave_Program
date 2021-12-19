from src.resistor import *
from src.capacitor import *
from src.inductor import *
from src.r_port import *
from src.l_port import *
from src.label import *
from src.terminal import *
from src.line import *
from src.node import *
from src.textbox import *
from src.input_box import *

pygame.init()

GRAY = (220, 220, 220)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
LINES_GAP = 20
SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


class App(object):
    execute = False
    sprites_list = pygame.sprite.Group()
    initial_list = pygame.sprite.Group()
    res_list = pygame.sprite.Group()
    cap_list = pygame.sprite.Group()
    ind_list = pygame.sprite.Group()
    ter_list = pygame.sprite.Group()
    ter_ports_list = pygame.sprite.Group()
    lines_list = pygame.sprite.Group()
    label_list = pygame.sprite.Group()
    label_fixed_list = pygame.sprite.Group()
    temp_list = pygame.sprite.GroupSingle()
    input_box_list = pygame.sprite.Group()
    nodes_list = []
    cord_lines_list = []
    all_cord = []
    res_up = False
    cap_up = False
    ind_up = False
    element_down = True
    element_up = False
    angle = 0
    rotate_element = False
    element_temp = 0
    drawing_line = None
    side = True
    vertical = False
    tmp_surface = pygame.Surface(SIZE, pygame.SRCALPHA)
    tmp_surface.fill(WHITE)
    tmp_surface.set_colorkey(WHITE)
    line_temp = 0
    line_temp_x1 = 0
    line_temp_x2 = 0
    line_temp_y1 = 0
    line_temp_y2 = 0
    l2 = 0
    hit_terminal = False
    hit_line = False

    def __init__(self):
        self.res = Resistor('R0', 0)
        self.cap = Capacitor('C0', 0)
        self.ind = Inductor('L0', 0)
        self.port_v1_up = R_Port('V1', 0)
        self.port_v1_down = R_Port('V1', 0)
        self.port_v2_up = L_Port('V2', 0)
        self.port_v2_down = L_Port('V2', 0)
        self.port_v1_up.place(40, 100)
        self.port_v1_down.place(40, 460)
        self.port_v2_up.place(1080, 100)
        self.port_v2_down.place(1080, 460)
        self.term_port_v1_up = Terminal('V1', '1')
        self.term_port_v1_down = Terminal('V1', '0')
        self.term_port_v2_up = Terminal('V2', '1')
        self.term_port_v2_down = Terminal('V2', '0')
        self.term_port_v1_up.place(115, 135)
        self.term_port_v1_down.place(115, 495)
        self.term_port_v2_up.place(1075, 135)
        self.term_port_v2_down.place(1075, 495)
        self.term_port_v1_up.cord = (120, 140)
        self.term_port_v1_down.cord = (120, 500)
        self.term_port_v2_up.cord = (1080, 140)
        self.term_port_v2_down.cord = (1080, 500)
        self.ter_ports_list.add(self.term_port_v1_up)
        self.ter_ports_list.add(self.term_port_v1_down)
        self.ter_ports_list.add(self.term_port_v2_up)
        self.ter_ports_list.add(self.term_port_v2_down)
        self.res.place(20, 0)
        self.cap.place(120, 0)
        self.ind.place(220, 0)
        self.sprites_list.add(self.res)
        self.sprites_list.add(self.cap)
        self.sprites_list.add(self.ind)
        self.sprites_list.add(self.port_v1_up)
        self.sprites_list.add(self.port_v1_down)
        self.sprites_list.add(self.port_v2_up)
        self.sprites_list.add(self.port_v2_down)
        self.initial_list = self.sprites_list.copy()

        self.btn1 = Button('EXECUTE', 1000, 10, 80, 20, self.btn1_action)
        self.btn2 = Button('CLEAN', 1100, 10, 80, 20, self.btn2_action)
        self.btn3 = Button('ACCEPT', 640, 10, 80, 20, self.btn3_action)
        self.label_component = Label('R10')
        self.label_component.place(380,13)
        self.label_fixed_list.add(self.label_component)
        self.label_value = Label('K-\u03A9')
        self.label_value.place(530, 13)
        self.label_fixed_list.add(self.label_value)
        self.input_box1 = InputBox(420, 10, 1, 25, text=str(''))

    def btn3_action(self):
        for r in self.res_list:
            if r.name == self.label_component.name:
                r.value = float(self.input_box1.text) * 1000
                r.update()
        for c in self.cap_list:
            if c.name == self.label_component.name:
                c.value = float(self.input_box1.text) * (10**-9)
                c.update()
        for i in self.ind_list:
            if i.name == self.label_component.name:
                i.value = float(self.input_box1.text) * (10**-9)
                i.update()

    def btn1_action(self):
        try:
            #self.execute = False
            self.nodes_list = []
            len_list = len(self.cord_lines_list)
            match_list = []
            for i in range(len_list):
                for j in range(i+1, len_list):
                    match = False
                    l1 = (self.cord_lines_list[i])
                    l2 = (self.cord_lines_list[j])
                    for a in l1:
                        for b in l2:
                            if a == b:
                                match = True
                                match_list.append((i,j))
                                break
                        if match:
                            break

            # se crea la lista de adyacencia
            ad_list = {}
            for i in range(len_list):
                ad_list[int(i)] = set([i])
            for m in match_list:
                for i in ad_list:
                    if i == m[0]:
                        ad_list[i] = ad_list[i] | {m[1]}
                    if i == m[1]:
                        ad_list[i] = ad_list[i] | {m[0]}
            # print(ad_list)
            nodes = Node.get_nodes(ad_list)
            # print(nodes)
            for k in nodes.keys():
                cords = []
                for l in nodes[k]:
                    cords = cords + self.lines_list.sprites()[l].cord
                self.nodes_list.append(Node(index=k, lines=nodes[k], cords=cords))
            # print(self.nodes_list)
            d = {}
            for t in self.ter_list:
                for n in self.nodes_list:
                    if t.cord in n.cords:
                        try:
                            d[t.component] = d[t.component] | {n.index}
                        except:
                            d[t.component] = {n.index}
                        # print("match", t.component,n.index)
            for t in self.ter_ports_list:
                # print(t.cord)
                for n in self.nodes_list:
                    # print(n.cords)
                    if t.cord in n.cords:
                        try:
                            d[t.component] = d[t.component] | {n.index}
                        except:
                            d[t.component] = {n.index}
                        # print("match", t.component,n.index)
            for i in d.keys():
                d[i] = sorted(d[i], reverse=True)
                for r in self.res_list:
                    if r.name == i:
                        d[i] = d[i] + [str(r.value)]
                for c in self.cap_list:
                    if c.name == i:
                        d[i] = d[i] + [str(c.value)]
                for ind in self.ind_list:
                    if ind.name == i:
                        d[i] = d[i] + [str(ind.value)]
            d['V1'] = d['V1'] + [0]
            d['V2'] = d['V2'] + [0]
            # print(d)
            for i in self.ter_ports_list:
                print(i.name)
            p1x, p1y = self.term_port_v1_up.cord
            p2x, p2y = self.term_port_v2_up.cord

            for i in self.nodes_list:
                if (p1x, p1y) in i.cords:
                    v1_pos = i.index
                if (p2x, p2y) in i.cords:
                    v2_pos = i.index
            print(d['V1'])
            print(d['V2'])
            if d['V1'][0] == v1_pos:
                temp = d['V1'][1]
                d['V1'][1] = d['V1'][0]
                d['V1'][0] = temp
            if d['V2'][0] == v2_pos:
                temp = d['V2'][1]
                d['V2'][1] = d['V2'][0]
                d['V2'][0] = temp
            print(d['V1'])
            print(d['V2'])
            # Write document
            file = open('net.txt', 'w')
            components = []
            for i in d.keys():
                temp = [i]
                for j in d[i]:
                    temp.append(j)
                components.append(temp)
            for i in components:
                word = ''
                for j in i:
                    word = word + ' ' + str(j)
                print(word)
                file.write(word + '\n')
            file.close()
            self.execute = True
        except:
            print('Error en funcion execute')

    def btn2_action(self):
        self.lines_list.empty()
        self.cord_lines_list.clear()
        self.res_list.empty()
        self.cap_list.empty()
        self.ind_list.empty()
        self.ter_list.empty()
        self.label_list.empty()
        self.temp_list.empty()

    @property
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            self.input_box1.handle_event(event)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.left_click_event()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.right_click_event()

            self.btn1.handle_event(event)
            self.btn2.handle_event(event)
            self.btn3.handle_event(event)

    def double_click(self):
        x_clicked, y_clicked = self.mouse_pos(self)
        for r in self.res_list:
            if r.rect.collidepoint(x_clicked, y_clicked):
                print('colide')
                screen1 = pygame.display.set_mode((500, 480), 0, 32)
                a = TextBox(screen1,'R11', 500)

            else:
                print('not')

    def run_logic(self):
        mouse_x, mouse_y = self.mouse_pos(self)
        # Create new element
        if self.element_down:
            if self.res_up:
                self.res_up = False
                new = self.temp_list.sprite
                new.place(mouse_x, mouse_y)
                self.res_list.add(new)
                self.sprites_list.add(new)
                self.sprites_list.add(new.label_name)
                self.label_list.add(new.label_name)
                self.sprites_list.add(new.label_value)
                self.label_list.add(new.label_value)
            if self.cap_up:
                self.cap_up = False
                new = self.temp_list.sprite
                new.place(mouse_x, mouse_y)
                self.cap_list.add(new)
                self.sprites_list.add(new)
                self.sprites_list.add(new.label_name)
                self.label_list.add(new.label_name)
                self.sprites_list.add(new.label_value)
                self.label_list.add(new.label_value)
            if self.ind_up:
                self.ind_up = False
                new = self.temp_list.sprite
                new.place(mouse_x, mouse_y)
                self.ind_list.add(new)
                self.sprites_list.add(new)
                self.sprites_list.add(new.label_name)
                self.label_list.add(new.label_name)
                self.sprites_list.add(new.label_value)
                self.label_list.add(new.label_value)

        if self.res_up:
            self.temp_list.sprite.place(mouse_x, mouse_y)
        if self.cap_up:
            self.temp_list.sprite.place(mouse_x, mouse_y)
        if self.ind_up:
            self.temp_list.sprite.place(mouse_x, mouse_y)


    def display_frame(self, screen):
        screen.fill(WHITE)
        self.place_grid(screen, GRAY)
        self.tmp_surface.fill((0, 0, 0, 0))
        self.display_lines(screen)
        # self.sprites_list.draw(screen)
        self.lines_list.draw(screen)
        self.ter_list.draw(screen)
        self.ter_ports_list.draw(screen)
        self.res_list.draw(screen)
        # for r in self.res_list:
        #     r.label_list.draw(screen)
        # for i in self.ind_list:
        #     i.label_list.draw(screen)
        # for c in self.cap_list:
        #     c.label_list.draw(screen)
        self.cap_list.draw(screen)
        self.ind_list.draw(screen)
        self.label_list.draw(screen)
        self.label_fixed_list.draw(screen)
        self.initial_list.draw(screen)
        self.temp_list.draw(screen)
        self.input_box1.draw(screen)
        # self.input_box2.draw(screen)
        self.input_box1.update()
        # self.input_box2.update()
        self.btn1.update()
        self.btn2.update()
        self.btn3.update()
        self.label_component.update()
        self.label_value.update()
        # --- draws ---
        self.btn1.draw(screen)
        self.btn2.draw(screen)
        self.btn3.draw(screen)
        # self.label_component.place(100, 100)

        pygame.display.flip()



    def display_lines(self, screen):
        if self.drawing_line:
            size = pygame.Vector2(pygame.mouse.get_pos()) - self.drawing_line
            x0 = self.drawing_line[0]
            y0 = self.drawing_line[1]
            w, h = self.r_pos(size[0], size[1])
            l1_cord_1, l1_cord_2, l2_cord_1, l2_cord_2 = self.cord_lines(x0, y0, w, h, side=self.side)
            pygame.draw.line(self.tmp_surface, RED, l1_cord_1, l1_cord_2, 3)
            pygame.draw.line(self.tmp_surface, RED, l2_cord_1, l2_cord_2, 3)
        # print(self.sprites_list)
        # print(self.lines_list)
        screen.blit(self.tmp_surface, (0, 0))

    def cord_lines(self, x0, y0, w, h, side):
        l1_x1 = x0
        l1_y1 = y0
        l2_x2 = x0 + w
        l2_y2 = y0 + h
        if side:
            l1_x2 = x0 + w
            l1_y2 = y0
            l2_x1 = x0 + w
            l2_y1 = y0
        else:
            l1_x2 = x0
            l1_y2 = y0 + h
            l2_x1 = x0
            l2_y1 = y0 + h
        return [l1_x1, l1_y1], [l1_x2, l1_y2], [l2_x1, l2_y1], [l2_x2, l2_y2]

    def add_terminals(self, element):
        x, y = element.rect[0], element.rect[1]
        if element.horizontal:
            x1 = x
            y1 = y + 20
            x2 = x + 80
            y2 = y1
        else:
            x1 = x + 20
            y1 = y
            x2 = x1
            y2 = y + 80
        terminal1 = Terminal(element.name, 1)
        terminal2 = Terminal(element.name, 2)
        terminal1.place(x1-4.5, y1-4.5)
        terminal2.place(x2 - 4.5, y2 - 4.5)
        # print((x1, y1))
        # print((x2, y2))
        terminal1.cord = (x1, y1)
        terminal2.cord = (x2, y2)
        self.ter_list.add(terminal1)
        self.ter_list.add(terminal2)
        self.sprites_list.add(terminal1)
        self.sprites_list.add(terminal2)

    def rotate_temp(self):
        self.temp_list.sprite.rotate()

    # Help functions
    @staticmethod
    def r_pos(x, y):
        x = (round(x / LINES_GAP) * LINES_GAP)
        y = (round(y / LINES_GAP) * LINES_GAP)
        return x, y

    @staticmethod
    def mouse_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        x, y = self.r_pos(mouse_pos[0], mouse_pos[1])
        return x, y

    @staticmethod
    def place_grid(screen, color):
        for i in range(LINES_GAP, SCREEN_WIDTH, LINES_GAP):
            pygame.draw.line(screen, color, [i, LINES_GAP * 2], [i, SCREEN_HEIGHT])
        for i in range(LINES_GAP * 2, SCREEN_HEIGHT, LINES_GAP):
            pygame.draw.line(screen, color, [0, i], [SCREEN_WIDTH, i])

    def left_click_event(self):
        # Image rotation
        if self.temp_list.sprite and not self.element_down:
            self.rotate_temp()
            self.vertical = not self.vertical
        # line invert
        if self.drawing_line:
            self.side = not self.side

    def get_internal_points(self, p1, p2):
        list_temp = []
        if p1 > p2:
            temp = p2
            p2 = p1
            p1 = temp
        steps = int((p2-p1)/20)
        for i in range(0, steps+1):
            list_temp.append(p1 + (20*i))
        return list_temp

    def save_line(self):
        l1_x1, l1_y1 = self.line_temp_x1, self.line_temp_y1
        l2_x2, l2_y2 = self.line_temp_x2, self.line_temp_y2
        if self.side:
            l1_x2 = l2_x2
            l1_y2 = l1_y1
            l2_x1 = l2_x2
            l2_y1 = l1_y1
        else:
            l1_x2 = l1_x1
            l1_y2 = l2_y2
            l2_x1 = l1_x1
            l2_y1 = l2_y2

        # print(l1_x1, l1_y1, l1_x2, l1_y2)
        # print(l2_x1, l2_y1, l2_x2, l2_y2)
        points = []
        if self.side:
            x_points_l1 = self.get_internal_points(l1_x1, l1_x2)
            y_points_l2 = self.get_internal_points(l2_y1, l2_y2)
            for x in x_points_l1:
                points.append((x, l1_y1))
            for y in y_points_l2:
                points.append((l2_x1, y))
        else:
            y_points_l1 = self.get_internal_points(l1_y1, l1_y2)
            x_points_l2 = self.get_internal_points(l2_x1, l2_x2)
            for y in y_points_l1:
                points.append((l1_x1, y))

            for x in x_points_l2:
                points.append((x, l2_y1))
        self.cord_lines_list.append(points)
        for i in points:
            self.all_cord.append(i)
        return points

    def right_click_event(self):
        x_clicked, y_clicked = self.mouse_pos(self)
        clicked = (x_clicked, y_clicked)
        # Create line
        if not self.element_up:
            cords_list = []
            for r in self.res_list:
                x1_rec, y1_rec, x2_rec, y2_rec = r.rect
                if r.horizontal:
                    cords = [(x1_rec+20,y1_rec),(x1_rec+40,y1_rec),(x1_rec+60,y1_rec),(x1_rec+20,y1_rec+20),(x1_rec+40,y1_rec+20),(x1_rec+60,y1_rec+20),(x1_rec+20,y1_rec+40), (x1_rec+40,y1_rec+40), (x1_rec+60,y1_rec+40)]
                else:
                    cords = [(x1_rec,y1_rec+20),(x1_rec,y1_rec+40),(x1_rec,y1_rec+60),(x1_rec+20,y1_rec+20),(x1_rec+20,y1_rec+40),(x1_rec+20,y1_rec+60),(x1_rec+40,y1_rec+20),(x1_rec+40,y1_rec+40),(x1_rec+40,y1_rec+60)]
                cords_list = cords_list + cords
                if clicked in cords:
                    print(r.horizontal)
                    # self.input_box1.set_text(str(r.value/1000))
                    self.input_box1.set_text('')
                    self.label_component.name = r.name
                    self.label_value.name = 'K-Ohm'
            for c in self.cap_list:
                x1_rec, y1_rec, x2_rec, y2_rec = c.rect
                if c.horizontal:
                    cords = [(x1_rec+20,y1_rec),(x1_rec+40,y1_rec),(x1_rec+60,y1_rec),(x1_rec+20,y1_rec+20),(x1_rec+40,y1_rec+20),(x1_rec+60,y1_rec+20),(x1_rec+20,y1_rec+40), (x1_rec+40,y1_rec+40), (x1_rec+60,y1_rec+40)]
                else:
                    cords = [(x1_rec,y1_rec+20),(x1_rec,y1_rec+40),(x1_rec,y1_rec+60),(x1_rec+20,y1_rec+20),(x1_rec+20,y1_rec+40),(x1_rec+20,y1_rec+60),(x1_rec+40,y1_rec+20),(x1_rec+40,y1_rec+40),(x1_rec+40,y1_rec+60)]
                cords_list = cords_list + cords
                if clicked in cords:
                    # self.input_box1.set_text(str(c.value * (10**9)))
                    self.input_box1.set_text('')
                    self.label_component.name = c.name
                    self.label_value.name = 'nF'
            for i in self.ind_list:
                x1_rec, y1_rec, x2_rec, y2_rec = i.rect
                if i.horizontal:
                    cords = [(x1_rec+20,y1_rec),(x1_rec+40,y1_rec),(x1_rec+60,y1_rec),(x1_rec+20,y1_rec+20),(x1_rec+40,y1_rec+20),(x1_rec+60,y1_rec+20),(x1_rec+20,y1_rec+40), (x1_rec+40,y1_rec+40), (x1_rec+60,y1_rec+40)]
                else:
                    cords = [(x1_rec,y1_rec+20),(x1_rec,y1_rec+40),(x1_rec,y1_rec+60),(x1_rec+20,y1_rec+20),(x1_rec+20,y1_rec+40),(x1_rec+20,y1_rec+60),(x1_rec+40,y1_rec+20),(x1_rec+40,y1_rec+40),(x1_rec+40,y1_rec+60)]
                cords_list = cords_list + cords
                if clicked in cords:
                    # self.input_box1.set_text(str(i.value * (10**9)))
                    self.input_box1.set_text('')
                    self.label_component.name = i.name
                    self.label_value.name = 'nH'

            if SCREEN_HEIGHT > y_clicked > LINES_GAP*2 and SCREEN_WIDTH > x_clicked > 0 and clicked not in cords_list:
                # print(x_clicked,y_clicked)
                # if self.check_collide(x_clicked,y_clicked):
                if not self.drawing_line:
                    self.line_temp = Line(SIZE)
                    self.line_temp_x1 = x_clicked
                    self.line_temp_y1 = y_clicked
                    self.drawing_line = [x_clicked, y_clicked]
                    # self.hit_line = False
                    # self.hit_terminal = False
                else:
                    self.line_temp_x2 = x_clicked
                    self.line_temp_y2 = y_clicked
                    self.drawing_line = None
                    self.line_temp.patch(self.tmp_surface)
                    cord = self.save_line()
                    self.line_temp.set_cord(cord)
                    self.lines_list.add(self.line_temp)
                    self.sprites_list.add(self.line_temp)

        # Create new element
        if not self.element_up:
            if self.res.rect.collidepoint(x_clicked, y_clicked):
                self.res_up = True
                self.element_down = False
                self.element_up = True
                pygame.mouse.set_visible(0)
                num = len(self.res_list)
                self.element_temp = Resistor('R' + str(num), 1000)
                self.temp_list.add(self.element_temp)
            if self.cap.rect.collidepoint(x_clicked, y_clicked):
                self.cap_up = True
                self.element_down = False
                self.element_up = True
                pygame.mouse.set_visible(0)
                num = len(self.cap_list)
                self.element_temp = Capacitor('C' + str(num), float(10**-9))
                self.temp_list.add(self.element_temp)
            if self.ind.rect.collidepoint(x_clicked, y_clicked):
                self.ind_up = True
                self.element_down = False
                self.element_up = True
                pygame.mouse.set_visible(0)
                num = len(self.ind_list)
                self.element_temp = Inductor('L' + str(num), float(10**-9))
                self.temp_list.add(self.element_temp)
        else:
            self.element_down = True
            self.element_up = False
            self.add_terminals(self.temp_list.sprite)
            pygame.mouse.set_visible(1)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    a = pygame.image.load('icon4.png')
    pygame.display.set_icon(a)
    pygame.display.set_caption('Parameters')
    clock = pygame.time.Clock()
    app = App()
    done = False

    while not done:
        done = app.process_events
        app.run_logic()
        app.display_frame(screen)
        clock.tick(60)
    pygame.quit()

    pass


if __name__ == '__main__':
    main()
