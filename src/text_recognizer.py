import pytesseract
import cv2
import numpy as np
import re

class TextRecognizer:
    def __init__(self):
        # Configuración de Tesseract optimizada para texto de credenciales
        self.config = '--psm 7 --oem 3'  # Modo de línea única con mejor motor OCR
        
    def find_white_card(self, image):
        """Detecta el cuadrado blanco de la credencial en la imagen"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbral para detectar áreas blancas
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Buscar el contorno que parece una credencial (rectangular y blanco)
        best_rect = None
        max_area = 0
        
        for cnt in contours:
            # Aproximar el contorno a un polígono
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            
            # Si tiene 4 vértices (es rectangular)
            if len(approx) == 4:
                area = cv2.contourArea(cnt)
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Calcular la relación de aspecto
                aspect_ratio = float(w)/h
                
                # Verificar si parece una credencial (relación de aspecto cercana a 1.6)
                if 1.4 <= aspect_ratio <= 1.8 and area > max_area:
                    # Verificar si el área es predominantemente blanca
                    roi = gray[y:y+h, x:x+w]
                    if np.mean(roi) > 180:  # Si el promedio es alto (área blanca)
                        max_area = area
                        best_rect = (x, y, w, h)
        
        return best_rect

    def preprocess_roi(self, roi):
        """Preprocesa la región de interés para mejorar el OCR"""
        # Convertir a escala de grises si es necesario
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Redimensionar si es muy pequeño
        min_height = 30
        if gray.shape[0] < min_height:
            scale_factor = min_height / gray.shape[0]
            gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor)
        
        # Aumentar el contraste
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        contrasted = clahe.apply(gray)
        
        # Binarización
        _, binary = cv2.threshold(contrasted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary

    def clean_text(self, text):
        """Limpia y valida el texto detectado"""
        if not text:
            return ""
        
        # Eliminar caracteres especiales y líneas nuevas
        text = re.sub(r'[^A-Za-z\s]', '', text)
        # Convertir a mayúsculas
        text = text.upper()
        # Eliminar espacios múltiples y espacios al inicio/final
        text = ' '.join(text.split())
        
        return text if text else ""

    def extract_text(self, image):
        """Extrae texto de la credencial en la imagen"""
        if image is None or image.size == 0:
            return ""
        
        # Encontrar la credencial
        card_rect = self.find_white_card(image)
        if card_rect is None:
            return ""
        
        # Extraer la región de la credencial
        x, y, w, h = card_rect
        card_roi = image[y:y+h, x:x+w]
        
        # Preprocesar la región
        processed_roi = self.preprocess_roi(card_roi)
        
        try:
            # Intentar con diferentes configuraciones
            configs = [
                '--psm 7 --oem 3',  # Línea única
                '--psm 6 --oem 3',  # Bloque uniforme
            ]
            
            for config in configs:
                text = pytesseract.image_to_string(
                    processed_roi,
                    config=config,
                    lang='eng'
                )
                
                cleaned_text = self.clean_text(text)
                if cleaned_text:
                    return cleaned_text
            
            return ""
            
        except Exception as e:
            print(f"Error en OCR: {str(e)}")
            return ""

    def is_valid_id(self, text):
        """Verifica si el texto contiene solo números"""
        if not text:
            return False
        # Eliminar espacios y caracteres no alfanuméricos
        cleaned_text = ''.join(filter(str.isalnum, text))
        # Verificar si el texto limpio contiene solo números
        return cleaned_text.isdigit() 