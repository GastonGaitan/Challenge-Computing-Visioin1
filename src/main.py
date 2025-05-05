import cv2
import os
from face_detector import FaceDetector
from text_recognizer import TextRecognizer
from database_manager import DatabaseManager
import uuid
from datetime import datetime, timedelta
import logging

def setup_logger():
    """Configura el logger para mostrar información en tiempo real"""
    # Crear el directorio de logs si no existe
    log_dir = 'data/logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar el logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            # Handler para mostrar en consola
            logging.StreamHandler(),
            # Handler para guardar en archivo
            logging.FileHandler(os.path.join(log_dir, f'access_log_{datetime.now().strftime("%Y%m%d")}.txt'))
        ]
    )
    return logging.getLogger('AccessControl')

def is_numeric_filename(filename):
    """Verifica si el nombre del archivo (sin extensión) contiene solo números"""
    name = os.path.splitext(filename)[0]
    return name.isdigit()

def save_face_image(frame, face_location, name):
    """
    Guarda la imagen recortada del rostro
    
    Args:
        frame: Imagen completa
        face_location: Tupla (top, right, bottom, left) con la ubicación del rostro
        name: Nombre de la persona para el archivo
        
    Returns:
        str: Ruta donde se guardó la imagen
    """
    top, right, bottom, left = face_location
    face_image = frame[top:bottom, left:right]
    
    # Crear directorio si no existe
    faces_dir = os.path.join('data', 'detected_faces')
    os.makedirs(faces_dir, exist_ok=True)
    
    # Generar nombre único para la imagen
    filename = f"{name}_{uuid.uuid4().hex[:8]}.jpg"
    image_path = os.path.join(faces_dir, filename)
    
    # Guardar imagen
    cv2.imwrite(image_path, face_image)
    return image_path

def load_authorized_faces(detector, faces_dir):
    """Carga todas las imágenes de personas autorizadas desde el directorio"""
    text_recognizer = TextRecognizer()
    
    for filename in os.listdir(faces_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(faces_dir, filename)
            
            # Si el nombre del archivo es numérico, buscar credencial
            if is_numeric_filename(filename):
                print(f"Procesando imagen con nombre numérico: {filename}")
                image = cv2.imread(image_path)
                if image is not None:
                    # Intentar extraer texto de la credencial
                    extracted_text = text_recognizer.extract_text(image)
                    if extracted_text:
                        person_name = extracted_text
                        print(f"Texto extraído de credencial: {person_name}")
                    else:
                        person_name = os.path.splitext(filename)[0]
                        print(f"No se encontró credencial, usando nombre del archivo: {person_name}")
                else:
                    person_name = os.path.splitext(filename)[0]
                    print(f"Error al leer la imagen, usando nombre del archivo: {person_name}")
            else:
                # Si el nombre tiene letras, usar el nombre del archivo
                person_name = os.path.splitext(filename)[0]
                print(f"Usando nombre del archivo: {person_name}")
            
            # Cargar la imagen para reconocimiento facial
            if detector.load_authorized_face(image_path, person_name):
                print(f"Imagen cargada exitosamente como: {person_name}")
            else:
                print(f"Error al cargar la imagen: {person_name}")

def main():
    # Configurar logger
    logger = setup_logger()
    logger.info("=== Sistema de Control de Acceso Iniciado ===")
    
    # Inicializar el detector y la base de datos
    detector = FaceDetector()
    db_manager = DatabaseManager()
    
    # Diccionario para almacenar el último tiempo de registro por persona
    last_register_time = {}
    # Tiempo mínimo entre registros (10 minutos)
    MIN_TIME_BETWEEN_REGISTERS = timedelta(minutes=10)
    
    # Cargar rostros autorizados
    faces_dir = os.path.join('data', 'authorized_faces')
    logger.info("Cargando rostros autorizados...")
    load_authorized_faces(detector, faces_dir)
    
    # Iniciar la webcam
    logger.info("Iniciando webcam... Presiona 'q' para salir.")
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Error al capturar imagen de la webcam")
            break
            
        # Detectar rostros en el frame
        results = detector.detect_faces(frame)
        
        # Tiempo actual
        current_time = datetime.now()
        
        # Dibujar resultados
        for (top, right, bottom, left), name in results:
            # Definir color basado en si el rostro es reconocido o no
            if name == "Desconocido":
                display_text = "No autorizado"
                color = (0, 0, 255)  # Rojo en BGR
                logger.warning(f"Persona no autorizada detectada - {current_time.strftime('%H:%M:%S')}")
            else:
                color = (0, 255, 0)  # Verde en BGR
                display_text = name
                
                # Solo procesar registro para personas autorizadas
                # Verificar si ha pasado suficiente tiempo desde el último registro
                last_time = last_register_time.get(name)
                should_register = last_time is None or (current_time - last_time) >= MIN_TIME_BETWEEN_REGISTERS
                
                if should_register:
                    # Guardar imagen del rostro
                    face_location = (top, right, bottom, left)
                    face_image_path = save_face_image(frame, face_location, name)
                    
                    # Registrar el acceso en la base de datos
                    db_manager.register_access(
                        name=name,
                        person_id=name,  # Usamos el nombre como ID
                        face_image_path=face_image_path
                    )
                    
                    # Actualizar el tiempo del último registro
                    last_register_time[name] = current_time
                    
                    # Log detallado del registro
                    logger.info(f"Nuevo registro de acceso - {name}")
                    logger.info(f"  ├─ ID: {name}")
                    logger.info(f"  ├─ Hora: {current_time.strftime('%H:%M:%S')}")
                    logger.info(f"  └─ Imagen: {os.path.basename(face_image_path)}")
                elif last_time is not None:
                    # Calcular tiempo restante para próximo registro
                    time_until_next = (last_time + MIN_TIME_BETWEEN_REGISTERS - current_time).seconds
                    minutes = time_until_next // 60
                    seconds = time_until_next % 60
                    logger.debug(f"Esperando {minutes}m {seconds}s para próximo registro de {name}")
            
            # Calcular el padding para hacer el cuadrado más grande
            height = bottom - top
            width = right - left
            padding_v = int(height * 0.2)  # 20% de padding vertical
            padding_h = int(width * 0.2)   # 20% de padding horizontal
            
            # Ajustar las coordenadas con padding
            top_pad = max(0, top - padding_v)
            bottom_pad = min(frame.shape[0], bottom + padding_v)
            left_pad = max(0, left - padding_h)
            right_pad = min(frame.shape[1], right + padding_h)
            
            # Dibujar un rectángulo alrededor del rostro
            cv2.rectangle(frame, (left_pad, top_pad), (right_pad, bottom_pad), color, 3)
            
            # Dibujar el texto
            text_size = 0.8
            text_thickness = 2
            
            # Calcular el tamaño del texto para el fondo
            (text_width, text_height), _ = cv2.getTextSize(display_text, 
                                                         cv2.FONT_HERSHEY_DUPLEX, 
                                                         text_size, 
                                                         text_thickness)
            
            # Dibujar el fondo del texto
            text_bg_height = int(text_height + 10)
            cv2.rectangle(frame, 
                         (left_pad, bottom_pad), 
                         (left_pad + text_width + 10, bottom_pad + text_bg_height), 
                         color, 
                         cv2.FILLED)
            
            # Dibujar el texto
            cv2.putText(frame, 
                       display_text, 
                       (left_pad + 5, bottom_pad + text_height + 2), 
                       cv2.FONT_HERSHEY_DUPLEX, 
                       text_size, 
                       (255, 255, 255), 
                       text_thickness)
        
        # Mostrar el frame
        cv2.imshow('Reconocimiento Facial', frame)
        
        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    logger.info("=== Sistema de Control de Acceso Finalizado ===")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 