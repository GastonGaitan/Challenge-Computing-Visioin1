import cv2
import os
from face_detector import FaceDetector

def load_authorized_faces(detector, faces_dir):
    """Carga todas las imágenes de personas autorizadas desde el directorio"""
    for filename in os.listdir(faces_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # El nombre de la persona será el nombre del archivo sin la extensión
            person_name = os.path.splitext(filename)[0]
            image_path = os.path.join(faces_dir, filename)
            
            if detector.load_authorized_face(image_path, person_name):
                print(f"Imagen cargada exitosamente: {person_name}")
            else:
                print(f"Error al cargar la imagen: {person_name}")

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
                color = (0, 0, 255)  # Rojo en BGR
                display_text = "No autorizado"
            else:
                color = (0, 255, 0)  # Verde en BGR
                display_text = name
            
            # Calcular el padding para hacer el cuadrado más grande
            height = bottom - top
            width = right - left
            padding_v = int(height * 0.2)  # 20% de padding vertical
            padding_h = int(width * 0.2)   # 20% de padding horizontal
            
            # Ajustar las coordenadas con padding, asegurando que no se salgan del frame
            top_pad = max(0, top - padding_v)
            bottom_pad = min(frame.shape[0], bottom + padding_v)
            left_pad = max(0, left - padding_h)
            right_pad = min(frame.shape[1], right + padding_h)
            
            # Dibujar un rectángulo alrededor del rostro
            cv2.rectangle(frame, (left_pad, top_pad), (right_pad, bottom_pad), color, 3)
            
            # Dibujar el nombre debajo del rectángulo
            text_size = 0.8  # Tamaño de fuente
            text_thickness = 2  # Grosor del texto
            
            # Calcular el tamaño del texto para el fondo dependiendo de la etiqueta a poner en el cuadro de itentificacion
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