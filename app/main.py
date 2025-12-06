from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth import router as auth_router
from .routers import processos, oab, documentos
from .database import engine, Base

# Create tables (for dev only - usage of Alembic is recommended for prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Judicial API",
    description="API para consulta de processos e automação jurídica",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(processos.router, prefix="/processos", tags=["Processos"])
app.include_router(oab.router, prefix="/oab", tags=["OAB"])
app.include_router(documentos.router, prefix="/documentos", tags=["Documentos"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "judicial-api"}

@app.get("/")
def read_root():
    return {"message": "Judicial API Running", "status": "ok"}

