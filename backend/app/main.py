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

# ---- App ----
app = FastAPI(title="MusicScope API")

# ---- CORS ----
# In Railway/production, it's easy for the frontend domain to differ (preview, custom domain, etc.).
# So we support an env var and fall back to allowing all origins.
# Examples:
#   ALLOWED_ORIGINS=https://musicscope-frontend-production.up.railway.app,https://mydomain.com
#   ALLOWED_ORIGINS=*
allowed_origins_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "https://musicscope-frontend-production.up.railway.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
)

allowed_origins_raw = allowed_origins_raw.strip()
if allowed_origins_raw == "*":
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(etl_router)
app.include_router(analytics_router)

@app.get("/health")
def health():
    return {"status": "ok"}