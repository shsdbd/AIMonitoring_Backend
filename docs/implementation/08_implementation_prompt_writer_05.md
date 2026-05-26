# Step 5. 최종 개발 지시서

```markdown
# Implementation Prompt: DB/Model 정합성 1차 구현

## 1. 목표

현재 FastAPI 백엔드 프로젝트의 SQLAlchemy 모델 계층을 최종 데이터베이스 설계와 일치시켜라.

이번 작업의 목표는 `users`, `equipment`, `events`, `comments` 4개 테이블에 대응하는 SQLAlchemy 모델을 정리하고, `Base.metadata.create_all()` 기준으로 4개 테이블이 모두 생성 대상에 포함되도록 만드는 것이다.

이번 작업은 **DB/Model 계층만** 다룬다. FastAPI 라우터, 서비스 로직, Pydantic 스키마, API 응답 수정은 하지 마라.

## 2. 현재 상황

현재 프로젝트에는 다음 구조가 있다.

```text
database.py
main.py
models/
├── __init__.py
└── event.py
schemas/
├── __init__.py
└── event.py
```

현재 `models/event.py`는 최종 설계와 맞지 않는다.

- `Event` 모델에 `user_id`가 없다.
- `Event`에 `equipment_type`이 직접 컬럼으로 있다.
- `equipment_id`가 문자열로 되어 있다.
- bbox 필드가 없다.
- priority 필드가 없다.
- `User`, `Equipment`, `Comment` 모델이 없다.
- `database.init_db()`는 `models.event`만 import한다.

현재 `POST /api/v1/events`는 `user_id` 불일치 때문에 500 오류가 발생한 이력이 있다. 다만 이번 작업에서는 API를 고치지 말고 모델 계층만 정리한다.

## 3. 반드시 참조할 문서

- `docs/database/06_database_design_06.md`
- `docs/domain/04_domain_modeling_06.md`
- `docs/architecture/05_architecture_planning_06.md`
- `docs/tasks/07_task_breakdown_06.md`
- `.agent/skills/context_packet.md`

## 4. 변경 범위

### 생성할 파일

- `models/user.py`
- `models/equipment.py`
- `models/comment.py`

### 수정할 파일

- `models/event.py`
- `models/__init__.py`
- `database.py`

### 수정하지 말아야 할 파일

- `main.py`
- `schemas/*`
- `routers/*`
- `services/*`
- `storage/*`
- `docker-compose.yml`

## 5. 구현 상세 요구사항

### 5.1 공통 스타일

- 기존 프로젝트의 SQLAlchemy 2.0 스타일을 유지한다.
- `Mapped`, `mapped_column`을 사용한다.
- 모든 모델은 기존 `database.Base`를 상속한다.
- 테이블명은 다음을 사용한다.
  - `users`
  - `equipment`
  - `events`
  - `comments`
- 불필요한 repository 패턴, service 패턴, 새 프레임워크를 도입하지 마라.

### 5.2 User 모델

`models/user.py`에 `User` 모델을 작성한다.

테이블명: `users`

컬럼:

- `id`: integer primary key autoincrement
- `username`: string length 50, not null, unique
- `role`: string length 20, not null, default `OPERATOR`
- `created_at`: timezone-aware datetime, not null, server default current timestamp

제약:

- `role IN ('ADMIN', 'OPERATOR')`

### 5.3 Equipment 모델

`models/equipment.py`에 `Equipment` 모델을 작성한다.

테이블명: `equipment`

컬럼:

- `id`: integer primary key autoincrement
- `equipment_type`: string length 20, not null
- `location_name`: string length 100, not null
- `status`: string length 20, not null, default `ACTIVE`

제약:

- `equipment_type IN ('CCTV', 'DRONE')`
- `status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')`

인덱스:

- `equipment_type`
- `status`

주의:

- 장비 종류 컬럼명은 `type`이 아니라 반드시 `equipment_type`으로 사용한다.

### 5.4 Event 모델

기존 `models/event.py`의 `Event` 모델을 최종 DB 설계 기준으로 재작성한다.

테이블명: `events`

컬럼:

- `id`: integer primary key autoincrement
- `equipment_id`: integer, foreign key to `equipment.id`, not null
- `user_id`: integer, foreign key to `users.id`, nullable
- `obstacle_type`: string length 50, not null
- `confidence`: float, not null
- `latitude`: float, not null
- `longitude`: float, not null
- `status`: string length 20, not null, default `UNCHECKED`
- `image_url`: string length 255, not null
- `bbox_x`: float, not null
- `bbox_y`: float, not null
- `bbox_width`: float, not null
- `bbox_height`: float, not null
- `priority`: integer, not null
- `detected_at`: timezone-aware datetime, not null, server default current timestamp

제약:

- `confidence >= 0.0 AND confidence <= 1.0`
- `latitude >= -90.0 AND latitude <= 90.0`
- `longitude >= -180.0 AND longitude <= 180.0`
- `status IN ('UNCHECKED', 'CHECKING', 'COMPLETED', 'MISIDENTIFIED')`
- `bbox_x >= 0.0`
- `bbox_y >= 0.0`
- `bbox_width > 0.0`
- `bbox_height > 0.0`
- `priority >= 1`

FK 삭제 정책:

- `equipment_id -> equipment.id`: `ON DELETE RESTRICT`
- `user_id -> users.id`: `ON DELETE SET NULL`

인덱스:

- `detected_at`
- `status`
- `equipment_id`
- `user_id`
- `priority`
- composite index on `(status, detected_at)`

주의:

- 기존 `equipment_type` 직접 컬럼은 제거한다.
- `equipment_id`는 문자열이 아니라 정수 FK로 취급한다.
- `user_id`는 반드시 nullable이어야 한다.
- latitude/longitude는 반드시 float로 둔다.

### 5.5 Comment 모델

`models/comment.py`에 `Comment` 모델을 작성한다.

테이블명: `comments`

컬럼:

- `id`: integer primary key autoincrement
- `event_id`: integer, foreign key to `events.id`, not null
- `user_id`: integer, foreign key to `users.id`, not null
- `content`: string length 500, not null
- `created_at`: timezone-aware datetime, not null, server default current timestamp

제약:

- `content`는 공백 문자열이면 안 된다.

FK 삭제 정책:

- `event_id -> events.id`: `ON DELETE CASCADE`
- `user_id -> users.id`: `ON DELETE RESTRICT`

인덱스:

- `event_id`
- `user_id`
- composite index on `(event_id, created_at)`

### 5.6 models/__init__.py

`models/__init__.py`에서 다음 모델을 import/export한다.

- `User`
- `Equipment`
- `Event`
- `Comment`

### 5.7 database.py

`init_db()`가 4개 모델을 모두 import하도록 수정한다.

목표는 `Base.metadata.create_all(bind=ENGINE)` 실행 시 4개 테이블이 metadata에 포함되는 것이다.

`SessionLocal`, `ENGINE`, `Base`, `DATABASE_URL` 구조는 변경하지 마라.

## 6. 검증 방법

다음 검증을 수행한다.

```bash
python -m compileall database.py models
```

가능하면 Python에서 다음도 확인한다.

```text
from database import Base
import models
Base.metadata.tables.keys()
```

기대 결과:

- `users`
- `equipment`
- `events`
- `comments`

위 네 테이블명이 metadata에 포함되어야 한다.

DB를 실제로 초기화할 경우, PostgreSQL에서 다음 테이블이 생성되어야 한다.

- `users`
- `equipment`
- `events`
- `comments`

## 7. 이번 작업에서 하지 말 것

- `main.py` 수정 금지
- Pydantic 스키마 수정 금지
- FastAPI router 작성 금지
- service 계층 작성 금지
- storage 계층 작성 금지
- Alembic 도입 금지
- Docker Compose 수정 금지
- DB 볼륨 삭제 실행 금지
- API 동작 성공까지 억지로 맞추지 말 것

이번 작업 후 API가 아직 실패할 수 있다. 그것은 정상이다. API 복구는 후속 티켓인 Event schema/service/router 작업에서 처리한다.

## 8. 완료 기준

- `models/user.py`, `models/equipment.py`, `models/comment.py`가 생성되어 있다.
- `models/event.py`가 최종 DB 설계 기준으로 수정되어 있다.
- `models/__init__.py`가 4개 모델을 export한다.
- `database.init_db()`가 4개 모델을 모두 import한다.
- `python -m compileall database.py models`가 성공한다.
- `Base.metadata.tables.keys()`에 `users`, `equipment`, `events`, `comments`가 포함된다.
```
