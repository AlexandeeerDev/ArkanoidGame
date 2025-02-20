import pygame
from settings import *  # Importa las constantes
from game import ArkanoidGame, draw_text_centered, show_message  # Importa las funciones y clases necesarias
import database
import socket
import json

def initialize_pygame():
    """Inicializa Pygame y configura la ventana."""
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Establece las dimensiones de la ventana
    pygame.display.set_caption("Arkanoid")  # Define el título de la ventana
    clock = pygame.time.Clock()  # Reloj para controlar la velocidad del juego
    return window, clock

def initialize_fonts():
    """Inicializa las fuentes usadas en el juego."""
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE)  # Fuente grande para los títulos
    small_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL)  # Fuente pequeña para los subtítulos
    return font, small_font

def get_username(window, font):
    """Muestra una pantalla para que el usuario ingrese su nombre."""
    username = ""
    asking = True

    while asking:
        window.fill(COLORS['BLACK'])  # Pinta el fondo de negro
        draw_text_centered("ARKANOID", font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 50)
        draw_text_centered("Introduce tu nombre de usuario:", font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 50)
        draw_text_centered(username, font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 100)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Si el jugador cierra la ventana
                # Enviar señal de cierre a la ventana secundaria
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'EXIT', ('localhost', 12346))
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:  # Si el jugador presiona una tecla
                if event.key == pygame.K_RETURN:  # Confirmar nombre
                    asking = False
                elif event.key == pygame.K_BACKSPACE:  # Eliminar último carácter
                    username = username[:-1]
                else:
                    username += event.unicode  # Añadir letra al nombre

    return username

def main_menu(window, font, small_font):
    """Muestra el menú principal del juego con opciones de dificultad."""
    menu_running = True
    while menu_running:
        window.fill(COLORS['BLACK'])  # Fondo negro
        draw_text_centered("ARKANOID", font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 100)
        draw_text_centered("Selecciona la dificultad:", small_font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2)
        draw_text_centered("Presiona 1 para Fácil", small_font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 50)
        draw_text_centered("Presiona 2 para Medio", small_font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 100)
        draw_text_centered("Presiona 3 para Difícil", small_font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 150)
        draw_text_centered("Presiona ESC para salir", small_font, COLORS['WHITE'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 200)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Si el jugador cierra la ventana
                # Enviar señal de cierre a la ventana secundaria
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'EXIT', ('localhost', 12346))
                pygame.quit()
                exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                return 'Fácil'
            if keys[pygame.K_2]:
                return 'Medio'
            if keys[pygame.K_3]:
                return 'Difícil'
            if keys[pygame.K_ESCAPE]:
                # Enviar señal de cierre a la ventana secundaria
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'EXIT', ('localhost', 12346))
                return 'exit'

def main():
    """Función principal que controla el flujo del juego."""
    # Inicializaciones
    window, clock = initialize_pygame()  # Inicializa Pygame y crea la ventana
    font, small_font = initialize_fonts()  # Inicializa las fuentes del juego

    # Conectar a la base de datos
    connection = database.connect_to_database()  # Conexión a la base de datos

    # Enviar señal de cierre a la ventana secundaria
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if connection:
        database.create_users_table(connection)  # Crear tabla de usuarios si no existe
        database.create_singleplayer_movements_table(connection)  # Crear tabla de movimientos
        database.create_singleplayer_games_table(connection)  # Crear tabla de partidas

    # Definir las posiciones de los botones
    button_positions = [
        (BUTTON_START_X, WINDOW_HEIGHT - 70),
        (BUTTON_START_X + BUTTON_WIDTH + BUTTON_SPACING, WINDOW_HEIGHT - 70),
        (BUTTON_START_X + 2 * (BUTTON_WIDTH + BUTTON_SPACING), WINDOW_HEIGHT - 70),
        (BUTTON_START_X + 3 * (BUTTON_WIDTH + BUTTON_SPACING), WINDOW_HEIGHT - 70)
    ]

    while True:
        # Solicitar el nombre de usuario
        username = get_username(window, font)

        # Verificar si el nombre de usuario ya existe en la base de datos
        if database.user_exists(connection, username):
            show_message(window, font, "El nombre de usuario ya existe. Por favor, elige otro.")
        else:
            break

    # Registrar al usuario en la base de datos
    database.add_user(connection, username)
    user_id = database.get_user_id(connection, username)

    # Crear instancia del juego Arkanoid
    game = ArkanoidGame(window, WINDOW_WIDTH, GAME_AREA_HEIGHT)

    running = True
    while running:
        # Selección de dificultad para el modo de un jugador
        difficulty = main_menu(window, font, small_font)
        if difficulty in ['Fácil', 'Medio', 'Difícil']:
            game_option = game.game_loop(difficulty, button_positions, font, small_font, connection, user_id)
            if game_option == 'exit':
                running = False
        if difficulty == 'exit':
            running = False

    sock.sendto(b'EXIT', ('localhost', 12346))
    sock.close()
    pygame.quit()  # Finaliza el juego

if __name__ == "__main__":
    main()
