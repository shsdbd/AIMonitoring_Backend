# Step 3. 변경 범위 및 예상 결과 정의

## 1. 생성할 파일

| 파일 | 목적 |
| --- | --- |
| `models/user.py` | `users` 테이블 SQLAlchemy 모델 |
| `models/equipment.py` | `equipment` 테이블 SQLAlchemy 모델 |
| `models/comment.py` | `comments` 테이블 SQLAlchemy 모델 |

## 2. 수정할 파일

| 파일 | 수정 목적 |
| --- | --- |
| `models/event.py` | 최종 DB 설계 기준으로 Event 모델 재정렬 |
| `models/__init__.py` | 4개 모델 import/export |
| `database.py` | `init_db()`가 4개 모델을 모두 인식하도록 import 정리 |

## 3. 수정하지 않을 파일

| 파일/영역 | 이유 |
| --- | --- |
| `main.py` | 라우터/서비스 분리는 후속 티켓이다. |
| `schemas/` | Pydantic 스키마 정리는 후속 티켓이다. |
| `routers/` | 아직 생성하지 않는다. |
| `services/` | 아직 생성하지 않는다. |
| `storage/` | 아직 생성하지 않는다. |
| `docker-compose.yml` | DB 인프라 설정은 변경하지 않는다. |

## 4. 모델별 예상 결과

### User

`users` 테이블을 표현해야 한다.

필수 컬럼:

- `id`
- `username`
- `role`
- `created_at`

필수 제약:

- `username` unique
- `role IN ('ADMIN', 'OPERATOR')`
- `role` 기본값은 `OPERATOR`
- `created_at` 기본값은 DB 현재 시각

### Equipment

`equipment` 테이블을 표현해야 한다.

필수 컬럼:

- `id`
- `equipment_type`
- `location_name`
- `status`

필수 제약:

- `equipment_type IN ('CCTV', 'DRONE')`
- `status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')`
- `status` 기본값은 `ACTIVE`

### Event

`events` 테이블을 표현해야 한다.

필수 컬럼:

- `id`
- `equipment_id`
- `user_id`
- `obstacle_type`
- `confidence`
- `latitude`
- `longitude`
- `status`
- `image_url`
- `bbox_x`
- `bbox_y`
- `bbox_width`
- `bbox_height`
- `priority`
- `detected_at`

필수 제약:

- `equipment_id -> equipment.id`, NOT NULL
- `user_id -> users.id`, nullable
- `confidence`는 0.0 이상 1.0 이하
- `latitude`는 -90.0 이상 90.0 이하
- `longitude`는 -180.0 이상 180.0 이하
- `status IN ('UNCHECKED', 'CHECKING', 'COMPLETED', 'MISIDENTIFIED')`
- `bbox_x`, `bbox_y`는 0 이상
- `bbox_width`, `bbox_height`는 0 초과
- `priority`는 1 이상
- `status` 기본값은 `UNCHECKED`
- `detected_at` 기본값은 DB 현재 시각

주의:

- 기존 `events.equipment_type` 직접 컬럼은 제거한다.
- `equipment_id`는 문자열이 아니라 정수 FK로 취급한다.

### Comment

`comments` 테이블을 표현해야 한다.

필수 컬럼:

- `id`
- `event_id`
- `user_id`
- `content`
- `created_at`

필수 제약:

- `event_id -> events.id`
- `user_id -> users.id`
- `content`는 공백 문자열 금지
- `created_at` 기본값은 DB 현재 시각

## 5. 인덱스 예상 결과

모델 또는 SQLAlchemy table args에 다음 인덱스가 반영되어야 한다.

- `events.detected_at`
- `events.status`
- `events.equipment_id`
- `events.user_id`
- `events.priority`
- `(events.status, events.detected_at)`
- `comments.event_id`
- `comments.user_id`
- `(comments.event_id, comments.created_at)`
- `equipment.equipment_type`
- `equipment.status`

## 6. Step 3 결론

변경 범위는 `models/`와 `database.py`에 한정한다.

결과적으로 SQLAlchemy 모델 계층이 최종 데이터베이스 설계서와 일치해야 하며, API 계층은 후속 티켓에서 별도로 정리한다.
