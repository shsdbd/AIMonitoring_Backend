from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers.events import router as events_router
from routers.health import router as health_router

STATIC_DIR = Path("static")
IMAGE_DIR = STATIC_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="도로 관제 시스템 API 서버",
    description="AI 모듈 및 프론트엔드 대시보드 연동을 위한 REST API",
    version="1.3.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(events_router)


@app.on_event("startup")
def on_startup():
    init_db()
