from settings import *  # Importa las variables globales
from game import *  # Importa la clase ArkanoidGame
import database
import pygame

# Inicialización de Pygame
pygame.init()

# Inicialización de fuentes
font = pygame.font.SysFont('Arial', 40)  # Fuente grande
small_font = pygame.font.SysFont('Arial', 30)  # Fuente pequeña

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
        draw_text_centered("ARKANOID", font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 50)
        draw_text_centered("Introduce tu nombre de usuario:", small_font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 50)
        draw_text_centered(username, small_font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 100)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Cerrar completamente el juego
                exit()  # Salir del programa
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    asking = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

    return username

# Función para mostrar el menú de selección de modo de juego
def mode_menu(window, window_width, game_area_height, font, small_font):
    menu_running = True
    while menu_running:
        window.fill(BLACK)  # Fondo del menú
        draw_text_centered("ARKANOID", font, WHITE, window, window_width // 2, game_area_height // 2 - 100)
        draw_text_centered("Selecciona el modo de juego:", small_font, WHITE, window, window_width // 2, game_area_height // 2)
        draw_text_centered("Presiona 1 para Solitario", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 50)
        draw_text_centered("Presiona 2 para Multijugador", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 100)
        draw_text_centered("Presiona ESC para salir", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 150)

        pygame.display.update()

        # Gestión de eventos para el menú
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Cerrar completamente el juego
                exit()  # Salir del programa
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                return 'solitario'
            if keys[pygame.K_2]:
                return 'multijugador'
            if keys[pygame.K_ESCAPE]:
                return 'exit'

# Función para mostrar el menú principal
def main_menu(window, window_width, game_area_height, font, small_font):
    """ Menú principal del juego """
    menu_running = True
    while menu_running:
        window.fill(BLACK)  # Fondo del menú
        draw_text_centered("ARKANOID", font, WHITE, window, window_width // 2, game_area_height // 2 - 100)
        draw_text_centered("Selecciona la dificultad:", small_font, WHITE, window, window_width // 2, game_area_height // 2)
        draw_text_centered("Presiona 1 para Fácil", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 50)
        draw_text_centered("Presiona 2 para Medio", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 100)
        draw_text_centered("Presiona 3 para Difícil", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 150)
        draw_text_centered("Presiona ESC para salir", small_font, WHITE, window, window_width // 2, game_area_height // 2 + 200)

        pygame.display.update()

        # Gestión de eventos para el menú
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Cerrar completamente el juego
                exit()  # Salir del programa
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                return 'facil'
            if keys[pygame.K_2]:
                return 'medio'
            if keys[pygame.K_3]:
                return 'dificil'
            if keys[pygame.K_ESCAPE]:
                return 'exit'

# Bucle principal que controla el flujo entre el menú y el juego
def main():
    # Conectar a la base de datos
    connection = database.connect_to_database()
    if connection:
        # Crear las tablas necesarias
        database.create_users_table(connection)
        database.create_singleplayer_movements_table(connection)

        # Crear las otras tablas (single, multiplayer movements)
        database.create_tables(connection)

    button_positions = [
        (BUTTON_START_X, WINDOW_HEIGHT - 70),
        (BUTTON_START_X + BUTTON_WIDTH + BUTTON_SPACING, WINDOW_HEIGHT - 70),
        (BUTTON_START_X + 2 * (BUTTON_WIDTH + BUTTON_SPACING), WINDOW_HEIGHT - 70),
        (BUTTON_START_X + 3 * (BUTTON_WIDTH + BUTTON_SPACING), WINDOW_HEIGHT - 70)
    ]

    username = None
    while True:
        # Solicitar el nombre de usuario
        username = get_username(window, font)

        # Verificar si el nombre de usuario ya existe
        if database.user_exists(connection, username):
            # Mostrar mensaje de advertencia
            show_message(window, font, "El nombre de usuario ya existe. Por favor, elige otro.")
        else:
            break  # Salir del bucle si el nombre de usuario es válido

    # Registrar al usuario en la base de datos
    database.add_user(connection, username)
    user_id = database.get_user_id(connection, username)

    game = ArkanoidGame(window, WINDOW_WIDTH, GAME_AREA_HEIGHT)

    running = True
    while running:
        # Mostrar menú de selección de modo de juego
        mode = mode_menu(window, WINDOW_WIDTH, GAME_AREA_HEIGHT, font, small_font)
        
        if mode == 'solitario':
            # Selección de dificultad para el modo solitario
            difficulty = main_menu(window, WINDOW_WIDTH, GAME_AREA_HEIGHT, font, small_font)
            if difficulty in ['facil', 'medio', 'dificil']:
                game_option = game.game_loop(difficulty, button_positions, font, small_font, connection, user_id)
                if game_option == 'exit':
                    running = False
                    
        elif mode == 'multijugador':
            # Selección de dificultad para el modo multijugador
            difficulty = main_menu(window, WINDOW_WIDTH, GAME_AREA_HEIGHT, font, small_font)
            if difficulty in ['facil', 'medio', 'dificil']:
                # Iniciar el flujo de modo multijugador con la dificultad seleccionada
                game_multiplayer_option = start_multiplayer_game(window, game, difficulty, button_positions, font, small_font, connection, user_id)
                if game_multiplayer_option == 'exit':
                    running = False

        elif mode == 'exit':
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
