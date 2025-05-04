import cv2
import face_recognition
import numpy as np
from typing import List, Tuple

class FaceDetector:
    def __init__(self):
        """
        Inicializa el detector de rostros
        """
        self.known_face_encodings = []
        self.known_face_names = []

    def load_authorized_face(self, image_path: str, person_name: str) -> bool:
        """
        Carga una imagen de una persona autorizada y la agrega a la base de datos
        
        Args:
            image_path (str): Ruta a la imagen de la persona
            person_name (str): Nombre de la persona
            
        Returns:
            bool: True si se pudo cargar la imagen correctamente, False en caso contrario
        """
        try:
            # Cargar la imagen y obtener los encodings faciales
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                print(f"No se encontró ningún rostro en la imagen de {person_name}")
                return False
                
            # Tomamos el primer rostro encontrado
            face_encoding = face_encodings[0]
            
            # Agregamos el encoding y el nombre a nuestras listas
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(person_name)
            
            return True
            
        except Exception as e:
            print(f"Error al cargar la imagen de {person_name}: {str(e)}")
            return False
            
    def detect_faces(self, image: np.ndarray) -> List[Tuple[tuple, str]]:
        """
        Detecta y reconoce rostros en una imagen
        
        Args:
            image (np.ndarray): Imagen en formato OpenCV/NumPy
            
        Returns:
            List[Tuple[tuple, str]]: Lista de tuplas con las coordenadas del rostro y el nombre de la persona
        """
        # Convertir la imagen de BGR (OpenCV) a RGB (face_recognition)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Encontrar todos los rostros en la imagen
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        results = []
        
        for face_location, face_encoding in zip(face_locations, face_encodings):
            # Comparar el rostro con nuestra base de datos de rostros conocidos
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Desconocido"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
            
            results.append((face_location, name))
            
        return results 