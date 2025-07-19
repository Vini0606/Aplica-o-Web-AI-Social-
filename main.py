# main.py

import os
from fastapi import FastAPI
from dotenv import load_dotenv
from config import settings
from models import create_db_tables

# Importar os routers
from api.v1.endpoints import brief_routes
from api.v1.endpoints import data_routes
from api.v1.endpoints import report_routes
from auth.auth_routes import auth_router

load_dotenv(override=True)

app = FastAPI(
    title="AI Social Media Analysis API",
    description="API para análise de mídias sociais e geração de relatórios.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    create_db_tables()
    os.makedirs(settings.REPORTS_PATH, exist_ok=True)
    os.makedirs(settings.RAW_DATA_PATH, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_PATH, exist_ok=True)

# Incluir os routers na aplicação principal
app.include_router(auth_router, prefix="/api/v1")
app.include_router(brief_routes.router, prefix="/api/v1")
app.include_router(data_routes.router, prefix="/api/v1")
app.include_router(report_routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à AI Social Media Analysis API! Acesse /docs para a documentação interativa."}