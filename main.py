from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
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

# 1. FastAPI 앱 인스턴스 생성 및 Swagger 문서 타이틀 설정
app = FastAPI(
    title="도로 관제 시스템 API 서버",
    description="AI 모듈 및 프론트엔드 대시보드 연동을 위한 REST API",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 2. CORS 미들웨어 설정 (프론트엔드 React 포트와의 연동 에러 방지)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 모든 접근을 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 서버 초기화 시 테이블이 없으면 자동 생성
@app.on_event("startup")
def on_startup():
    init_db()


# 3. 서버 정상 구동 확인용 기본 엔드포인트
@app.get("/")
def read_root():
    return {"status": "running", "message": "도로 관제 시스템 백엔드 서버가 정상 구동 중입니다."}


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

    event = Event(
        equipment_type=event_data.equipment_type,
        equipment_id=event_data.equipment_id,
        obstacle_type=event_data.obstacle_type,
        confidence=event_data.confidence,
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        image_url=image_url,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


# 4. 프론트엔드가 폴링 테스트를 해볼 수 있는 샘플 데이터 엔드포인트
@app.get("/api/v1/events/sample")
def get_sample_event():
    return {
        "id": 1,
        "equipment_type": "DRONE",
        "obstacle_type": "ANIMAL_CORPSE",
        "status": "UNCHECKED",
        "latitude": 37.5665,
        "longitude": 126.9780
    }
# main.py 파일 맨 아래에 그대로 추가하세요.

from fastapi import Body  # 💡 파일 최상단 fastapi import 문에 Body를 추가하거나 여기에 명시 유지가능

# 4. 전체 이벤트 목록 조회 API (실제 Docker DB 연동 완료)
@app.get("/api/v1/events", response_model=list[EventRead])
def get_all_events(db: Session = Depends(get_db)):
    """
    DB에 누적된 도로 장애물 탐지 이벤트 전체 목록을 최신순(ID 역순)으로 조회합니다.
    """
    return db.query(Event).order_by(Event.id.desc()).all()


# 5. 관제사 상태 변경 API (2차 보고서 명세 Body 포맷 100% 일치)
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
    Body 포맷 규격: {"status": "COMPLETED"}
    """
    # 1. DB 내 해당 이벤트 존재 여부 검증
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="해당 이벤트를 찾을 수 없습니다.")
    
    # 2. 데이터 업데이트 및 트랜잭션 커밋
    event.status = status
    db.commit()
    db.refresh(event)
    
    return event