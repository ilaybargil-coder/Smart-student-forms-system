from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from db import engine
from models import Base
from routes.requests import router as requests_router
from routes.auth import router as auth_router
from routes import users
app = FastAPI()

# --- CORS (שמים לפני routers) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # לפיתוח
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Frontend serve ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "Frontend")

# סטטיים (JS/CSS/HTML)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))



@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


@app.get("/health")
def health():
    return {"ok": True}




# --- Routers ---
app.include_router(auth_router)
app.include_router(requests_router)


# --- DB tables (אופציונלי; אם Supabase כבר יצר, אפשר לכבות)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[WARN] create_all skipped: {e}")


from routes.courses import router as courses_router
from routes.request_types import router as request_types_router

app.include_router(courses_router)
app.include_router(request_types_router)
app.include_router(users.router)