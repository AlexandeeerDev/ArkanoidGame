import mysql.connector

# Función para conectar a la base de datos
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="autorack.proxy.rlwy.net",
            user="root",
            password="zsRDpGGRyLRHGLIoZiEATZYeJmFaqbgl",
            port=41205,
            database="railway"
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Función para crear las tablas necesarias si no existen
def create_tables(connection):
    cursor = connection.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL
        )
    ''')

    # Crear tabla de movimientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            position VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    connection.commit()
    cursor.close()

# Función para añadir un nuevo usuario
def add_user(connection, username):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
    connection.commit()
    cursor.close()

# Función para obtener el ID del usuario a partir de su nombre
def get_user_id(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id

# Función para registrar un movimiento en la base de datos
def add_movement(connection, user_id, position):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO movements (user_id, position) VALUES (%s, %s)", (user_id, position))
    connection.commit()
    cursor.close()
