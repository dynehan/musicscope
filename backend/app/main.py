from dotenv import load_dotenv
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.etl import router as etl_router
from app.api.analytics import router as analytics_router

from create_tables import init_db

# load .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

# CORS origins: comma-separated list in env (useful for Railway), with local dev defaults
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
)
cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

# create app FIRST
app = FastAPI(title="MusicScope API")

@app.on_event("startup")
def _startup_create_tables():
    init_db()


# CORS (only once)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(etl_router)
app.include_router(analytics_router)

@app.get("/health")
def health():
    return {"status": "ok"}