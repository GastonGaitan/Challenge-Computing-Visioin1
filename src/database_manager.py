import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='data/access.db'):
        """
        Inicializa el gestor de base de datos
        
        Args:
            db_path (str): Ruta al archivo de la base de datos
        """
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea la tabla si no existe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Crear tabla de registros de acceso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,           -- Nombre reconocido por OCR o nombre de imagen
                    person_id TEXT,               -- ID de persona reconocida (puede ser NULL)
                    timestamp DATETIME NOT NULL,  -- Fecha y hora del acceso
                    face_image_path TEXT         -- Ruta a la imagen del rostro
                )
            ''')
            
            conn.commit()
    
    def register_access(self, name, person_id=None, face_image_path=None):
        """
        Registra un nuevo acceso en la base de datos
        
        Args:
            name (str): Nombre reconocido por OCR o nombre de imagen
            person_id (str, optional): ID de la persona reconocida
            face_image_path (str, optional): Ruta a la imagen del rostro guardada
        
        Returns:
            int: ID del registro creado
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (name, person_id, timestamp, face_image_path)
                VALUES (?, ?, ?, ?)
            ''', (name, person_id, datetime.now(), face_image_path))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_access_logs(self, limit=100):
        """
        Obtiene los últimos registros de acceso
        
        Args:
            limit (int): Número máximo de registros a retornar
            
        Returns:
            list: Lista de registros de acceso
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, person_id, timestamp, face_image_path
                FROM access_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            return cursor.fetchall() 