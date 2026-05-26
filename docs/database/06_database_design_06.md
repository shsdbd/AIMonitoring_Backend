# Step 6. 최종 데이터베이스 설계서

## 1. 문서 목적

이 문서는 `database-design` 단계의 최종 산출물이다.

확정된 도메인 모델과 아키텍처 계획을 바탕으로 PostgreSQL에 생성할 물리 테이블, 컬럼, 제약 조건, 인덱스, DDL 초안을 정의한다.

## 2. 최종 테이블 목록

| 테이블 | 설명 |
| --- | --- |
| `users` | 도로 관제사 또는 시스템 사용자 |
| `equipment` | CCTV/드론 등 탐지 장비 |
| `events` | AI가 탐지한 도로 장애물 이벤트 |
| `comments` | 이벤트별 처리 기록 또는 확인 메모 |

## 3. 최종 관계

| 관계 | FK | 삭제 정책 |
| --- | --- | --- |
| `users` -> `events` | `events.user_id` | `ON DELETE SET NULL` |
| `equipment` -> `events` | `events.equipment_id` | `ON DELETE RESTRICT` |
| `users` -> `comments` | `comments.user_id` | `ON DELETE RESTRICT` |
| `events` -> `comments` | `comments.event_id` | `ON DELETE CASCADE` |

## 4. 핵심 테이블 스펙 요약

### `users`

| 컬럼 | 타입 | Nullability | 기본값 |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 |
| `username` | `VARCHAR(50)` | `NOT NULL` | 없음 |
| `role` | `VARCHAR(20)` | `NOT NULL` | `'OPERATOR'` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` |

### `equipment`

| 컬럼 | 타입 | Nullability | 기본값 |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 |
| `equipment_type` | `VARCHAR(20)` | `NOT NULL` | 없음 |
| `location_name` | `VARCHAR(100)` | `NOT NULL` | 없음 |
| `status` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` |

### `events`

| 컬럼 | 타입 | Nullability | 기본값 |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 |
| `equipment_id` | `INTEGER` | `NOT NULL` | 없음 |
| `user_id` | `INTEGER` | `NULL` | `NULL` |
| `obstacle_type` | `VARCHAR(50)` | `NOT NULL` | 없음 |
| `confidence` | `FLOAT` | `NOT NULL` | 없음 |
| `latitude` | `FLOAT` | `NOT NULL` | 없음 |
| `longitude` | `FLOAT` | `NOT NULL` | 없음 |
| `status` | `VARCHAR(20)` | `NOT NULL` | `'UNCHECKED'` |
| `image_url` | `VARCHAR(255)` | `NOT NULL` | 없음 |
| `bbox_x` | `FLOAT` | `NOT NULL` | 없음 |
| `bbox_y` | `FLOAT` | `NOT NULL` | 없음 |
| `bbox_width` | `FLOAT` | `NOT NULL` | 없음 |
| `bbox_height` | `FLOAT` | `NOT NULL` | 없음 |
| `priority` | `INTEGER` | `NOT NULL` | 없음 |
| `detected_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` |

### `comments`

| 컬럼 | 타입 | Nullability | 기본값 |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 |
| `event_id` | `INTEGER` | `NOT NULL` | 없음 |
| `user_id` | `INTEGER` | `NOT NULL` | 없음 |
| `content` | `VARCHAR(500)` | `NOT NULL` | 없음 |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` |

## 5. 핵심 제약 조건

| 항목 | 제약 |
| --- | --- |
| User role | `ADMIN`, `OPERATOR`만 허용 |
| Equipment type | `CCTV`, `DRONE`만 허용 |
| Equipment status | `ACTIVE`, `INACTIVE`, `MAINTENANCE`만 허용 |
| Event confidence | `0.0 <= confidence <= 1.0` |
| Event latitude | `-90.0 <= latitude <= 90.0` |
| Event longitude | `-180.0 <= longitude <= 180.0` |
| Event status | `UNCHECKED`, `CHECKING`, `COMPLETED`, `MISIDENTIFIED`만 허용 |
| Event bbox | `bbox_x`, `bbox_y`는 0 이상, `bbox_width`, `bbox_height`는 0 초과 |
| Event priority | 1 이상의 정수 |
| Comment content | 공백 문자열 금지 |

## 6. 최종 인덱스 전략

| 인덱스 | 목적 |
| --- | --- |
| `idx_events_detected_at` | 최신 이벤트 목록 조회 |
| `idx_events_status` | 상태별 조회 |
| `idx_events_equipment_id` | 장비별 이벤트 조회 및 FK 조회 |
| `idx_events_user_id` | 관제사별 이벤트 조회 및 FK 조회 |
| `idx_events_priority` | 우선순위 조회/정렬 가능성 대비 |
| `idx_events_status_detected_at` | 미처리 이벤트 최신순 조회 |
| `idx_comments_event_id` | 이벤트별 코멘트 조회 |
| `idx_comments_user_id` | 사용자별 코멘트 조회 |
| `idx_comments_event_created_at` | 이벤트별 코멘트 시간순 조회 |
| `idx_equipment_type` | 장비 종류별 조회 |
| `idx_equipment_status` | 장비 상태별 조회 |

## 7. 최종 DDL

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

## 8. 후속 구현 주의사항

| 항목 | 주의사항 |
| --- | --- |
| 기존 DB | 현재 `events` 테이블이 이미 존재할 수 있으므로 구현 전 볼륨 초기화 또는 마이그레이션 전략이 필요하다. |
| 모델 정합성 | SQLAlchemy 모델은 이 DB 설계와 컬럼명/Nullability/FK/Check 제약을 일치시켜야 한다. |
| 테스트 데이터 | 이벤트 생성 전 `equipment` 기준 데이터가 필요하다. |
| nullable user_id | 최초 AI 이벤트 생성 시 `user_id`는 `NULL`로 저장 가능해야 한다. |
| bbox/priority | 세부 값 체계는 후속 AI/프론트 협의 결과에 따라 제약이 강화될 수 있다. |

## 9. 최종 결론

최종 DB 설계는 `users`, `equipment`, `events`, `comments` 4개 테이블로 구성한다.

MVP 핵심 테이블은 `events`이며, 위도/경도는 `FLOAT NOT NULL`, `user_id`는 nullable FK, `equipment_id`는 NOT NULL FK로 설계한다.

인덱스는 최신 이벤트 목록, 상태별 미처리 이벤트 조회, 이벤트별 코멘트 조회를 중심으로 설계한다.
