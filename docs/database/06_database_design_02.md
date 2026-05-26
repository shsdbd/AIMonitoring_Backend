# Step 2. 물리 테이블 및 컬럼 상세 스펙 설계

## 1. 설계 기준

PostgreSQL 기준의 물리 테이블, 컬럼명, 데이터 타입, Nullability, 기본값을 정의한다.

이 문서는 DB 설계 문서이며, SQLAlchemy 모델 구현은 포함하지 않는다.

## 2. `users` 테이블

| 컬럼명 | PostgreSQL 타입 | Nullability | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 | 사용자 PK |
| `username` | `VARCHAR(50)` | `NOT NULL` | 없음 | 관제사/사용자 이름 |
| `role` | `VARCHAR(20)` | `NOT NULL` | `'OPERATOR'` | 사용자 역할 |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 사용자 생성 시각 |

## 3. `equipment` 테이블

| 컬럼명 | PostgreSQL 타입 | Nullability | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 | 장비 PK |
| `equipment_type` | `VARCHAR(20)` | `NOT NULL` | 없음 | 장비 종류. 예: CCTV, DRONE |
| `location_name` | `VARCHAR(100)` | `NOT NULL` | 없음 | 장비 설치 또는 운용 거점 이름 |
| `status` | `VARCHAR(20)` | `NOT NULL` | `'ACTIVE'` | 장비 상태 |

## 4. `events` 테이블

| 컬럼명 | PostgreSQL 타입 | Nullability | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 | 이벤트 PK |
| `equipment_id` | `INTEGER` | `NOT NULL` | 없음 | 탐지 장비 FK |
| `user_id` | `INTEGER` | `NULL` | `NULL` | 관제 담당자/확인자 FK |
| `obstacle_type` | `VARCHAR(50)` | `NOT NULL` | 없음 | 장애물 종류 |
| `confidence` | `FLOAT` | `NOT NULL` | 없음 | AI 탐지 신뢰도 |
| `latitude` | `FLOAT` | `NOT NULL` | 없음 | 장애물 위도 |
| `longitude` | `FLOAT` | `NOT NULL` | 없음 | 장애물 경도 |
| `status` | `VARCHAR(20)` | `NOT NULL` | `'UNCHECKED'` | 이벤트 처리 상태 |
| `image_url` | `VARCHAR(255)` | `NOT NULL` | 없음 | 탐지 근거 이미지 또는 영상 참조 |
| `bbox_x` | `FLOAT` | `NOT NULL` | 없음 | 장애물 강조 박스 x 좌표 |
| `bbox_y` | `FLOAT` | `NOT NULL` | 없음 | 장애물 강조 박스 y 좌표 |
| `bbox_width` | `FLOAT` | `NOT NULL` | 없음 | 장애물 강조 박스 너비 |
| `bbox_height` | `FLOAT` | `NOT NULL` | 없음 | 장애물 강조 박스 높이 |
| `priority` | `INTEGER` | `NOT NULL` | 없음 | 이벤트 처리 우선순위 |
| `detected_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 탐지 또는 등록 시각 |

## 5. `comments` 테이블

| 컬럼명 | PostgreSQL 타입 | Nullability | 기본값 | 설명 |
| --- | --- | --- | --- | --- |
| `id` | `SERIAL` | `NOT NULL` | 자동 증가 | 코멘트 PK |
| `event_id` | `INTEGER` | `NOT NULL` | 없음 | 연결된 이벤트 FK |
| `user_id` | `INTEGER` | `NOT NULL` | 없음 | 작성자 FK |
| `content` | `VARCHAR(500)` | `NOT NULL` | 없음 | 처리 기록 또는 메모 |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL` | `NOW()` | 작성 시각 |

## 6. 타입 선택 근거

| 타입 | 사용 위치 | 이유 |
| --- | --- | --- |
| `SERIAL` | 모든 PK | 학부 프로젝트와 MVP 수준에서 단순하고 명확한 자동 증가 식별자 |
| `VARCHAR(n)` | 이름, 상태, URL, 내용 | 값 길이를 제한해 데이터 품질 유지 |
| `FLOAT` | 위도/경도, 신뢰도, bbox | DECISIONS의 위경도 `FLOAT` 결정 준수 및 bbox 소수 표현 가능 |
| `INTEGER` | FK, priority | 참조 식별자와 우선순위 표현 |
| `TIMESTAMPTZ` | 생성/탐지 시각 | 타임존 포함 시각 저장 |

## 7. Step 2 결론

물리 테이블은 `users`, `equipment`, `events`, `comments` 네 개로 설계한다.

`events`는 MVP 핵심 데이터를 모두 포함하며, `latitude`, `longitude`, `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`는 모두 `FLOAT`로 설계한다.

`equipment_type`은 `equipment` 테이블의 장비 종류 컬럼명으로 확정한다.
