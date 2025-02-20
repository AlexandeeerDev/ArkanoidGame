import pygame
from settings import COLORS, BALL_RADIUS, BALL_SPEED_X, BALL_SPEED_Y, PADDLE_SECTION_WIDTH, PADDLE_HEIGHT

# Clase que representa la raqueta (Paddle) controlada por el jugador
class Paddle:
    def __init__(self, paddle_positions, game_area_height):
        """Inicializa el Paddle con las posiciones predefinidas y su tamaño."""
        self.width = PADDLE_SECTION_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = paddle_positions[1]  # Inicia en la posición "Izquierda Media"
        self.y = game_area_height - 30  # Ajusta la posición dentro del área de juego
        self.positions = paddle_positions  # Posiciones predefinidas del paddle

    def move_to(self, index):
        """Mueve el paddle a la posición index en la lista de posiciones."""
        self.x = self.positions[index]

    def draw(self, surface):
        """Dibuja el paddle en la pantalla."""
        pygame.draw.rect(surface, COLORS['WHITE'], (self.x, self.y, self.width, self.height))


# Clase que representa la pelota del juego
class Ball:
    def __init__(self, window_width, game_area_height):
        """Inicializa la pelota con la velocidad y posición inicial."""
        self.window_width = window_width
        self.game_area_height = game_area_height
        self.radius = BALL_RADIUS
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y
        self.reset()  # Establece la posición inicial

    def move(self):
        """Mueve la pelota según su velocidad actual."""
        self.x += self.speed_x
        self.y += self.speed_y

    def bounce(self, axis):
        """Cambia la dirección de la pelota en el eje dado ('x' o 'y')."""
        if axis == 'x':
            self.speed_x *= -1
        elif axis == 'y':
            self.speed_y *= -1

    def reset(self):
        """Restablece la pelota a su posición inicial en el centro del área de juego."""
        self.x = self.window_width // 2
        self.y = self.game_area_height // 2
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y

    def draw(self, surface):
        """Dibuja la pelota en la pantalla."""
        pygame.draw.circle(surface, COLORS['SILVER'], (self.x, self.y), self.radius)


# Clase que representa los bloques (Bricks) que el jugador debe destruir
class Brick:
    def __init__(self, x, y, width, height, color):
        """Inicializa un bloque con su posición, tamaño y color."""
        self.rect = pygame.Rect(x, y, width, height)  # Define el rectángulo del bloque
        self.color = color  # Color del bloque

    def draw(self, surface):
        """Dibuja el bloque en la pantalla."""
        pygame.draw.rect(surface, self.color, self.rect)
