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

            accesos.append({
                "id": row.id,
                "nombre": row.name,
                "persona_id": row.person_id if row.person_id else "No identificado",
                "timestamp": timestamp,
                "estado": "Permitido" if row.person_id else "No autorizado",
                "imagen": row.face_image_path
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
            accesos.append({
                "id": row.id,
                "nombre": row.name,
                "persona_id": row.person_id if row.person_id else "No identificado",
                "timestamp": row.timestamp,
                "estado": "Permitido" if row.person_id else "No autorizado",
                "imagen": row.face_image_path
            })
    return accesos 