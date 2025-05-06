# Sistema de Control de Accesos con Reconocimiento Facial

Este proyecto consiste en dos aplicaciones que trabajan en conjunto:
1. Sistema de detección y reconocimiento facial
2. Interfaz web para visualización de accesos

## Requisitos Previos

- Python 3.8 o superior
- Webcam conectada al sistema
- Sistema operativo Linux (probado en Ubuntu)
- SQLite3

## Estructura del Proyecto

```
Challenge Computing Vision1/
├── app/
│   ├── main.py              # Aplicación FastAPI
│   ├── templates/           # Templates HTML
│   └── static/             # Archivos estáticos
├── data/
│   ├── access.db           # Base de datos SQLite
│   ├── detected_faces/     # Imágenes de rostros detectados
│   └── authorized_faces/   # Imágenes de rostros autorizados
├── src/
│   └── ...                 # Archivos del sistema de reconocimiento
├── requirements.txt        # Dependencias del proyecto
└── README.md
```

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/GastonGaitan/Challenge-Computing-Visioin1
cd Challenge\ Computing\ Vision1
```

2. Crear y activar el entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución del Sistema

El sistema requiere ejecutar dos aplicaciones simultáneamente en terminales diferentes:

### Terminal 1 - Sistema de Reconocimiento Facial
1. Activar el entorno virtual:
```bash
source venv/bin/activate
```

2. Ejecutar el sistema de reconocimiento:
```bash
python src/main.py
```

Esta aplicación:
- Activa la webcam
- Detecta rostros en tiempo real
- Compara con la base de datos de rostros autorizados
- Registra los accesos en la base de datos

### Terminal 2 - Interfaz Web
1. En una nueva terminal, activar el entorno virtual:
```bash
source venv/bin/activate
```

2. Ejecutar la aplicación web:
```bash
uvicorn app.main:app --reload
```

La interfaz web estará disponible en:
- http://localhost:8000 - Interfaz web principal
- http://localhost:8000/api/accesos - API REST
- http://localhost:8000/docs - Documentación de la API

## Uso del Sistema

1. El sistema de reconocimiento facial (Terminal 1) detectará automáticamente los rostros que aparezcan en la webcam.

2. La interfaz web (Terminal 2) mostrará en tiempo real:
   - ID del acceso
   - Imagen del rostro detectado
   - Nombre de la persona (si está registrada)
   - Fecha y hora del acceso
   - Estado del acceso (Permitido/No autorizado)

## Detener el Sistema

Para detener cualquiera de las aplicaciones:
1. Presionar `Ctrl + C` en la terminal correspondiente
2. Para desactivar el entorno virtual:
```bash
deactivate
```

## Solución de Problemas

1. Si la webcam no se activa:
   - Verificar que la webcam esté conectada
   - Verificar permisos de acceso a la webcam

2. Si las imágenes no se muestran en la interfaz web:
   - Verificar que la carpeta `data/detected_faces` existe y tiene permisos de lectura
   - Verificar que las rutas en el código coinciden con la estructura de tu sistema

3. Si hay problemas con la base de datos:
   - Verificar que `access.db` existe en la carpeta `data/`
   - Verificar permisos de lectura/escritura en la base de datos

## Contribuir

Si deseas contribuir al proyecto:
1. Hacer fork del repositorio
2. Crear una rama para tu feature
3. Hacer commit de tus cambios
4. Crear un pull request

## Licencia

Creado por Gaston Gaitan