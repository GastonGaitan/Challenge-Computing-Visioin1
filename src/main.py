import cv2
import os
from face_detector import FaceDetector
from text_recognizer import TextRecognizer

def is_numeric_filename(filename):
    """Verifica si el nombre del archivo (sin extensión) contiene solo números"""
    name = os.path.splitext(filename)[0]
    return name.isdigit()

def load_authorized_faces(detector, faces_dir):
    """Carga todas las imágenes de personas autorizadas desde el directorio"""
    text_recognizer = TextRecognizer()
    
    for filename in os.listdir(faces_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(faces_dir, filename)
            
            # Leer la imagen
            image = cv2.imread(image_path)
            if image is not None:
                # Intentar extraer texto de la credencial
                extracted_text = text_recognizer.extract_text(image)
                if extracted_text:
                    person_name = extracted_text
                    print(f"Texto extraído de credencial en {filename}: {person_name}")
                    
                    # Usar esta imagen para el reconocimiento facial
                    if detector.load_authorized_face(image_path, person_name):
                        print(f"Imagen cargada exitosamente como: {person_name}")
                    else:
                        print(f"Error al cargar la imagen para reconocimiento facial")
                else:
                    print(f"No se encontró credencial en {filename}")
            else:
                print(f"Error al leer la imagen {filename}")

def main():
    # Inicializar el detector
    detector = FaceDetector()
    
    # Cargar rostros autorizados
    faces_dir = os.path.join('data', 'authorized_faces')
    print("Cargando rostros autorizados...")
    load_authorized_faces(detector, faces_dir)
    
    # Iniciar la webcam
    print("\nIniciando webcam... Presiona 'q' para salir.")
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar imagen de la webcam")
            break
            
        # Detectar rostros en el frame
        results = detector.detect_faces(frame)
        
        # Dibujar resultados
        for (top, right, bottom, left), name in results:
            # Definir color basado en si el rostro es reconocido o no
            if name == "Desconocido":
                display_text = "No autorizado"
                color = (0, 0, 255)  # Rojo en BGR
            else:
                color = (0, 255, 0)  # Verde en BGR
                display_text = name
            
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
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 