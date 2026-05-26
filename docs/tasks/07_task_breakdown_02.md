# Step 2. 백엔드 작업 분해: DB & Model

## 1. 분해 기준

DB & Model 작업은 PostgreSQL 설계서와 도메인 모델을 코드 구조에 반영하기 위한 데이터 계층 작업이다.

이 단계에서는 티켓만 정의하며, 실제 SQLAlchemy 코드는 작성하지 않는다.

## 2. DB/Model 작업 목록

- [ ] **DBM-01. 모델 패키지 구조 정리**
  - `models/` 하위에 `user.py`, `equipment.py`, `event.py`, `comment.py` 파일을 둘 수 있도록 구조를 정리한다.
  - `models/__init__.py`에서 4개 모델을 import할 수 있도록 계획한다.

- [ ] **DBM-02. User 모델 설계 반영**
  - `users` 테이블 설계를 SQLAlchemy 모델로 반영할 준비를 한다.
  - 컬럼: `id`, `username`, `role`, `created_at`
  - 제약: username unique, role check

- [ ] **DBM-03. Equipment 모델 설계 반영**
  - `equipment` 테이블 설계를 SQLAlchemy 모델로 반영할 준비를 한다.
  - 컬럼: `id`, `equipment_type`, `location_name`, `status`
  - 제약: equipment_type check, status check

- [ ] **DBM-04. Event 모델 재설계**
  - 기존 `models/event.py`를 DB 설계 기준으로 재정렬한다.
  - 제거 방향: `events.equipment_type`
  - 추가 방향: `user_id`, `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`, `priority`
  - 수정 방향: `equipment_id`를 `equipment.id` 참조 정수 FK로 정리

- [ ] **DBM-05. Comment 모델 설계 반영**
  - `comments` 테이블 설계를 SQLAlchemy 모델로 반영할 준비를 한다.
  - 컬럼: `id`, `event_id`, `user_id`, `content`, `created_at`
  - 제약: content blank 금지

- [ ] **DBM-06. FK 관계 및 삭제 정책 반영**
  - `events.equipment_id -> equipment.id`는 `ON DELETE RESTRICT`
  - `events.user_id -> users.id`는 `ON DELETE SET NULL`
  - `comments.event_id -> events.id`는 `ON DELETE CASCADE`
  - `comments.user_id -> users.id`는 `ON DELETE RESTRICT`

- [ ] **DBM-07. 인덱스 설계 반영**
  - `events.detected_at`, `events.status`, `events.equipment_id`, `events.user_id`, `events.priority`, `(events.status, events.detected_at)` 인덱스 반영
  - `comments.event_id`, `comments.user_id`, `(comments.event_id, comments.created_at)` 인덱스 반영
  - `equipment.equipment_type`, `equipment.status` 인덱스 반영

- [ ] **DBM-08. DB 초기화 import 범위 정리**
  - `init_db()`가 4개 모델을 모두 인식하도록 import 범위를 정리한다.
  - 기존 `models.event`만 import하는 구조를 확장한다.

- [ ] **DBM-09. 기존 개발 DB/볼륨 처리 전략 결정**
  - 현재 이미 생성된 `events` 테이블이 새 설계와 다를 수 있으므로 개발 환경에서는 볼륨 초기화 또는 마이그레이션 전략을 결정한다.
  - MVP 개발 초기에는 볼륨 초기화 방식이 가장 단순하다.

## 3. DB/Model 우선순위

| 우선순위 | 티켓 | 이유 |
| --- | --- | --- |
| 1 | DBM-09 | 기존 DB와 새 설계 충돌을 먼저 처리해야 한다. |
| 2 | DBM-01 | 모델 파일 구조가 선행되어야 한다. |
| 3 | DBM-02, DBM-03 | Event FK 대상 모델이 먼저 필요하다. |
| 4 | DBM-04 | MVP 핵심 Event 모델 정합성 복구 |
| 5 | DBM-05 | Comment는 조건부 기능이지만 도메인 구조상 필요 |
| 6 | DBM-06, DBM-07 | 관계와 조회 성능 제약 반영 |
| 7 | DBM-08 | 모든 모델이 DB 초기화에 반영되도록 마무리 |

## 4. Step 2 결론

DB & Model 작업의 핵심은 현재 `Event` 단일 모델을 최종 DB 설계에 맞는 4개 테이블 구조로 확장하는 것이다.

가장 중요한 수정은 `Event` 모델의 `user_id`, `equipment_id`, bbox, priority 정합성을 맞추는 것이다.
