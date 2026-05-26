# Step 5. PostgreSQL 호환 DDL 스크립트 초안

## 1. 작성 기준

이 DDL은 PostgreSQL 기준 초안이다.

후속 구현 단계에서 SQLAlchemy 모델과 마이그레이션 전략을 정할 때 이 설계를 기준으로 삼는다.

## 2. DDL 초안

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'OPERATOR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_users_role
        CHECK (role IN ('ADMIN', 'OPERATOR'))
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    equipment_type VARCHAR(20) NOT NULL,
    location_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT ck_equipment_type
        CHECK (equipment_type IN ('CCTV', 'DRONE')),
    CONSTRAINT ck_equipment_status
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE'))
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL,
    user_id INTEGER NULL,
    obstacle_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'UNCHECKED',
    image_url VARCHAR(255) NOT NULL,
    bbox_x FLOAT NOT NULL,
    bbox_y FLOAT NOT NULL,
    bbox_width FLOAT NOT NULL,
    bbox_height FLOAT NOT NULL,
    priority INTEGER NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_events_equipment_id
        FOREIGN KEY (equipment_id)
        REFERENCES equipment(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_events_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL,
    CONSTRAINT ck_events_confidence
        CHECK (confidence >= 0.0 AND confidence <= 1.0),
    CONSTRAINT ck_events_latitude
        CHECK (latitude >= -90.0 AND latitude <= 90.0),
    CONSTRAINT ck_events_longitude
        CHECK (longitude >= -180.0 AND longitude <= 180.0),
    CONSTRAINT ck_events_status
        CHECK (status IN ('UNCHECKED', 'CHECKING', 'COMPLETED', 'MISIDENTIFIED')),
    CONSTRAINT ck_events_bbox_x
        CHECK (bbox_x >= 0.0),
    CONSTRAINT ck_events_bbox_y
        CHECK (bbox_y >= 0.0),
    CONSTRAINT ck_events_bbox_width
        CHECK (bbox_width > 0.0),
    CONSTRAINT ck_events_bbox_height
        CHECK (bbox_height > 0.0),
    CONSTRAINT ck_events_priority
        CHECK (priority >= 1)
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_comments_event_id
        FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_comments_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT ck_comments_content_not_blank
        CHECK (LENGTH(BTRIM(content)) > 0)
);

CREATE INDEX idx_events_detected_at
    ON events (detected_at DESC);

CREATE INDEX idx_events_status
    ON events (status);

CREATE INDEX idx_events_equipment_id
    ON events (equipment_id);

CREATE INDEX idx_events_user_id
    ON events (user_id);

CREATE INDEX idx_events_priority
    ON events (priority);

CREATE INDEX idx_events_status_detected_at
    ON events (status, detected_at DESC);

CREATE INDEX idx_comments_event_id
    ON comments (event_id);

CREATE INDEX idx_comments_user_id
    ON comments (user_id);

CREATE INDEX idx_comments_event_created_at
    ON comments (event_id, created_at ASC);

CREATE INDEX idx_equipment_type
    ON equipment (equipment_type);

CREATE INDEX idx_equipment_status
    ON equipment (status);
```

## 3. DDL 적용 순서

| 순서 | 대상 | 이유 |
| --- | --- | --- |
| 1 | `users` | `events`, `comments`가 참조 |
| 2 | `equipment` | `events`가 참조 |
| 3 | `events` | `comments`가 참조 |
| 4 | `comments` | `users`, `events` 참조 |
| 5 | 인덱스 | 테이블 생성 후 조회 최적화 |

## 4. 주의사항

| 항목 | 설명 |
| --- | --- |
| 마이그레이션 | 현재 DB에 기존 `events` 테이블이 있으면 바로 적용하기보다 볼륨 초기화 또는 마이그레이션 전략이 필요하다. |
| SQLAlchemy 반영 | 후속 구현 단계에서 이 DDL과 동일한 모델/제약 조건을 반영해야 한다. |
| priority | 구체 등급 체계는 아직 미정이므로 최소 제약만 둔다. |
| bbox | 좌표 기준은 미정이므로 음수 금지/크기 양수만 강제한다. |

## 5. Step 5 결론

DDL 초안은 4개 핵심 테이블과 MVP 조회 흐름을 위한 인덱스를 포함한다.

위도/경도는 `FLOAT NOT NULL`, `events.user_id`는 nullable FK, `events.equipment_id`는 NOT NULL FK로 설계했다.
