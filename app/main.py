from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from datetime import datetime
import os

app = FastAPI(title="Sistema de Accesos")

# Configuración de templates y archivos estáticos
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuración de la ruta absoluta para las imágenes
WORKSPACE_PATH = "/home/gastongaitan/Escritorio/Challenge Computing Visioin1"
app.mount("/faces", StaticFiles(directory=os.path.join(WORKSPACE_PATH, "data/detected_faces")), name="faces")

# Configuración de la base de datos
DATABASE_URL = "sqlite:///./data/access.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Rutas
@app.get("/")
async def home(request: Request):
    with engine.connect() as connection:
        # Consulta SQL para obtener los accesos
        query = text("""
            SELECT id, name, person_id, timestamp, face_image_path 
            FROM access_logs 
            ORDER BY timestamp DESC
        """)
        result = connection.execute(query)
        accesos = []
        for row in result:
            try:
                # Intentar parsear el timestamp con microsegundos
                timestamp = datetime.strptime(row.timestamp, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    # Si falla, intentar sin microsegundos
                    timestamp = datetime.strptime(row.timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Si aún falla, usar el timestamp como string
                    timestamp = row.timestamp

            # Ajustar la ruta de la imagen para usar el prefijo /faces/
            imagen_path = row.face_image_path
            if imagen_path:
                # Extraer solo el nombre del archivo de la ruta completa
                imagen_nombre = os.path.basename(imagen_path)
                imagen_path = f"/faces/{imagen_nombre}"

            accesos.append({
                "id": row.id,
                "nombre": row.name,
                "persona_id": row.person_id if row.person_id else "No identificado",
                "timestamp": timestamp,
                "estado": "Permitido" if row.person_id else "No autorizado",
                "imagen": imagen_path
            })
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "accesos": accesos}
    )

@app.get("/api/accesos")
async def get_accesos():
    with engine.connect() as connection:
        query = text("""
            SELECT id, name, person_id, timestamp, face_image_path 
            FROM access_logs 
            ORDER BY timestamp DESC
        """)
        result = connection.execute(query)
        accesos = []
        for row in result:
            imagen_path = row.face_image_path
            if imagen_path:
                imagen_nombre = os.path.basename(imagen_path)
                imagen_path = f"/faces/{imagen_nombre}"
                
            accesos.append({
                "id": row.id,
                "nombre": row.name,
                "persona_id": row.person_id if row.person_id else "No identificado",
                "timestamp": row.timestamp,
                "estado": "Permitido" if row.person_id else "No autorizado",
                "imagen": imagen_path
            })
    return accesos 