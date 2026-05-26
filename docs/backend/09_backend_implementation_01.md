# Step 1. 구현 지시서 및 변경 범위 확인

## 구현 목표

현재 FastAPI 백엔드 프로젝트의 SQLAlchemy 모델 계층을 최종 데이터베이스 설계와 일치시킨다.

이번 구현은 `users`, `equipment`, `events`, `comments` 4개 테이블에 대응하는 SQLAlchemy 모델을 정리하고, `Base.metadata.create_all()` 기준으로 4개 테이블이 모두 생성 대상에 포함되도록 만드는 것이 목표다.

## 변경 대상 파일

### 생성

- `models/user.py`
- `models/equipment.py`
- `models/comment.py`

### 수정

- `models/event.py`
- `models/__init__.py`
- `database.py`

## 제외 대상

이번 단계에서는 아래 파일과 영역을 수정하지 않는다.

- `main.py`
- `schemas/*`
- `routers/*`
- `services/*`
- `storage/*`
- `docker-compose.yml`
- `ai_model/*`

## 구현 기준

- `ai_model` 원본 파일은 AI 파트 산출물로 보존하고 수정하지 않는다.
- 백엔드 내장 YOLO 추론 모듈은 후속 구현 단계에서 별도 파일로 작성한다.
- 이번 단계는 DB/Model 정합성만 맞춘다.
- 검증 기준은 `python -m compileall database.py models` 성공 및 SQLAlchemy metadata에 `users`, `equipment`, `events`, `comments`가 포함되는 것이다.
