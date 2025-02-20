import mysql.connector
from mysql.connector import Error
import re

# Buffer para almacenar movimientos localmente antes de guardarlos en la base de datos
movements_buffer = []

# Comando completo para la conexión
mysql_command = "mysql -hjunction.proxy.rlwy.net -uroot -pvwrTORlTmwslPHVOaxRxRUtfLnhQpCWh --port 52226 --protocol=TCP railway"

def extract_connection_params(command):
    """
    Extrae los parámetros de conexión de un comando estilo MySQL.
    """
    # Usar expresiones regulares para capturar los parámetros
    host = re.search(r'-h([^\s]+)', command).group(1)
    user = re.search(r'-u([^\s]+)', command).group(1)
    password = re.search(r'-p([^\s]+)', command).group(1)
    port = re.search(r'--port\s+(\d+)', command).group(1)
    database = re.search(r'(\w+)$', command).group(1)

    return {
        'host': host,
        'user': user,
        'password': password,
        'port': int(port),
        'database': database
    }

def connect_to_database():
    """
    Conecta a la base de datos utilizando el comando MySQL predefinido en el archivo.
    """
    params = extract_connection_params(mysql_command)
    
    try:
        # Conectar a la base de datos utilizando los parámetros extraídos
        connection = mysql.connector.connect(
            host=params['host'],
            user=params['user'],
            password=params['password'],
            port=params['port'],
            database=params['database']
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos")
            return connection
    except Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

def create_users_table(connection):
    """
    Crea la tabla 'users' con los campos id, username, y created_at.
    """
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    connection.commit()
    cursor.close()

def create_singleplayer_movements_table(connection):
    """
    Crea la tabla 'singleplayer_movements' con los campos id, user_id, position, difficulty.
    """
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS singleplayer_movements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            position VARCHAR(15) NOT NULL,
            difficulty VARCHAR(10) NOT NULL,  -- Campo para almacenar la dificultad
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    connection.commit()
    cursor.close()

def user_exists(connection, username):
    """
    Verifica si un usuario ya existe en la base de datos.
    Devuelve True si existe, de lo contrario, False.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user is not None

def add_user(connection, username):
    """
    Añade un nuevo usuario a la tabla 'users'.
    """
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
    connection.commit()
    cursor.close()

def get_user_id(connection, username):
    """
    Devuelve el ID de un usuario a partir de su nombre.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id

def buffer_movement(user_id, position):
    """
    Almacena el movimiento localmente en el buffer.
    """
    movements_buffer.append((user_id, position))

def save_movements(connection, difficulty):
    """
    Inserta todos los movimientos almacenados en el buffer a la base de datos con la dificultad.
    """
    if movements_buffer:
        cursor = connection.cursor()
        cursor.executemany(
            "INSERT INTO singleplayer_movements (user_id, position, difficulty) VALUES (%s, %s, %s)", 
            [(user_id, position, difficulty) for user_id, position in movements_buffer]
        )
        connection.commit()
        cursor.close()
        movements_buffer.clear()  # Limpiar el buffer una vez guardado

def create_singleplayer_games_table(connection):
    """
    Crea la tabla 'singleplayer_games' para almacenar los resultados de las partidas.
    """
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS singleplayer_games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            difficulty VARCHAR(10) NOT NULL,
            result VARCHAR(10) NOT NULL,  -- Ganó o Perdió
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    connection.commit()
    cursor.close()

def save_game_result(connection, user_id, difficulty, result):
    """
    Guarda el resultado final de la partida (ganar o perder) en la tabla singleplayer_games.
    """
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO singleplayer_games (user_id, difficulty, result) VALUES (%s, %s, %s)",
        (user_id, difficulty, result)
    )
    connection.commit()
    cursor.close()
