from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models.event import Event
from schemas.event import EventCreate, EventRead

STATIC_DIR = Path("static")
IMAGE_DIR = STATIC_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def save_upload_image(image: UploadFile) -> str:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일만 업로드할 수 있습니다.",
        )

    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    date_path = datetime.now().strftime("%Y/%m/%d")
    save_dir = IMAGE_DIR / date_path
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{suffix}"
    save_path = save_dir / filename

    with save_path.open("wb") as buffer:
        while chunk := await image.read(1024 * 1024):
            buffer.write(chunk)

    return f"/static/images/{date_path}/{filename}"


# FastAPI 앱 인스턴스 생성 및 Swagger 문서 타이틀 설정
app = FastAPI(
    title="도로 관제 시스템 API 서버",
    description="AI 모듈 및 프론트엔드 대시보드 연동을 위한 REST API (위경도 좌표 및 ERD 적용 버전)",
    version="1.2.0"
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def read_root():
    return {"status": "running", "message": "도로 관제 시스템 백엔드 서버가 정상 가동 중입니다."}


# 4. AI 모듈 장애물 실시간 수신 API (위도/경도 데이터 포함)
@app.post(
    "/api/v1/events",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    event_data: EventCreate = Depends(EventCreate.as_form),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    image_url = await save_upload_image(image)

    # 💡 ERD 구조와 관제 필수 좌표(위경도)를 모두 결합하여 DB에 저장
    event = Event(
        equipment_id=int(event_data.equipment_id),
        user_id=None,  # 최초 탐지 시 관제사 미배정
        obstacle_type=event_data.obstacle_type,
        confidence=event_data.confidence,
        latitude=event_data.latitude,    # 위도 반영
        longitude=event_data.longitude,  # 경도 반영
        status="UNCHECKED",
        image_url=image_url,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


# 5. 프론트엔드 대시보드 샘플 엔드포인트
@app.get("/api/v1/events/sample")
def get_sample_event():
    return {
        "id": 1,
        "equipment_id": 101,
        "user_id": None,
        "obstacle_type": "ANIMAL_CORPSE",
        "confidence": 0.95,
        "status": "UNCHECKED",
        "latitude": 37.5665,   # 샘플 좌표 (서울 시청)
        "longitude": 126.9780,
        "image_url": "/static/images/sample.jpg",
        "detected_at": datetime.now().isoformat()
    }


# 6. 전체 이벤트 목록 조회 API
@app.get("/api/v1/events", response_model=list[EventRead])
def get_all_events(db: Session = Depends(get_db)):
    """
    DB에 누적된 도로 장애물 탐지 이벤트 전체 목록을 최신순(ID 역순)으로 조회합니다.
    """
    return db.query(Event).order_by(Event.id.desc()).all()


# 7. 관제사 상태 변경 API
@app.patch("/api/v1/events/{event_id}/status", response_model=EventRead)
def update_event_status(
    event_id: int,
    status: str = Body(
        ..., 
        embed=True, 
        pattern="^(UNCHECKED|CHECKING|COMPLETED|MISIDENTIFIED)$"
    ),
    db: Session = Depends(get_db)
):
    """
    특정 이벤트의 처리 상태를 업데이트합니다.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="해당 이벤트를 찾을 수 없습니다.")
    
    event.status = status
    db.commit()
    db.refresh(event)
    
    return event