# Sistema de Control de Acceso con Reconocimiento Facial

Este sistema implementa un control de acceso que utiliza reconocimiento facial y detección de credenciales mediante OCR.

## Características

- Reconocimiento facial para identificar personas autorizadas
- Detección y lectura de credenciales mediante OCR
- Registro de accesos en base de datos SQLite
- Dashboard web para visualización de accesos

## Requisitos

- Python 3.8+
- OpenCV
- face_recognition
- Tesseract OCR
- Flask (para el dashboard web)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd control-acceso
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Instalar Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
# Windows: Descargar el instalador de https://github.com/UB-Mannheim/tesseract/wiki
```

## Estructura del Proyecto

```
.
├── app/
│   ├── static/
│   ├── templates/
│   ├── database.py
│   ├── face_recognition.py
│   ├── ocr.py
│   └── main.py
├── data/
│   ├── authorized_faces/
│   └── access_logs/
├── requirements.txt
└── README.md
```

## Uso

1. Agregar fotos de personas autorizadas en la carpeta `data/authorized_faces/`
2. Ejecutar la aplicación:
```bash
python app/main.py
```
3. Acceder al dashboard web en `http://localhost:5000`

## Configuración

- Las imágenes de personas autorizadas deben estar en formato JPG
- Cada imagen debe nombrarse con el ID de la persona (ejemplo: "001.jpg")
- La base de datos se creará automáticamente en `data/access.db` 