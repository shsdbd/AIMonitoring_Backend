import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.exception_handlers import validation_exception_handler
from database import init_db
from routers.events import compat_router as events_compat_router
from routers.events import router as events_router
from routers.health import router as health_router

STATIC_DIR = Path("static")
IMAGE_DIR = STATIC_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CORS_ORIGINS = [
    "https://roadkill-detection.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ORIGINS")
    if not configured_origins:
        return DEFAULT_CORS_ORIGINS

    return [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]


app = FastAPI(
    title="도로 관제 시스템 API 서버",
    description="AI 모듈 및 프론트엔드 대시보드 연동을 위한 REST API",
    version="1.3.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(events_compat_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.on_event("startup")
def on_startup():
    init_db()
