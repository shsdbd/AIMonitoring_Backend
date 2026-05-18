from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db

# 1. FastAPI 앱 인스턴스 생성 및 Swagger 문서 타이틀 설정
app = FastAPI(
    title="도로 관제 시스템 API 서버",
    description="AI 모듈 및 프론트엔드 대시보드 연동을 위한 REST API",
    version="1.0.0"
)

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
