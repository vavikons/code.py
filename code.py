import pygame
import os
import sys


def load_image(name, extension='.png'):
    fullname = os.path.join('pictures', name)
    fullname += extension
    if not os.path.isfile(fullname):
        fullname = os.path.join('data', 'not_found.png')
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    return image


def load_sound(name, extension='.mp3'):
    fullname = os.path.join('sound', name)
    fullname += extension
    sound = pygame.mixer.Sound(fullname)
    sound.play()


def scale(image, size):
    return pygame.transform.scale(image, size)


def flip(image):
    return pygame.transform.flip(image, True, False)


class Player:
    def __init__(self, board):
        self.board = board
        self.money = 10
        self.spend_food = 0
        self.figures = []
        self.towers = [4] * 4
        self.fields = [1] * 3
        self.food = sum(self.fields) * 2

    def get_food(self):
        return str(self.spend_food) + '/' + str(self.food)


class Figure:
    def __init__(self, board, pos, color, name, food, hps, hits, steps, money):
        self.board = board
        self.pos = pos
        self.color = color
        self.name = name
        self.food = food
        self.hps = hps
        self.hits = hits
        self.steps = steps
        self.money = money
        self.name = name
        self.coords = [board.to_real(pos[0], 'x'), board.to_real(pos[1], 'y')]
        self.moving = False

    def get_name(self, num=1):
        return self.name + '_' + str(self.color) + '_' + str(num) + ''

    def __repr__(self):
        return f'name=Figure({self.name}, color={self.color}, coords={self.coords})'

    def can_attack(self, obj, x, y):
        if self is obj or obj == 0:
            return False
        if abs(self.pos[0] - x) + abs(self.pos[1] - y) <= 1\
                and self.color != obj.color:
            return True
        return False

    def can_go_to(self, obj, x, y):
        if self is obj or obj != 0:
            return False
        if abs(self.pos[0] - x) + abs(self.pos[1] - y) <= 1:
            return True
        return False


class Board:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.left = cell_size * 7
        self.top = cell_size
        self.cell_size = cell_size

        self.board = [[0] * width for _ in range(height)]
        self.player = 1
        self.players = [Player(Board), Player(Board)]
        self.figures = []

        self.canmove = True
        self.marker = None

        self.marker_fig = None
        self.fig_steps = 0
        self.direction = [0, 0]
        self.run_count = 0

        self.fig_hits = 0
        self.hit_count = 0
        self.enemy = None

        self.tower = None

        self.field_marker = None
        self.variants = []

    def render(self, screen):
        # Выделение ходящего игрока
        if self.player == 1:
            pygame.draw.rect(screen, (0, 0, 255), ((0, 0), (self.cell_size * 7, self.cell_size)), 5)
        else:
            pygame.draw.rect(screen, (255, 0, 0), ((self.cell_size * 8, 0), (self.cell_size * 8, self.cell_size)), 5)

        # Количсетво предметов у игроков
        text_size = self.cell_size // 5 * 2
        font = pygame.font.SysFont('Comic Sans MS', text_size)
        text = font.render(str(self.players[0].money), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 4 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))
        text = font.render(str(self.players[0].get_food()), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 6 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))
        text = font.render(str(self.players[1].money), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 9 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))
        text = font.render(str(self.players[1].spend_food), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 11 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))

        # Поля
        for i, elem in enumerate(self.players[0].fields):
            if self.field_marker == i:
                image = load_image("выделение_1")
                image = scale(image, (self.cell_size * 4, self.cell_size * 2))
                screen.blit(image, (cell_size, cell_size * 2 + i * cell_size * 2))

            image = load_image(f'поле_{elem}')
            image = scale(image, (self.cell_size * 4, self.cell_size * 2))
            screen.blit(image, (cell_size, cell_size * 2 + i * cell_size * 2))

            text = font.render(str(elem) + '/3', True, (0, 0, 0))
            screen.blit(text, (cell_size * 3 // 4, cell_size * 2 + i * cell_size * 2))

        # Башни
        for i, playeri in enumerate(self.players):
            for j, towerj in enumerate(playeri.towers):
                if self.tower is not None and self.tower == [j, i + 1]:
                    image = load_image("выделение_1")
                    image = scale(image, (self.cell_size, int(self.cell_size * 2)))
                    screen.blit(image, (cell_size * 6 + i * cell_size * 9,
                                        cell_size + j * cell_size * 2))
                name = ''
                if towerj > 0:
                    name = f"башня_{towerj}"
                if name != '':
                    image = load_image(name)
                    image = scale(image, (self.cell_size, int(self.cell_size * 2.5)))
                    screen.blit(image, (cell_size * 6 + i * cell_size * 9,
                                        cell_size + j * cell_size * 2))

        # Выделение
        if self.marker is not None:
            x, y = self.marker
            cell = self.board[y][x]
            image = load_image("выделение_1")
            image = scale(image, (self.cell_size, self.cell_size))
            screen.blit(image, (self.to_real(x, 'x'), self.to_real(y, 'y')))
            if self.can_place(cell, x, y) and self.marker_fig is None:
                a = Figure(self, [x, y], self.player, 'мечник', 1, 2, 1, 1, 2)
                b = Figure(self, [x, y], self.player, 'всадник', 2, 3, 1, 2, 4)
                c = Figure(self, [x, y], self.player, 'копейщик', 1, 2, 2, 1, 6)
                good = []
                for i in [a, b, c]:
                    if self.players[self.player - 1].food - self.players[self.player - 1].spend_food \
                           >= i.food \
                            and self.players[self.player - 1].money >= i.money:
                        good.append(i)
                if len(good) > 0:
                    size = int((3 - len(good)) / 6 * self.cell_size)
                    for i, elem in enumerate(good):
                        image = load_image(elem.get_name())
                        image = scale(image, (self.cell_size // 3, self.cell_size // 3))
                        screen.blit(image, (self.to_real(x, 'x') + size + i * self.cell_size // 3,
                                            self.to_real(y, 'y')))
                    if x == 0:
                        color = (0, 0, 255)
                    else:
                        color = (255, 0, 0)
                    text = font.render(''.join(list(map(str, range(1, len(good) + 1)))), True, color)
                    screen.blit(text, (self.to_real(x, 'x') + (self.cell_size - text.get_width()) // 2,
                                       self.to_real(y, 'y') + text.get_height() // 2))
                    self.variants = good
                else:
                    self.marker = None
            elif cell != 0:
                for i in range(self.height):
                    for j in range(self.width):
                        obj = self.board[i][j]
                        if cell.can_attack(obj, j, i):
                            image = load_image("выделение_2")
                            image = scale(image, (self.cell_size, self.cell_size))
                            screen.blit(image, (self.to_real(j, 'x'), self.to_real(i, 'y')))
                        elif cell.can_go_to(obj, j, i):
                            image = load_image("выделение_3")
                            image = scale(image, (self.cell_size, self.cell_size))
                            screen.blit(image, (self.to_real(j, 'x'), self.to_real(i, 'y')))

        # Фигуры на поле
        for obj in self.figures:
            hit = False
            rotate = 0
            if obj == self.marker_fig:
                if self.direction != [0, 0]:
                    image = load_image(obj.get_name(self.run_count + 2))
                    if self.direction[0] == 1 and self.player == 2 or \
                            self.direction[0] == -1 and self.player == 1:
                        image = flip(image)
                elif self.hit_count > 0:
                    if self.hit_count % 2 > 0:
                        image = load_image(obj.get_name(4))
                        hit = True
                    else:
                        image = load_image(obj.get_name())
                    if self.tower is None and (self.enemy.pos[0] > obj.pos[0] and self.player == 2 or
                       self.enemy.pos[0] < obj.pos[0] and self.player == 1):
                        image = flip(image)
                        rotate += 1
                else:
                    image = load_image(obj.get_name())
            else:
                image = load_image(obj.get_name())
            if hit:
                image = scale(image, (int(self.cell_size * 1.5), self.cell_size))
            else:
                image = scale(image, (self.cell_size, self.cell_size))
            if obj.color == 2:
                image = flip(image)
                rotate += 1
            if hit and rotate % 2 > 0:
                screen.blit(image, (obj.coords[0] - int(cell_size * 0.5), obj.coords[1]))
            else:
                screen.blit(image, obj.coords)
            hp = obj.hps
            for m in range(hp):
                image = load_image('сердце')
                image = scale(image, (self.cell_size // 6, self.cell_size // 6))
                screen.blit(image, (obj.coords[0] + m * self.cell_size // 6,
                                    obj.coords[1]))

        # Еще выделение
        if self.marker is not None:
            x, y = self.marker
            cell = self.board[y][x]
            if not self.can_place(cell, x, y):
                if self.marker_fig is None:
                    obj = cell
                    steps_hits = ['шаги'] * obj.steps + ['атака'] * obj.hits
                else:
                    steps_hits = ['шаги'] * self.fig_steps + ['атака'] * self.fig_hits
                for i, elem in enumerate(steps_hits):
                    image = load_image(elem)
                    image = scale(image, (self.cell_size // 3, self.cell_size // 3))
                    screen.blit(image, (cell.coords[0] + i * self.cell_size // 3,
                                        cell.coords[1] + self.cell_size // 3 * 2))

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def on_click(self, cell_coords):
        if cell_coords is not None and self.canmove:
            if 6 < cell_coords[0] < 15 and 0 < cell_coords[1]:
                x, y = cell_coords
                x -= 7
                y -= 1
                if self.marker is not None:
                    cell = self.board[self.marker[1]][self.marker[0]]
                    new_cell = self.board[y][x]
                    if cell != 0 and cell.can_go_to(new_cell, x, y) and cell.color == self.player:
                        if self.marker_fig is None:
                            self.marker_fig = cell
                            self.fig_steps = self.marker_fig.steps
                            self.fig_hits = self.marker_fig.hits
                        if self.fig_steps > 0:
                            self.canmove = False
                            self.direction = [x - self.marker[0], y - self.marker[1]]
                            self.marker = None
                            load_sound('шаги')
                            pygame.time.set_timer(MYEVENTTYPE, SPEED)
                    elif cell != 0 and new_cell != 0 and cell.can_attack(new_cell, x, y):
                        if self.marker_fig is None:
                            self.marker_fig = self.board[self.marker[1]][self.marker[0]]
                            self.fig_steps = 0
                            self.fig_hits = self.marker_fig.hits
                        if self.fig_hits > 0:
                            self.canmove = False
                            self.hit_count = 24
                            self.enemy = new_cell
                            load_sound('удары')
                            pygame.time.set_timer(MYEVENTTYPE, SPEED)
                if self.can_place(self.board[y][x], x, y) or self.board[y][x] != 0 and \
                        self.board[y][x].color == self.player:
                    self.marker = x, y
            elif (cell_coords[0] == 6 and 0 < cell_coords[1] and self.player == 2 or
                    cell_coords[0] == 15 and 0 < cell_coords[1] and self.player == 1)\
                    and self.marker_fig is None and self.marker is not None:
                x, y = cell_coords
                x -= 7
                y -= 1
                tower = y // 2
                cell = self.board[self.marker[1]][self.marker[0]]
                if cell != 0 and abs(cell.pos[0] - x) == 1 and\
                        self.players[self.player - 1].towers[tower] > 0:
                    if self.player == 1 and cell.pos[0] == 7:
                        self.marker_fig = cell
                        self.canmove = False
                        self.fig_hits = 1
                        self.hit_count = 24
                        self.tower = [tower, 2]
                        load_sound('удары_башня')
                        pygame.time.set_timer(MYEVENTTYPE, SPEED)
                    elif self.player == 2 and cell.pos[0] == 0:
                        self.marker_fig = cell
                        self.canmove = False
                        self.fig_hits = 1
                        self.hit_count = 24
                        self.tower = [tower, 1]
                        load_sound('удары_башня')
                        pygame.time.set_timer(MYEVENTTYPE, SPEED)
            elif 0 < cell_coords[0] < 5 and 1 < cell_coords[1] < 8:
                field_coords = (cell_coords[1] - 2) // 2
                if self.field_marker is None or self.field_marker != field_coords:
                    self.field_marker = field_coords
                elif self.field_marker == field_coords and self.players[0].money >= 10\
                        and self.players[0].fields[field_coords] < 3:
                    self.players[0].fields[field_coords] += 1
                    self.players[0].food = sum(self.players[0].fields) * 2
                    self.players[0].money -= 10
                    self.field_marker = None
                else:
                    self.field_marker = None
            elif cell_coords[0] == 5 and cell_coords[1] == 1 and (self.player == 1 or not AI):
                self.marker_fig = None
                self.fig_steps = 0
                self.direction = [0, 0]
                self.run_count = 0

                self.fig_hits = 0
                self.hit_count = 0
                self.enemy = None

                self.tower = None
                self.change_player()
                pygame.time.set_timer(MYEVENTTYPE, 0)
            elif cell_coords[0] == 0 and cell_coords[1] == 1:
                info_screen(board)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        if x < 0 or y < 0 or x > self.cell_size * 16 or y > self.cell_size * 9:
            return None
        return x // self.cell_size, y // self.cell_size

    def get_key(self, unicode, key):
        if self.canmove:
            if len(self.variants) > 0 and \
                    unicode.ljust(1, '-') in ''.join(list(map(str, range(1, len(self.variants) + 1)))):
                x, y = self.marker
                new_figure = self.variants[int(unicode) - 1]
                self.board[y][x] = new_figure
                self.figures.append(new_figure)
                self.players[self.player - 1].spend_food += new_figure.food
                self.players[self.player - 1].money -= new_figure.money
                self.change_player()
                self.variants = []
        if key == 27:
            terminate()

    def myevent(self):
        if self.marker_fig is not None:
            fig = self.marker_fig
            x, y = self.to_real(fig.pos[0], 'x'), self.to_real(fig.pos[1], 'y')
            if self.direction != [0, 0]:
                if abs(fig.coords[0] - x) >= cell_size or abs(fig.coords[1] - y) >= cell_size:
                    self.canmove = True
                    self.fig_steps -= 1
                    self.board[fig.pos[1]][fig.pos[0]] = 0
                    fig.pos[0] += self.direction[0]
                    fig.pos[1] += self.direction[1]
                    fig.coords = [self.to_real(fig.pos[0], 'x'), self.to_real(fig.pos[1], 'y')]
                    self.run_count = 0
                    self.board[fig.pos[1]][fig.pos[0]] = fig
                    self.direction = [0, 0]
                    self.marker = [fig.pos[0], fig.pos[1]]
                    pygame.time.set_timer(MYEVENTTYPE, 0)
                else:
                    self.run_count = (self.run_count + 1) % 2
                    fig.coords[0] += self.cell_size // 10 * self.direction[0]
                    fig.coords[1] += self.cell_size // 10 * self.direction[1]
            elif self.enemy is not None:
                self.hit_count -= 1
                if self.hit_count == 0:
                    self.canmove = True
                    self.enemy.hps -= 1
                    if self.enemy.hps == 0:
                        x, y = self.enemy.pos
                        self.board[y][x] = 0
                        self.figures.remove(self.enemy)
                        self.players[self.enemy.color - 1].spend_food -= self.enemy.food
                    self.fig_steps = 0
                    self.fig_hits -= 1
                    self.marker = [fig.pos[0], fig.pos[1]]
                    pygame.time.set_timer(MYEVENTTYPE, 0)
            elif self.tower is not None:
                self.hit_count -= 1
                if self.hit_count == 0:
                    self.canmove = True
                    self.players[self.player - 2].towers[self.tower[0]] -= 1
                    self.fig_steps = 0
                    self.fig_hits = 0
                    self.tower = None
                    self.marker = [fig.pos[0], fig.pos[1]]
                    pygame.time.set_timer(MYEVENTTYPE, 0)
            if self.tower is None:
                x, y = fig.pos[0], fig.pos[1]
                enemies = False
                for i, j in [[-1, 0], [0, -1], [1, 0], [0, 1]]:
                    if 0 <= y + i <= 7 and 0 <= x + j <= 7 and \
                            self.board[y + i][x + j] != 0 and \
                            self.board[y + i][x + j].color != self.player:
                        enemies = True
                        break
                if self.tower is not None:
                    enemies = True
                if self.fig_steps == 0 and (self.fig_hits == 0 or enemies is False):
                    self.marker_fig = None
                    self.change_player()
                    pygame.time.set_timer(MYEVENTTYPE, 0)

    def to_real(self, coord, type):
        if type == 'x':
            return coord * self.cell_size + self.left
        else:
            return coord * self.cell_size + self.top

    def can_place(self, cell, x, y):
        if cell == 0 and (x == 0 and self.player == 1 or x == 7 and self.player == 2)\
                and self.players[self.player - 1].towers[y // 2] > 0:
            return True
        return False

    def change_player(self):
        self.marker = None
        if self.player == 1:
            self.player = 2
            if AI:
                print('ИИ в разработке')
        else:
            self.player = 1
            for i in self.players:
                i.money += 1


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    screen.fill((0, 153, 0))
    image = load_image("стартовый_фон")
    image = scale(image, size)
    screen.blit(image, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def info_screen(board):
    board.canmove = False
    page = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                cell = board.get_cell(event.pos)
                if cell[0] == 15 and cell[1] == 0:
                    board.canmove = True
                    return
                elif page == 1 and cell[0] == 15 and cell[1] == 8:
                    page = 2
                elif page == 2 and cell[0] == 0 and cell[1] == 8:
                    page = 1
        screen.fill((205, 183, 135))
        image = load_image(f"правила_фон_{page}")
        image = scale(image, size)
        screen.blit(image, (0, 0))
        pygame.display.flip()


def end_screen(board):
    screen.fill((0, 153, 0))
    if sum(board.players[0].towers) == 0:
        name = 'конечный_фон_1'
    else:
        name = 'конечный_фон_2'
    image = load_image(name)
    image = scale(image, size)
    screen.blit(image, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
            if event.type == pygame.KEYDOWN:
                board.get_key(event.unicode, event.key)
            if event.type == MYEVENTTYPE:
                board.myevent()
        screen.fill((0, 153, 0))
        image = load_image("фон")
        image = scale(image, size)
        screen.blit(image, (0, 0))
        board.render(screen)
        pygame.display.flip()
        if sum(board.players[0].towers) == 0 or \
                sum(board.players[1].towers) == 0:
            end_screen(board)
            break


pygame.init()
pygame.mixer.music.load('sound/фон.mid')
pygame.mixer.music.play()
AI = True
SPEED = 50
MYEVENTTYPE = pygame.USEREVENT + 1
infoObject = pygame.display.Info()
cell_size = min([infoObject.current_w // 16, infoObject.current_h // 9])
size = width, height = cell_size * 16, cell_size * 9
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
start_screen()
board = Board(8, 8, cell_size)

main()
pygame.quit()
