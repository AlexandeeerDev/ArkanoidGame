import pygame
from settings import *  # Importa las variables globales
from game import ArkanoidGame  # Importa la clase ArkanoidGame
import database

# Inicialización de Pygame
pygame.init()

# Inicialización de la ventana
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Arkanoid")

# Inicialización del reloj para controlar la velocidad del juego
clock = pygame.time.Clock()

# Función para mostrar el menú principal y pedir el nombre de usuario
def get_username(window, font):
    username = ""
    asking = True

    while asking:
        window.fill(BLACK)
        draw_text_centered("Introduce tu nombre de usuario:", font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 50)
        draw_text_centered(username, font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    asking = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

    return username

# Función para mostrar el menú principal
def main_menu(window, window_width, game_area_height, font, small_font):
    """ Menú principal del juego """
    menu_running = True
    while menu_running:
        window.fill(BLACK)  # Fondo del menú
        draw_text_centered("ARKANOID", font, WHITE, window, window_width // 2, game_area_height // 2 - 100)
        draw_text_centered("Presiona 1 para Fácil", small_font, WHITE, window, window_width // 2, game_area_height // 2)
        draw_text_centered("Presiona 2 para Medio", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 50)
        draw_text_centered("Presiona 3 para Difícil", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 100)
        draw_text_centered("Presiona ESC para salir", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 150)

        pygame.display.update()

        # Gestión de eventos para el menú
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                return 'facil'
            if keys[pygame.K_2]:
                return 'medio'
            if keys[pygame.K_3]:
                return 'dificil'
            if keys[pygame.K_ESCAPE]:
                return 'exit'

def draw_text_centered(text, font, color, surface, x, y):
    """ Función auxiliar para centrar texto """
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Bucle principal que controla el flujo entre el menú y el juego
def main():
    # Conectar a la base de datos
    connection = database.connect_to_database()
    if connection:
        database.create_tables(connection)

    button_positions = [
        (BUTTON_START_X, WINDOW_HEIGHT - 70),
        (BUTTON_START_X + BUTTON_WIDTH + BUTTON_SPACING, WINDOW_HEIGHT - 70),
        (BUTTON_START_X + 2 * (BUTTON_WIDTH + BUTTON_SPACING), WINDOW_HEIGHT - 70),
        (BUTTON_START_X + 3 * (BUTTON_WIDTH + BUTTON_SPACING), WINDOW_HEIGHT - 70)
    ]
    font = pygame.font.SysFont('Arial', 50)
    small_font = pygame.font.SysFont('Arial', 30)

    # Obtener el nombre de usuario
    username = get_username(window, font)
    if not username:
        return

    # Registrar al usuario en la base de datos
    database.add_user(connection, username)
    user_id = database.get_user_id(connection, username)

    game = ArkanoidGame(window, WINDOW_WIDTH, GAME_AREA_HEIGHT)

    running = True
    while running:
        difficulty = main_menu(window, WINDOW_WIDTH, GAME_AREA_HEIGHT, font, small_font)
        if difficulty in ['facil', 'medio', 'dificil']:
            game_option = game.game_loop(difficulty, button_positions, font, small_font, connection, user_id)
            if game_option == 'exit':
                running = False
        elif difficulty == 'exit':
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
