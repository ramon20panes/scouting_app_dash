# db_template.py
import sqlite3
import hashlib
import os
from pathlib import Path

def get_db_connection():
    """Simula la conexión a la base de datos"""
    conn = sqlite3.connect(":memory:")  # Usa una base de datos en memoria para ejemplo
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con tablas y usuarios de ejemplo"""
    conn = get_db_connection()
    
    # Crear tabla de usuarios
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        player_id INTEGER
    )
    ''')
    
    # Crear usuarios de ejemplo
    users = [
        ('coach_dev', hash_password('coach_dev_pass'), 'Entrenador Ejemplo', 'coach', None),
        ('ejemplo_médico', hash_password('médico_dev'), 'médico Ejemplo', 'médico', None),
        ('ejemplo_preparador', hash_password('preparador_dev'), 'preparador Ejemplo', 'preparador', None),
        ('ejemplo_jugador', hash_password('jugador_dev'), 'Jugador Ejemplo', 'player', 1)
    ]
    
    # Verificar si ya existen usuarios para no duplicar
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:  # Solo insertar si no hay usuarios
        conn.executemany(
            "INSERT INTO users (username, password, name, role, player_id) VALUES (?, ?, ?, ?, ?)",
            users
        )
        conn.commit()
    
    conn.close()

def hash_password(password):
    """Genera un hash seguro para la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_user(username, password):
    """Verifica las credenciales del usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hashed_password)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Obtiene los datos de un usuario por su ID (username)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return dict(user) if user else None

# Si se ejecuta directamente
if __name__ == "__main__":
    init_db()
    print("Base de datos de ejemplo inicializada")