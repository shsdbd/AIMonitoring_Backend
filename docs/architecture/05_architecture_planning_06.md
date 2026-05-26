# Step 6. 최종 아키텍처 정의서

## 1. 문서 목적

이 문서는 `architecture-planning` 단계의 최종 산출물이다.

확정된 MVP 범위와 도메인 모델을 바탕으로 FastAPI 백엔드의 폴더 구조, 계층 구조, 모듈 책임, 예외 처리, 의존성 주입 구조를 정의한다.

## 2. 현재 아키텍처 요약

현재 프로젝트는 다음과 같은 단순 프로토타입 구조다.

```text
AIMonitoring_Backend/
├── database.py
├── docker-compose.yml
├── main.py
├── models/
│   └── event.py
└── schemas/
    └── event.py
```

현재 `main.py`는 FastAPI 앱 생성, CORS, static 마운트, DB dependency, 이미지 저장, 이벤트 라우팅과 비즈니스 흐름을 모두 포함한다.

## 3. 목표 아키텍처

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

## 4. 계층별 책임

| 계층 | 책임 |
| --- | --- |
| `main.py` | 앱 생성, CORS 등록, static 마운트, 라우터 등록, startup 초기화 |
| `core/` | 설정, 공통 에러, 전역 예외 처리 |
| `dependencies/` | DB 세션, 인증/AI 검증 등 FastAPI dependency |
| `models/` | SQLAlchemy 도메인 모델 |
| `schemas/` | Pydantic 요청/응답 스키마 |
| `routers/` | HTTP 엔드포인트 선언 |
| `services/` | 비즈니스 유스케이스 처리 |
| `storage/` | 이미지 저장 및 정적 URL 생성 |
| `static/` | 업로드 이미지 파일 저장소 |

## 5. 기존 자산 보존 정책

| 기존 자산 | 보존 방식 |
| --- | --- |
| CORS 미들웨어 | `main.py` 앱 초기화 단계에서 유지 |
| `/static` 마운트 | `main.py`에서 유지 |
| 이미지 저장 경로 | `static/images/{YYYY}/{MM}/{DD}/` 정책 유지 |
| DB 세션 생성 | `SessionLocal` 기반 흐름 유지 후 dependency로 분리 |
| Docker Compose DB 연결 | `DATABASE_URL` 환경변수 기반 구조 유지 |

## 6. 모듈 경계 규칙

| 계층 | 참조 가능 |
| --- | --- |
| `routers/` | `schemas`, `services`, `dependencies` |
| `services/` | `models`, `storage`, `core.errors` |
| `models/` | `database.Base`, SQLAlchemy 공통 요소 |
| `schemas/` | Pydantic, 표준 타입 |
| `dependencies/` | `database`, `core`, 인증 유틸 |
| `storage/` | 파일 시스템, 설정 |
| `core/` | 표준 라이브러리, 설정 |

금지 규칙:

- `models`는 `schemas`, `routers`, `services`를 참조하지 않는다.
- `schemas`는 `models`를 참조하지 않는다.
- `services`는 `routers`를 참조하지 않는다.
- `main.py`에는 도메인 비즈니스 로직을 작성하지 않는다.

## 7. 도메인별 모듈 책임

| 도메인 | Router | Service | Model | Schema |
| --- | --- | --- | --- | --- |
| Event | 이벤트 등록, 목록/상세, 상태 변경 엔드포인트 | 이벤트 등록, 조회, 상태 변경 유스케이스 | Event 영속성 모델 | Event 요청/응답 검증 |
| Equipment | 조건부 장비 조회/관리 엔드포인트 | 장비 식별/검증 | Equipment 모델 | Equipment 스키마 |
| User | 조건부 사용자 조회/관리 엔드포인트 | 사용자 식별/검증 | User 모델 | User 스키마 |
| Comment | 조건부 코멘트 작성/조회 엔드포인트 | 처리 기록 작성/조회 | Comment 모델 | Comment 스키마 |

## 8. 예외 처리 설계

공통 오류 응답은 다음 구조를 목표로 한다.

```json
{
  "error_code": "EVENT_NOT_FOUND",
  "message": "해당 이벤트를 찾을 수 없습니다.",
  "detail": null
}
```

MVP 우선 에러:

| 에러 코드 | 상황 |
| --- | --- |
| `EVENT_NOT_FOUND` | 이벤트 없음 |
| `INVALID_EVENT_STATUS` | 잘못된 상태값 |
| `INVALID_EVENT_PAYLOAD` | 필수 탐지 정보 부족 |
| `INVALID_IMAGE_FILE` | 잘못된 이미지 파일 |
| `EQUIPMENT_NOT_FOUND` | 참조 장비 없음 |

## 9. DI 설계

| Dependency | 위치 | 목적 |
| --- | --- | --- |
| `get_db` | `dependencies/database.py` | 요청 단위 DB 세션 제공 |
| `get_current_user` | `dependencies/auth.py` | 조건부 관제사 식별 |
| `require_operator` | `dependencies/auth.py` | 조건부 관제사 권한 확인 |
| `verify_ai_source` | `dependencies/auth.py` | 조건부 AI 요청 신뢰성 확인 |

MVP에서는 `get_db` 안정화를 우선하고, 인증 관련 dependency는 조건부 포함 범위에 맞춰 단계화한다.

## 10. MVP 구현 우선순위

| 우선순위 | 대상 |
| --- | --- |
| 1 | Event router/service/schema/model 정합성 복구 |
| 2 | 이미지 저장 책임을 `storage/image_storage.py`로 분리 |
| 3 | Equipment/User 모델과 참조 구조 정리 |
| 4 | Comment 조건부 기능 구조 마련 |
| 5 | 공통 에러와 전역 예외 처리 도입 |
| 6 | 인증/AI 검증 dependency 조건부 도입 |

## 11. 최종 결론

최종 아키텍처는 FastAPI의 계층형 구조를 따른다.

`main.py`는 앱 조립과 공통 미들웨어 등록만 담당하고, 도메인 기능은 `routers`, `services`, `models`, `schemas`로 분리한다.

기존 CORS, static 파일 마운트, Docker 기반 DB 연결은 보존하며, MVP 핵심인 Event 흐름을 우선 안정화한 뒤 User, Equipment, Comment를 점진적으로 확장한다.
