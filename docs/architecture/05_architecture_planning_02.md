# Step 2. 디렉토리 구조 및 계층 설계

## 1. 설계 기준

확정된 MVP 범위와 도메인 모델을 바탕으로 FastAPI 백엔드 구조를 계층형으로 분리한다.

이 구조는 구현 지시가 아니라 후속 구현 단계에서 따라야 할 설계 기준이다.

## 2. 제안 디렉토리 구조

```text
AIMonitoring_Backend/
├── main.py
├── database.py
├── docker-compose.yml
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── errors.py
│   └── exception_handlers.py
├── dependencies/
│   ├── __init__.py
│   ├── database.py
│   └── auth.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── equipment.py
│   ├── event.py
│   └── comment.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── equipment.py
│   ├── event.py
│   └── comment.py
├── routers/
│   ├── __init__.py
│   ├── health.py
│   ├── events.py
│   ├── users.py
│   ├── equipment.py
│   └── comments.py
├── services/
│   ├── __init__.py
│   ├── event_service.py
│   ├── user_service.py
│   ├── equipment_service.py
│   └── comment_service.py
├── storage/
│   ├── __init__.py
│   └── image_storage.py
└── static/
    └── images/
```

## 3. 계층별 책임

| 계층 | 책임 | 예시 |
| --- | --- | --- |
| `main.py` | FastAPI 앱 생성, 미들웨어 등록, static 마운트, 라우터 등록 | CORS, `/static`, router include |
| `core/` | 설정, 공통 예외, 전역 핸들러 | 환경 설정, 비즈니스 에러 클래스 |
| `dependencies/` | FastAPI dependency 모음 | DB 세션, 현재 사용자, AI 인증 |
| `models/` | SQLAlchemy 도메인 모델 | User, Equipment, Event, Comment |
| `schemas/` | Pydantic 요청/응답 스키마 | EventCreate, EventRead |
| `routers/` | HTTP 엔드포인트 선언과 요청/응답 연결 | events router, comments router |
| `services/` | 도메인 유스케이스와 비즈니스 흐름 | 이벤트 등록, 상태 변경 |
| `storage/` | 파일 저장/조회 정책 | 이미지 저장, static URL 생성 |
| `static/` | 정적 파일 저장소 | 업로드 이미지 |

## 4. 계층 흐름

```text
Client / AI Module / Frontend
        ↓
routers/
        ↓
services/
        ↓
models/ + database session
        ↓
PostgreSQL

파일 업로드 흐름:
routers/ -> services/ -> storage/ -> static/images/
```

## 5. `main.py`의 목표 책임

`main.py`는 앱 조립 지점으로만 사용한다.

| 유지할 책임 | 분리할 책임 |
| --- | --- |
| FastAPI 인스턴스 생성 | 이벤트 생성/조회/상태 변경 로직 |
| CORS 미들웨어 등록 | 이미지 저장 함수 |
| static 파일 마운트 | DB 세션 dependency |
| 라우터 등록 | SQLAlchemy 쿼리/비즈니스 로직 |
| startup 초기화 | 도메인별 처리 흐름 |

## 6. MVP 우선 구현 순서에 맞는 구조

| 우선순위 | 모듈 | 이유 |
| --- | --- | --- |
| 1 | `routers/events.py`, `services/event_service.py`, `schemas/event.py`, `models/event.py` | MVP 핵심 흐름 |
| 2 | `storage/image_storage.py` | 탐지 근거 이미지/참조 처리 |
| 3 | `models/equipment.py`, `schemas/equipment.py` | Event의 탐지 장비 참조 |
| 4 | `models/user.py`, `schemas/user.py` | Event의 관제사 참조 |
| 5 | `models/comment.py`, `schemas/comment.py`, `routers/comments.py` | 조건부 처리 기록 기능 |
| 6 | `dependencies/auth.py` | 조건부 접근 통제 |

## 7. Step 2 결론

제안 아키텍처는 `main.py`를 앱 조립 전용으로 축소하고, 도메인별 라우터/서비스/모델/스키마를 분리하는 계층형 구조다.

MVP 구현에서는 Event 흐름을 우선 분리하고, User, Equipment, Comment는 확정 도메인 모델에 맞춰 점진적으로 확장한다.
