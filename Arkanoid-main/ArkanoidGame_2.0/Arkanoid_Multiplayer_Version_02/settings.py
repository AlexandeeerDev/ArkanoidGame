# Dimensiones de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 700  # Ancho y alto de la ventana principal del juego
GAME_AREA_HEIGHT = 610  # Altura del área de juego

# Configuración de Paddle
PADDLE_HEIGHT = 20  # Altura del paddle
PADDLE_SECTION_WIDTH = WINDOW_WIDTH // 4  # Ancho de cada sección del paddle

# Configuración de la pelota
BALL_RADIUS = 10  # Radio de la pelota
BALL_SPEED_X = 2  # Velocidad de la pelota en el eje X
BALL_SPEED_Y = -2  # Velocidad de la pelota en el eje Y

# Configuración de botones
BUTTON_WIDTH = 120  # Ancho de los botones
BUTTON_HEIGHT = 50  # Altura de los botones
BUTTON_SPACING = 20  # Espacio entre botones
TOTAL_BUTTON_WIDTH = 4 * BUTTON_WIDTH + 3 * BUTTON_SPACING  # Ancho total que ocupan los 4 botones
BUTTON_START_X = (WINDOW_WIDTH - TOTAL_BUTTON_WIDTH) // 2  # Posición inicial de los botones en el eje X

# Configuración de bloques (Bricks)
BRICK_PADDING = 10  # Espacio entre bloques
BRICK_OFFSET_X = 50  # Margen desde el lado izquierdo
BRICK_OFFSET_Y = 50  # Margen desde la parte superior
BRICK_WIDTH = 80  # Ancho de los bloques
BRICK_HEIGHT = 30  # Altura de los bloques
BRICK_COLORS = [
    (192, 192, 192),  # SILVER
    (255, 0, 0),      # RED
    (255, 255, 0),    # YELLOW
    (0, 255, 0),      # GREEN
    (255, 105, 180),  # PINK
    (0, 0, 255)       # BLUE
]  # Colores asignados a las filas de bloques

# Configuración de texto
FONT_NAME = 'Arial'  # Nombre de la fuente utilizada en el juego
FONT_SIZE_LARGE = 40  # Tamaño de la fuente grande
FONT_SIZE_SMALL = 30  # Tamaño de la fuente pequeña

# Colores
COLORS = {
    'BLACK': (0, 0, 0),      # Negro
    'WHITE': (255, 255, 255),  # Blanco
    'RED': (255, 0, 0),       # Rojo
    'SILVER': (192, 192, 192), # Plateado
    'YELLOW': (255, 255, 0),  # Amarillo
    'GREEN': (0, 255, 0),     # Verde
    'PINK': (255, 105, 180),  # Rosa
    'BLUE': (0, 0, 255)       # Azul
}
