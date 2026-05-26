from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/")
def read_root() -> dict[str, str]:
    return {
        "status": "running",
        "message": "도로 관제 시스템 백엔드 서버가 정상 가동 중입니다.",
    }
