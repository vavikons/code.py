import pygame
import os
import sys


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        fullname = os.path.join('data', 'not_found.png')
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    return image


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
        self.food = sum(self.fields)

    def get_food(self):
        return str(self.spend_food) + '/' + str(self.food)


class Figure:
    def __init__(self, board, pos, color, name, food, hps, dmg, radius, money):
        self.board = board
        self.pos = pos
        self.color = color
        self.name = name
        self.food = food
        self.hps = hps
        self.dmg = dmg
        self.radius = radius
        self.money = money
        self.name = name
        self.coords = board.to_real(pos[0], 'x'), board.to_real(pos[1], 'y')
        self.moving = False

    def get_name(self):
        return self.name + '_' + str(self.color) + '_1' + '.png'


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.board = [[0] * width for _ in range(height)]
        self.player = 1
        self.players = [Player(Board), Player(Board)]
        self.canmove = True
        self.marker = None
        self.variants = []

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        # Выделение ходящего игрока
        if self.player == 1:
            pygame.draw.rect(screen, (0, 0, 255), ((0, 0), (self.cell_size * 3, self.cell_size)), 5)
        else:
            pygame.draw.rect(screen, (255, 0, 0), ((self.cell_size * 12, 0), (self.cell_size * 4, self.cell_size)), 5)

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
            image = load_image(f'поле_{elem}.png')
            image = pygame.transform.scale(image, (self.cell_size * 4, self.cell_size * 2))
            screen.blit(image, (cell_size, cell_size * 2 + i * cell_size * 2))

        # Башни
        for i, playeri in enumerate(self.players):
            for j, towerj in enumerate(playeri.towers):
                name = ''
                if towerj > 2:
                    name = "башня_1.png"
                elif towerj > 0:
                    name = "башня_2.png"
                if name != '':
                    image = load_image(name)
                    image = pygame.transform.scale(image, (self.cell_size, self.cell_size * 2))
                    screen.blit(image, (cell_size * 6 + i * cell_size * 9,
                                        cell_size + j * cell_size * 2))

        # Выделение
        if self.marker is not None:
            x, y = self.marker
            image = load_image("выделение_1.png")
            image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
            screen.blit(image, (self.to_real(x, 'x'), self.to_real(y, 'y')))
            if self.can_place(self.board[y][x], x, y):
                a = Figure(self, (x, y), self.player, 'мечник', 1, 2, 1, 1, 2)
                b = Figure(self, (x, y), self.player, 'копейщик', 1, 2, 2, 1, 4)
                c = Figure(self, (x, y), self.player, 'всадник', 2, 3, 1, 2, 4)
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
                        image = pygame.transform.scale(image, (self.cell_size // 3, self.cell_size // 3))
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

        # Фигуры на поле
        for i in range(self.height):
            y = self.to_real(i, 'y')
            for j in range(self.width):
                x = self.to_real(j, 'x')
                obj = self.board[i][j]
                if obj != 0:
                    image = load_image(obj.get_name())
                    image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
                    if obj.color == 2:
                        image = flip(image)
                    screen.blit(image, obj.coords)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def on_click(self, cell_coords):
        if cell_coords is not None:
            if 6 < cell_coords[0] < 15 and 0 < cell_coords[0]:
                x, y = cell_coords
                x -= 7
                y -= 1
                if self.can_place(self.board[y][x], x, y) or self.board[y][x] != 0 and \
                        self.board[y][x].color == self.player:
                    self.marker = x, y

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        if x < 0 or y < 0 or x > self.cell_size * 16 or y > self.cell_size * 9:
            return None
        return x // self.cell_size, y // self.cell_size

    def to_real(self, coord, type):
        if type == 'x':
            return coord * board.cell_size + board.left
        else:
            return coord * board.cell_size + board.top

    def can_place(self, cell, x, y):
        if cell == 0 and (x == 0 and self.player == 1 or x == 7 and self.player == 2)\
                and self.players[self.player - 1].towers[y // 2] > 0:
            return True
        return False

    def get_key(self, key):
        if len(self.variants) > 0 and \
                key in ''.join(list(map(str, range(1, len(self.variants) + 1)))):
            x, y = self.marker
            new_figure = self.variants[int(key) - 1]
            self.board[y][x] = new_figure
            self.players[self.player - 1].spend_food += new_figure.food
            self.players[self.player - 1].money -= new_figure.money
            if self.player == 1:
                self.player = 2
            else:
                self.player = 1
                for i in self.players:
                    i.money += 1
            self.variants = []


pygame.init()
cell_size = 90
size = width, height = cell_size * 16, cell_size * 9
screen = pygame.display.set_mode(size, pygame.SRCALPHA)
board = Board(8, 8)
board.set_view(cell_size * 7, cell_size, cell_size)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
        if event.type == pygame.KEYDOWN:
            board.get_key(event.unicode)
    image = load_image("фон.png")
    image = pygame.transform.scale(image, size)
    screen.blit(image, (0, 0))
    board.render(screen)
    pygame.display.flip()
pygame.quit()
