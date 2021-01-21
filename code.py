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
        self.money = 30
        self.food = 10
        self.spend_food = 0
        self.figures = []
        self.towers = [0] * 4

    def get_food(self):
        return str(self.spend_food) + '/' + str(self.food)


class Figure:
    def __init__(self, board, pos, color):
        self.board = board
        self.pos = pos
        self.color = color
        self.name = '0'
        self.coords = board.to_real(pos[0], 'x'), board.to_real(pos[1], 'y')
        self.moving = False


class Swordsman(Figure):
    def __init__(self, board, pos, color):
        super(Swordsman, self).__init__(board, pos, color)
        self.name = 'мечник'
        self.food = 1
        self.hps = 2
        self.dmg = 1
        self.money = 2

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

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        if self.marker is not None:
            x, y = self.marker
            image = load_image("выделение_1.png")
            image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
            screen.blit(image, (self.to_real(x, 'x'), self.to_real(y, 'y')))
        if self.player == 1:
            pygame.draw.rect(screen, (0, 0, 255), ((0, 0), (self.cell_size * 3, self.cell_size)), 5)
        else:
            pygame.draw.rect(screen, (255, 0, 0), ((self.cell_size * 12, 0), (self.cell_size * 4, self.cell_size)), 5)

        text_size = self.cell_size // 5 * 2
        font = pygame.font.SysFont('Comic Sans MS', text_size)
        text = font.render(str(self.players[0].money), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 4 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))
        font = pygame.font.SysFont('Comic Sans MS', text_size)
        text = font.render(str(self.players[0].get_food()), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 6 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))
        font = pygame.font.SysFont('Comic Sans MS', text_size)
        text = font.render(str(self.players[1].money), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 9 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))
        font = pygame.font.SysFont('Comic Sans MS', text_size)
        text = font.render(str(self.players[1].get_food()), True, (0, 0, 0))
        screen.blit(text, (self.cell_size * 11 + (self.cell_size - text.get_width()) // 2,
                           (self.cell_size - text.get_height()) // 2))

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
            x, y = cell_coords
            self.marker = x, y
            cell = self.board[y][x]
            new_figure = Swordsman(self, (x, y), self.player)
            if cell == 0 and (x == 0 and self.player == 1 or x == 7 and self.player == 2)\
                    and self.players[self.player - 1].food  - self.players[self.player - 1].spend_food\
                    >= new_figure.food \
                    and self.players[self.player - 1].money >= new_figure.money:
                self.board[y][x] = new_figure
                self.players[self.player - 1].spend_food += new_figure.food
                self.players[self.player - 1].money -= new_figure.money
                if self.player == 1:
                    self.player = 2
                else:
                    self.player = 1

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        if x < self.left or y < self.top \
                or x > self.left + self.width * self.cell_size \
                or y > self.top + self.height * self.cell_size:
            return None
        return (x - self.left) // self.cell_size, (y - self.top) // self.cell_size

    def to_real(self, coord, type):
        if type == 'x':
            return coord * board.cell_size + board.left
        else:
            return coord * board.cell_size + board.top


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
    image = load_image("фон.png")
    image = pygame.transform.scale(image, size)
    screen.blit(image, (0, 0))
    board.render(screen)
    pygame.display.flip()
pygame.quit()
