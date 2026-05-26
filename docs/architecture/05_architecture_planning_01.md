# Step 1. 기존 아키텍처 분석

## 1. 분석 목적

현재 프로젝트의 코드 구조를 확인하고, MVP 구현을 위해 어떤 구조적 개선이 필요한지 정리한다.

이 단계는 설계 분석이며, 소스 코드 수정이나 구현은 수행하지 않는다.

## 2. 현재 파일 구조

```text
AIMonitoring_Backend/
├── database.py
├── docker-compose.yml
├── main.py
├── models/
│   ├── __init__.py
│   └── event.py
└── schemas/
    ├── __init__.py
    └── event.py
```

## 3. 현재 구성 요소 분석

| 파일 | 현재 역할 |
| --- | --- |
| `main.py` | FastAPI 앱 생성, CORS 설정, static 파일 마운트, DB 세션 의존성, 이미지 저장 함수, 이벤트 생성/조회/상태 변경 라우트 포함 |
| `database.py` | DB 연결 URL, SQLAlchemy 엔진, 세션 팩토리, Base, 초기 테이블 생성 함수 포함 |
| `models/event.py` | `Event` SQLAlchemy 모델 정의 |
| `schemas/event.py` | `EventCreate`, `EventRead` Pydantic 스키마 정의 |
| `docker-compose.yml` | PostgreSQL 컨테이너와 FastAPI 웹 컨테이너 구성 |

## 4. 현재 아키텍처의 장점

| 장점 | 설명 |
| --- | --- |
| 단순성 | 파일 수가 적어 초기 프로토타입을 이해하기 쉽다. |
| 기본 실행 흐름 존재 | FastAPI 앱, DB 연결, 정적 파일 서빙, 이벤트 API가 한 번에 연결되어 있다. |
| Docker 기반 인프라 | PostgreSQL과 웹 서버가 Docker Compose로 분리되어 있다. |
| Swagger 검증 용이 | FastAPI 기본 문서로 API 테스트가 가능하다. |

## 5. 현재 아키텍처의 문제점

| 문제 | 설명 | 영향 |
| --- | --- | --- |
| `main.py` 책임 과다 | 앱 생성, 라우팅, 파일 저장, DB 세션, 비즈니스 흐름이 한 파일에 섞여 있다. | 기능 확장 시 유지보수가 어려워진다. |
| 라우터 계층 부재 | 도메인별 API 라우터가 분리되어 있지 않다. | User, Equipment, Comment 확장 시 `main.py`가 비대해진다. |
| 서비스 계층 부재 | 이벤트 등록/상태 변경 같은 핵심 흐름이 라우터에 직접 들어간다. | 테스트와 재사용이 어렵다. |
| 공통 의존성 위치 불명확 | `get_db`가 `main.py`에 있다. | 여러 라우터에서 재사용하기 어렵다. |
| 파일 저장 책임 분리 미흡 | 이미지 저장 함수가 `main.py`에 있다. | 파일 저장 정책 변경 시 라우터와 앱 초기화 코드가 함께 흔들린다. |
| 모델-스키마-라우트 불일치 | `user_id`, `equipment_type`, `equipment_id` 계약이 서로 맞지 않는다. | 현재 POST 이벤트 생성에서 500 오류가 발생한다. |
| 도메인 확장 미반영 | `User`, `Equipment`, `Comment` 모델/스키마/라우터가 없다. | 확정 도메인 모델과 코드 구조가 맞지 않는다. |

## 6. 반드시 보존해야 할 기존 자산

| 자산 | 보존 방향 |
| --- | --- |
| CORS 설정 | `main.py` 또는 앱 팩토리에서 유지한다. |
| StaticFiles 마운트 | `/static` 경로와 이미지 저장/서빙 흐름을 유지한다. |
| 이미지 저장 디렉터리 | 기존 `static/images/{YYYY}/{MM}/{DD}/` 정책을 유지하거나 동일 책임 모듈로 이동한다. |
| DB 세션 생성 | 기존 SQLAlchemy 세션 흐름을 공통 dependency로 이동해 재사용한다. |
| Docker Compose DB 연결 | `DATABASE_URL` 환경변수 기반 연결을 유지한다. |

## 7. 목표 아키텍처 방향

| 방향 | 설명 |
| --- | --- |
| 계층 분리 | App 초기화, Router, Service, Model, Schema, Dependency를 분리한다. |
| 도메인별 모듈화 | Event, User, Equipment, Comment 별 파일을 둔다. |
| 기존 동작 보존 | CORS, static 마운트, Docker 기반 실행 흐름은 깨지지 않게 한다. |
| MVP 우선 | Must-have인 Event 흐름을 우선 안정화하고 조건부 기능은 확장 가능하게 둔다. |
| 조기 구현 금지 | 이 단계에서는 구조만 정의하고 코드 변경은 하지 않는다. |

## 8. Step 1 결론

현재 프로젝트는 `Event` 중심 프로토타입으로, 기본 FastAPI 앱과 DB 연결은 존재하지만 계층 분리가 부족하다.

아키텍처 계획의 핵심은 `main.py`에 집중된 책임을 `routers`, `services`, `dependencies`, `core`, `models`, `schemas`로 분리하면서 기존 CORS와 static 파일 서빙 구조를 보존하는 것이다.
