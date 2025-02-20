# game.py

import pygame
from settings import *  # Importa las variables globales
from elements import Paddle, Ball, Brick  # Importa las clases desde elements.py
import database

# Clase principal del juego Arkanoid
class ArkanoidGame:
    def __init__(self, window, window_width, game_area_height):
        self.window = window
        self.window_width = window_width
        self.game_area_height = game_area_height

        # Inicializar el reloj para controlar la velocidad del juego
        self.clock = pygame.time.Clock()

        # Posiciones del paddle
        self.paddle_positions = [0, PADDLE_SECTION_WIDTH, 2 * PADDLE_SECTION_WIDTH, 3 * PADDLE_SECTION_WIDTH]
        self.paddle = Paddle(self.paddle_positions, game_area_height)

        # Crear la pelota
        self.ball = Ball(window_width, game_area_height)

        # Lista de bloques (bricks)
        self.bricks = []

        # Estado del juego
        self.game_over = False
        self.victory = False

    def reset_game(self):
        """ Restablecer el estado del juego para empezar de nuevo """
        self.ball.reset()
        self.paddle.move_to(1)  # Iniciar con el paddle en "Izquierda Media"
        self.game_over = False
        self.victory = False  # Reiniciar estados de juego

    def create_bricks(self, rows):
        """ Crea una matriz de bloques con el orden de colores basado en la dificultad """
        self.bricks = []
        padding = 10  # Espacio entre bloques
        offset_x = 50  # Margen desde la izquierda
        offset_y = 50  # Margen desde arriba
        brick_width = 80
        brick_height = 30

        # Lista de colores para cada fila
        row_colors = [SILVER, RED, YELLOW, GREEN, PINK, BLUE]

        for row in range(rows):
            color = row_colors[row % len(row_colors)]  # Asignar color por fila
            for col in range(8):  # 8 columnas
                x = offset_x + col * (brick_width + padding)
                y = offset_y + row * (brick_height + padding)
                self.bricks.append(Brick(x, y, brick_width, brick_height, color))

    def handle_collisions(self):
        """ Manejar colisiones de la pelota con paredes, paddle y bloques """
        if self.ball.x <= 0 or self.ball.x >= self.window_width - self.ball.radius:
            self.ball.bounce('x')
        if self.ball.y <= 0:
            self.ball.bounce('y')

        # Colisión con el paddle
        if self.paddle.y <= self.ball.y + self.ball.radius <= self.paddle.y + self.paddle.height and \
           self.paddle.x <= self.ball.x <= self.paddle.x + self.paddle.width:
            self.ball.bounce('y')

        # Colisión con los bloques
        for brick in self.bricks[:]:
            if brick.rect.collidepoint(self.ball.x, self.ball.y):
                self.ball.bounce('y')
                self.bricks.remove(brick)

        # Verificar si se han destruido todos los bloques (victoria)
        if len(self.bricks) == 0:
            self.victory = True

    def draw_text_centered(self, text, font, color, x, y):
        """ Función para mostrar texto en pantalla y centrarlo """
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        self.window.blit(text_obj, text_rect)

    def draw_game_elements(self):
        """ Dibujar paddle, pelota, bloques y botones """
        self.window.fill(BLACK)  # Fondo negro

        # Dibujar el cuadro blanco alrededor del área de juego
        pygame.draw.rect(self.window, WHITE, (0, 0, WINDOW_WIDTH, GAME_AREA_HEIGHT), 5)

        # Dibujar paddle, pelota y bloques dentro del área de juego
        self.paddle.draw(self.window)
        self.ball.draw(self.window)
        for brick in self.bricks:
            brick.draw(self.window)

    def show_endgame_message(self, message, font, small_font):
        """ Mostrar mensajes de fin del juego """
        self.draw_text_centered(message, font, RED if self.game_over else GREEN, self.window_width // 2, self.game_area_height // 2 - 50)
        self.draw_text_centered("Presiona ENTER para jugar de nuevo", small_font, WHITE, self.window_width // 2, self.game_area_height // 2 + 50)
        self.draw_text_centered("Presiona ESC para salir", small_font, WHITE, self.window_width // 2, self.game_area_height // 2 + 100)

    def game_loop(self, difficulty, button_positions, font, small_font, connection, user_id):
        """ Loop principal del juego """
        self.reset_game()

        # Configurar filas según la dificultad
        difficulty_levels = {
            "facil": 3,
            "medio": 4,
            "dificil": 6
        }
        rows = difficulty_levels.get(difficulty, 3)
        self.create_bricks(rows)

        running = True
        while running:
            self.clock.tick(60)  # Controla la velocidad del juego a 60 FPS

            # Gestión de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'exit'

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Detectar clic en botones para mover el paddle
                    self.handle_button_click(mouse_pos, button_positions, connection, user_id)

            if not self.game_over and not self.victory:
                self.ball.move()
                self.handle_collisions()

                # Si la pelota cae por debajo del área de juego (debajo del cuadro blanco)
                if self.ball.y >= self.game_area_height - self.ball.radius:
                    self.game_over = True

            self.draw_game_elements()

            # Dibujar botones de control debajo del cuadro
            for i, text in enumerate(["Izq", "Izq Med", "Der Med", "Der"]):
                pygame.draw.rect(self.window, WHITE, (button_positions[i][0], button_positions[i][1], BUTTON_WIDTH, BUTTON_HEIGHT))
                self.draw_text_centered(text, small_font, BLACK, button_positions[i][0] + BUTTON_WIDTH // 2, button_positions[i][1] + BUTTON_HEIGHT // 2)

            # Mostrar mensaje de "Perdiste" o "Ganaste"
            if self.game_over:
                self.show_endgame_message("Perdiste", font, small_font)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    return 'restart'
                if keys[pygame.K_ESCAPE]:
                    return 'exit'

            if self.victory:
                self.show_endgame_message("¡Ganaste!", font, small_font)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    return 'restart'
                if keys[pygame.K_ESCAPE]:
                    return 'exit'

            pygame.display.update()

    def handle_button_click(self, mouse_pos, button_positions, connection, user_id):
        """ Mover el paddle según el clic en los botones y registrar el movimiento en la base de datos """
        for i in range(4):
            if button_positions[i][0] <= mouse_pos[0] <= button_positions[i][0] + BUTTON_WIDTH and \
               button_positions[i][1] <= mouse_pos[1] <= button_positions[i][1] + BUTTON_HEIGHT:
                self.paddle.move_to(i)
                # Registrar movimiento en la base de datos
                position = ["Izquierda", "Izquierda Media", "Derecha Media", "Derecha"][i]
                database.add_movement(connection, user_id, position)

# game.py

import time
from database import create_multiplayer_session
from settings import *  # Importa las variables globales
from elements import Paddle, Ball, Brick  # Importa las clases desde elements.py

def start_multiplayer_game(window, game, button_positions, font, small_font, connection, user_id):
    """ Inicia el modo multijugador y maneja las votaciones """
    
    # Esperar a que los jugadores presionen ENTER para unirse
    num_players = wait_for_players(window, font, small_font, connection, user_id)
    
    if num_players >= 2:
        running = True
        session_id = create_multiplayer_session(connection, user_id)  # Crear una nueva sesión multijugador
        votes = [0, 0, 0, 0]  # Inicializar votos
        paddle_position = 1  # Posición inicial del paddle
        game.reset_game()  # Restablecer el juego antes de empezar

        while running:
            game.clock.tick(60)  # Controla la velocidad del juego a 60 FPS

            # Permitir a los jugadores votar, pero el juego sigue corriendo
            if time.time() % 2 < 0.1:  # Cada 2 segundos se recogen los votos
                paddle_position = collect_votes(window, game, button_positions, font, small_font, num_players, votes)

            # Mover el paddle a la posición más votada
            game.paddle.move_to(paddle_position)

            # Continuar con el resto del juego
            game.ball.move()  # Movimiento de la pelota
            game.handle_collisions()  # Manejar colisiones

            # Dibujar todos los elementos del juego (paddle, bloques, pelota)
            game.draw_game_elements()

            # Comprobar si el juego ha terminado
            if game.ball.y >= game.game_area_height - game.ball.radius:
                game.game_over = True

            if game.game_over:
                game.show_endgame_message("Perdiste", font, small_font)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    running = False
                if keys[pygame.K_ESCAPE]:
                    running = False

            pygame.display.update()

        # Al finalizar la partida, limpiar las tablas de la sesión
        end_multiplayer_game(connection)

from database import count_joined_players, add_player_to_session

def wait_for_players(window, font, small_font, connection, user_id):
    """ Espera a que los jugadores presionen ENTER para unirse al modo multijugador y los registra en la base de datos """
    
    max_players = 5  # El número máximo de jugadores
    running = True
    
    while running:
        # Contar los jugadores que han presionado "Enter"
        players = count_joined_players(connection)
        
        window.fill(BLACK)
        draw_text_centered(f"Jugadores conectados: {players}/{max_players}", font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 50)
        draw_text_centered("Presiona ENTER para unirte", small_font, WHITE, window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 50)
        pygame.display.update()

        # Gestión de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return players  # Devolver el número de jugadores conectados

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and players < max_players:
                    # Registrar el jugador en la base de datos con su user_id
                    add_player_to_session(connection, user_id)
                    players += 1  # Actualizamos localmente el número de jugadores
                    break  # Salimos del bucle para actualizar la pantalla

        if players >= 2:  # Si se han unido al menos 2 jugadores, comenzamos el juego
            running = False

    return players  # Devolver el número de jugadores conectados

def clear_multiplayer_sessions(connection):
    """ Borra los registros de sesiones de multijugador anteriores """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM multiplayer_sessions")
    connection.commit()
    cursor.close()


def collect_votes(window, game, button_positions, font, small_font, num_players, votes):
    """ Muestra un contador de votos y recoge los votos de los jugadores mientras el juego sigue corriendo """
    start_time = time.time()
    running = True

    while running:
        remaining_time = 2 - (time.time() - start_time)  # Contador de 2 segundos

        # Dibujar el juego en segundo plano
        game.draw_game_elements()

        # Dibujar el temporizador de votación en la parte superior
        draw_text_centered(f"Tiempo restante para votar: {remaining_time:.1f}s", small_font, WHITE, window, WINDOW_WIDTH // 2, 30)

        # Dibujar el número de votos encima del área de botones
        for i, text in enumerate(["Izq", "Izq Med", "Der Med", "Der"]):
            # Mostrar solo el número de votos encima del área de botones
            draw_text_centered(f"{votes[i]}", small_font, WHITE, window, button_positions[i][0] + BUTTON_WIDTH // 2, 60)

        # Dibujar botones de votación debajo del área de juego
        for i, text in enumerate(["Izq", "Izq Med", "Der Med", "Der"]):
            pygame.draw.rect(window, WHITE, (button_positions[i][0], button_positions[i][1], BUTTON_WIDTH, BUTTON_HEIGHT))
            draw_text_centered(text, small_font, BLACK, window, button_positions[i][0] + BUTTON_WIDTH // 2, button_positions[i][1] + BUTTON_HEIGHT // 2)

        pygame.display.update()

        if time.time() - start_time >= 2:
            running = False  # Terminar el bucle después de 2 segundos

        # Recoger los clics para votar
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i in range(4):
                    if button_positions[i][0] <= mouse_pos[0] <= button_positions[i][0] + BUTTON_WIDTH and \
                       button_positions[i][1] <= mouse_pos[1] <= button_positions[i][1] + BUTTON_HEIGHT:
                        votes[i] += 1  # Incrementar los votos para el botón correspondiente

    # La opción con más votos gana
    return votes.index(max(votes))

def register_multiplayer_movement(connection, user_id, session_id, position):
    """ Registra un movimiento en el modo multijugador """
    cursor = connection.cursor()
    cursor.execute("INSERT INTO multiplayer_movements (user_id, session_id, position) VALUES (%s, %s, %s)", (user_id, session_id, position))
    connection.commit()
    cursor.close()

def end_multiplayer_game(connection):
    """ Limpia las tablas al final de la partida """
    clear_multiplayer_sessions(connection)
    clear_multiplayer_movements(connection)

def clear_multiplayer_movements(connection):
    """ Borra los registros de movimientos del modo multijugador """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM multiplayer_movements")
    connection.commit()
    cursor.close()

def draw_text_centered(text, font, color, surface, x, y):
    """ Función para mostrar texto en pantalla y centrarlo """
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)
