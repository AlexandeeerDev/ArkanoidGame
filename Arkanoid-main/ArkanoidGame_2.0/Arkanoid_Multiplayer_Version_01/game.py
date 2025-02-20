import pygame
from settings import *
from elements import Paddle, Ball, Brick  # Importa las clases desde elements.py
import database
import socket
import json

# Clase principal del juego Arkanoid
class ArkanoidGame:
    def __init__(self, window, window_width, game_area_height):
        """Inicializa el juego Arkanoid con la ventana y dimensiones dadas."""
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

        # Configuración del socket para enviar el estado del juego
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_game_state(self):
        """
        Envía el estado del juego (paddle, pelota, bloques) a la ventana secundaria.
        """
        game_state = {
            'paddle_x': self.paddle.x,
            'paddle_y': self.paddle.y,
            'ball_x': self.ball.x,
            'ball_y': self.ball.y,
            'bricks': [(brick.rect.x, brick.rect.y, brick.color) for brick in self.bricks]  # Incluye el color del bloque
        }
        # Convertir a JSON y enviar por socket a la ventana secundaria
        self.sock.sendto(json.dumps(game_state).encode(), ('localhost', 12346))

    def reset_game(self):
        """Restablece el estado del juego para empezar de nuevo."""
        self.ball.reset()
        self.paddle.move_to(1)  # Iniciar con el paddle en "Izquierda Media"
        self.game_over = False
        self.victory = False  # Reiniciar estados de juego

    def create_bricks(self, rows):
        """Crea una matriz de bloques con el orden de colores basado en la dificultad."""
        self.bricks = []
        for row in range(rows):
            color = BRICK_COLORS[row % len(BRICK_COLORS)]  # Asignar color por fila
            for col in range(8):  # 8 columnas
                x = BRICK_OFFSET_X + col * (BRICK_WIDTH + BRICK_PADDING)
                y = BRICK_OFFSET_Y + row * (BRICK_HEIGHT + BRICK_PADDING)
                self.bricks.append(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color))

    def handle_collisions(self):
        """Maneja las colisiones de la pelota con paredes, paddle y bloques."""
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

    def draw_game_elements(self):
        """Dibuja paddle, pelota, bloques y botones en la pantalla."""
        self.window.fill(COLORS['BLACK'])  # Fondo negro

        # Dibujar el cuadro blanco alrededor del área de juego
        pygame.draw.rect(self.window, COLORS['WHITE'], (0, 0, WINDOW_WIDTH, GAME_AREA_HEIGHT), 5)

        # Dibujar paddle, pelota y bloques dentro del área de juego
        self.paddle.draw(self.window)
        self.ball.draw(self.window)
        for brick in self.bricks:
            brick.draw(self.window)

    def show_endgame_message(self, message, font, small_font):
        """Muestra mensajes de fin del juego."""
        draw_text_centered(message, font, COLORS['RED'] if self.game_over else COLORS['GREEN'], self.window, self.window_width // 2, self.game_area_height // 2 - 50)
        draw_text_centered("Presiona ENTER para jugar de nuevo", small_font, COLORS['WHITE'], self.window, self.window_width // 2, self.game_area_height // 2 + 50)
        draw_text_centered("Presiona ESC para salir", small_font, COLORS['WHITE'], self.window, self.window_width // 2, self.game_area_height // 2 + 100)

    def game_loop(self, difficulty, button_positions, font, small_font, connection, user_id):
        """Bucle principal del juego."""
        self.reset_game()

        # Configurar filas según la dificultad
        difficulty_levels = {
            "Fácil": 3,
            "Medio": 4,
            "Difícil": 6
        }
        rows = difficulty_levels.get(difficulty, 3)
        self.create_bricks(rows)

        self.result_saved = False  # Nueva variable para asegurarnos de que el resultado solo se guarda una vez
        running = True

        while running:
            self.clock.tick(60)  # Controla la velocidad del juego a 60 FPS

            # Gestión de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Si el juego no ha terminado (ni victoria ni derrota), marcar como "Inconcluso"
                    if not (self.game_over or self.victory):
                        database.save_movements(connection, difficulty)  # Guardar los movimientos en la tabla de movimientos
                        result = "No terminó"
                        database.save_game_result(connection, user_id, difficulty, result)  # Guardar el resultado de la partida
        
                    # Enviar una señal de cierre a la ventana secundaria
                    self.sock.sendto(b'EXIT', ('localhost', 12346))
                    return 'exit'
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Detectar clic en botones para mover el paddle
                    self.handle_button_click(mouse_pos, button_positions, connection, user_id)

            if not self.game_over and not self.victory:
                self.ball.move()
                self.handle_collisions()

                # Enviar el estado del juego a la ventana secundaria
                self.send_game_state()

                # Si la pelota cae por debajo del área de juego (debajo del cuadro blanco)
                if self.ball.y >= self.game_area_height - self.ball.radius:
                    self.game_over = True

            self.draw_game_elements()

            # Dibujar botones de control debajo del cuadro
            for i, text in enumerate(["Izq", "Izq Med", "Der Med", "Der"]):
                pygame.draw.rect(self.window, COLORS['WHITE'], (button_positions[i][0], button_positions[i][1], BUTTON_WIDTH, BUTTON_HEIGHT))
                draw_text_centered(text, small_font, COLORS['BLACK'], self.window, button_positions[i][0] + BUTTON_WIDTH // 2, button_positions[i][1] + BUTTON_HEIGHT // 2)

            # Mostrar mensaje de "Perdiste" o "Ganaste"
            if (self.game_over or self.victory) and not self.result_saved:
                # Guardar movimientos y resultado solo una vez
                database.save_movements(connection, difficulty)  # Guardar los movimientos en la tabla de movimientos
                result = "Perdió" if self.game_over else "Ganó"
                database.save_game_result(connection, user_id, difficulty, result)  # Guardar el resultado de la partida
                self.result_saved = True  # Marcar como guardado para que no se guarde más de una vez

            # Mostrar mensajes finales y permitir reiniciar o salir
            if self.game_over:
                self.show_endgame_message("Perdiste", font, small_font)
                # Obtener el estado de todas las teclas
                keys = pygame.key.get_pressed()
                # Detectar si se presionó ENTER
                if keys[pygame.K_RETURN]:
                    return 'restart'  # Reiniciar el juego
                # Detectar si se presionó ESC
                if keys[pygame.K_ESCAPE]:
                    # Enviar una señal de cierre a la ventana secundaria
                    self.sock.sendto(b'EXIT', ('localhost', 12346))
                    return 'exit'  # Salir del juego

            if self.victory:
                self.show_endgame_message("¡Ganaste!", font, small_font)
                # Obtener el estado de todas las teclas
                keys = pygame.key.get_pressed()
                # Detectar si se presionó ENTER
                if keys[pygame.K_RETURN]:
                    return 'restart'  # Reiniciar el juego
                # Detectar si se presionó ESC
                if keys[pygame.K_ESCAPE]:
                    # Enviar una señal de cierre a la ventana secundaria
                    self.sock.sendto(b'EXIT', ('localhost', 12346))
                    return 'exit'  # Salir del juego

            pygame.display.update()

    def handle_button_click(self, mouse_pos, button_positions, connection, user_id):
        """Mueve el paddle según el clic en los botones y registra el movimiento en la base de datos."""
        for i in range(4):
            if button_positions[i][0] <= mouse_pos[0] <= button_positions[i][0] + BUTTON_WIDTH and \
               button_positions[i][1] <= mouse_pos[1] <= button_positions[i][1] + BUTTON_HEIGHT:
                self.paddle.move_to(i)
                # Registrar movimiento en la base de datos
                position = ["Izquierda", "Izquierda Media", "Derecha Media", "Derecha"][i]
                database.buffer_movement(user_id, position)  # Cada vez que el paddle se mueva
        
    def game_loop_multiplayer(self, button_positions, font, small_font, connection, user_id):
        """Bucle principal del juego multijugador."""
        self.reset_game()

        self.result_saved = False  # Variable para evitar múltiples guardados
        running = True

        while running:
            self.clock.tick(60)  # Controla la velocidad del juego a 60 FPS

            # Gestión de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Guardar movimientos en la tabla multiplayer y marcar el juego como "Inconcluso"
                    database.save_movements_multiplayer(connection)  # Guardar en la tabla de movimientos multijugador
                    result = "No terminó"
                    database.save_game_result_multiplayer(connection, user_id, result)  # Guardar el resultado en multiplayer
            
                    # Enviar señal de cierre
                    self.sock.sendto(b'EXIT', ('localhost', 12346))
                    return 'exit'

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Detectar clic en botones para mover el paddle
                    self.handle_button_click(mouse_pos, button_positions, connection, user_id)

            if not self.game_over and not self.victory:
                self.ball.move()
                self.handle_collisions()

                # Enviar el estado del juego a la ventana secundaria
                self.send_game_state()

                if self.ball.y >= self.game_area_height - self.ball.radius:
                    self.game_over = True

            self.draw_game_elements()

            # Dibujar botones de control
            for i, text in enumerate(["Izq", "Izq Med", "Der Med", "Der"]):
                pygame.draw.rect(self.window, COLORS['WHITE'], (button_positions[i][0], button_positions[i][1], BUTTON_WIDTH, BUTTON_HEIGHT))
                draw_text_centered(text, small_font, COLORS['BLACK'], self.window, button_positions[i][0] + BUTTON_WIDTH // 2, button_positions[i][1] + BUTTON_HEIGHT // 2)

            if (self.game_over or self.victory) and not self.result_saved:
                database.save_movements_multiplayer(connection)  # Guardar movimientos en la tabla de multiplayer
                result = "Perdió" if self.game_over else "Ganó"
                database.save_game_result_multiplayer(connection, user_id, result)  # Guardar el resultado de la partida
                self.result_saved = True

            if self.game_over:
                self.show_endgame_message("Perdiste", font, small_font)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    return 'restart'
                if keys[pygame.K_ESCAPE]:
                    self.sock.sendto(b'EXIT', ('localhost', 12346))
                    return 'exit'

            if self.victory:
                self.show_endgame_message("¡Ganaste!", font, small_font)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    return 'restart'
                if keys[pygame.K_ESCAPE]:
                    self.sock.sendto(b'EXIT', ('localhost', 12346))
                    return 'exit'

            pygame.display.update()


# Función global para centrar texto en pantalla
def draw_text_centered(text, font, color, surface, x, y):
    """Función para mostrar texto en pantalla y centrarlo."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Función global para mostrar un mensaje temporal en pantalla
def show_message(window, font, message):
    """
    Muestra un mensaje temporal en la pantalla, centrado y con espacio.
    """
    window.fill(COLORS['BLACK'])

    # Separar el mensaje en dos líneas para mostrar
    message_lines = message.split('. ')  # Dividimos el mensaje en partes

    # Dibujar la primera línea centrada en la pantalla
    draw_text_centered(message_lines[0], font, COLORS['RED'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 50)

    # Si hay una segunda línea, mostrarla más abajo
    if len(message_lines) > 1:
        draw_text_centered(message_lines[1], font, COLORS['RED'], window, WINDOW_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 50)

    pygame.display.update()
    pygame.time.wait(2000)  # Mostrar el mensaje por 2 segundos