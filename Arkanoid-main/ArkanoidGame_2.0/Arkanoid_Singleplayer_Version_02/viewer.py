import pygame
import socket
import json
from settings import *
from game import draw_text_centered

# Inicialización de Pygame y configuración de ventana
def initialize_viewer_window():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, GAME_AREA_HEIGHT))
    pygame.display.set_caption("Arkanoid Viewer")
    return window

# Función para recibir datos desde el socket
def receive_game_state(sock):
    try:
        sock.settimeout(1.0)  # Evitar que el socket se bloquee indefinidamente
        data, _ = sock.recvfrom(4096)
        if data.decode() == 'EXIT':
            return 'EXIT'
        return json.loads(data.decode())  # Decodificar datos JSON si son válidos
    except socket.timeout:
        return None  # Si no hay datos, sigue esperando
    except json.JSONDecodeError:
        return None  # Si los datos son inválidos, ignóralos

# Dibuja mensaje de espera
def draw_waiting_message(window, font):
    window.fill(COLORS['BLACK'])
    draw_text_centered("Esperando que comience la partida", font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2)
    pygame.display.update()

# Dibuja los elementos del juego en pantalla
def draw_game_elements(window, game_state):
    window.fill(COLORS['BLACK'])
    pygame.draw.rect(window, COLORS['WHITE'], (game_state['paddle_x'], game_state['paddle_y'], PADDLE_SECTION_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(window, COLORS['SILVER'], (game_state['ball_x'], game_state['ball_y']), BALL_RADIUS)
    for brick_x, brick_y, brick_color in game_state['bricks']:
        pygame.draw.rect(window, brick_color, (brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))
    pygame.display.update()

# Función principal
def main():
    window = initialize_viewer_window()
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE)  # Fuente para mensajes
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 12346))  # Vincula el socket al puerto
    running = True
    waiting_for_game = True  # Espera hasta que llegue el estado del juego

    while running:
        game_state = receive_game_state(sock)

        if game_state == 'EXIT':  # Verifica si se recibe la señal de cierre
            running = False
            break
        elif game_state:  # Si se recibe el estado del juego, dibuja los elementos
            draw_game_elements(window, game_state)
            waiting_for_game = False
        else:
            draw_waiting_message(window, font)  # Muestra el mensaje de espera si no hay datos

        # Gestión de eventos de Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
