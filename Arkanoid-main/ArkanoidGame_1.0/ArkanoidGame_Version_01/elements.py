# elements.py

import pygame
from settings import WHITE, SILVER, BALL_RADIUS, BALL_SPEED_X, BALL_SPEED_Y, PADDLE_SECTION_WIDTH, PADDLE_HEIGHT

# Clase de Paddle (la raqueta)
class Paddle:
    def __init__(self, paddle_positions, game_area_height):
        self.width = PADDLE_SECTION_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = paddle_positions[1]  # Iniciamos en "Izquierda Media"
        self.y = game_area_height - 30  # Ajustamos la posición del paddle dentro del área de juego
        self.positions = paddle_positions  # Posiciones predefinidas

    def move_to(self, index):
        self.x = self.positions[index]

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height))

# Clase para la pelota
class Ball:
    def __init__(self, window_width, game_area_height):
        self.window_width = window_width
        self.game_area_height = game_area_height
        self.radius = BALL_RADIUS
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y
        self.reset()

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def bounce(self, axis):
        if axis == 'x':
            self.speed_x *= -1
        elif axis == 'y':
            self.speed_y *= -1

    def reset(self):
        self.x = self.window_width // 2
        self.y = self.game_area_height // 2
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y

    def draw(self, surface):
        pygame.draw.circle(surface, SILVER, (self.x, self.y), self.radius)  # Usamos gris metálico

# Clase de Bloque (Brick)
class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color  # Color del bloque

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
