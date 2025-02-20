import mysql.connector
from mysql.connector import Error

def connect_to_database():
    """
    Conecta a la base de datos y devuelve la conexión.
    Si hay un error, imprime el error y devuelve None.
    """
    try:
        connection = mysql.connector.connect(
            host="autorack.proxy.rlwy.net",
            user="root",
            password="EVBDpWqCoxOviTZDsEScHRwAcJrhLXYs",
            port=10605,
            database="railway"
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

def create_singleplayer_movements_table(connection):
    """
    Crea la tabla 'singleplayer_movements' con los campos id, user_id, position y timestamp.
    """
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS singleplayer_movements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            position VARCHAR(15) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    connection.commit()
    cursor.close()

movements_buffer = []

def buffer_movement(user_id, position):
    """
    Almacena el movimiento localmente en el buffer.
    """
    movements_buffer.append((user_id, position))

def save_movements(connection):
    """
    Inserta todos los movimientos almacenados en el buffer a la base de datos.
    """
    if movements_buffer:
        cursor = connection.cursor()
        cursor.executemany(
            "INSERT INTO singleplayer_movements (user_id, position) VALUES (%s, %s)", 
            movements_buffer
        )
        connection.commit()
        cursor.close()
        movements_buffer.clear()  # Limpiar el buffer una vez guardado

def create_tables(connection):
    """
    Crea las tablas 'multiplayer_sessions', 
    y 'multiplayer_movements' si no existen.
    """
    cursor = connection.cursor()

    # Crear tabla de sesiones de multijugador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS multiplayer_sessions (
            session_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            joined BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Crear tabla de movimientos del modo multijugador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS multiplayer_movements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_id INT NOT NULL,
            position VARCHAR(15) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    connection.commit()
    cursor.close()

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

def add_movement(connection, user_id, position):
    """
    Registra un movimiento en la tabla 'singleplayer_movements' con el ID del usuario.
    """
    cursor = connection.cursor()
    cursor.execute("INSERT INTO singleplayer_movements (user_id, position) VALUES (%s, %s)", (user_id, position))
    connection.commit()
    cursor.close()

def create_multiplayer_session(connection, user_id):
    """
    Crea una nueva sesión de multijugador y devuelve el session_id.
    """
    cursor = connection.cursor()

    # Insertar un nuevo registro para la sesión
    cursor.execute("INSERT INTO multiplayer_sessions (user_id, joined) VALUES (%s, %s)", (user_id, True))
    connection.commit()

    # Obtener el ID de la sesión recién creada
    cursor.execute("SELECT LAST_INSERT_ID()")
    session_id = cursor.fetchone()[0]

    cursor.close()
    return session_id

def count_joined_players(connection):
    """
    Cuenta cuántos jugadores han presionado 'Enter' en la tabla 'multiplayer_sessions'
    para unirse a la sesión multijugador.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM multiplayer_sessions WHERE joined = TRUE")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

def add_player_to_session(connection, user_id):
    """
    Registra que un jugador ha presionado 'Enter' para unirse a la sesión multijugador.
    """
    cursor = connection.cursor()
    cursor.execute("INSERT INTO multiplayer_sessions (user_id, joined) VALUES (%s, %s)", (user_id, True))
    connection.commit()
    cursor.close()

def register_multiplayer_movement(connection, user_id, session_id, position):
    """ Registra un movimiento (voto) en la tabla multiplayer_movements """
    cursor = connection.cursor()
    cursor.execute("INSERT INTO multiplayer_movements (user_id, session_id, position, read_status) VALUES (%s, %s, %s, %s)", 
                   (user_id, session_id, position, False))
    connection.commit()
    cursor.close()

def calculate_winner_from_db(connection, session_id):
    """ Llama al procedimiento almacenado que calcula el ganador """
    cursor = connection.cursor()
    cursor.callproc("calculate_winner_from_db", (session_id,))
    
    # Obtener la posición ganadora
    for result in cursor.stored_results():
        winner = result.fetchone()[0]
    
    cursor.close()
    return winner

