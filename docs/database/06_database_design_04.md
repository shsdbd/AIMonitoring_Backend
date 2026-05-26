# Step 4. 인덱스 설계 및 성능 최적화

## 1. 설계 기준

인덱스는 MVP의 조회 흐름을 기준으로 설계한다.

MVP 핵심 조회는 이벤트 목록 최신순 조회, 상태별 미처리 이벤트 조회, 장비별 이벤트 조회, 이벤트별 코멘트 조회다.

## 2. 기본 인덱스

PostgreSQL은 Primary Key와 Unique 제약 조건에 대해 자동으로 인덱스를 생성한다.

| 테이블 | 자동 인덱스 |
| --- | --- |
| `users` | `users_pkey`, `users_username_key` |
| `equipment` | `equipment_pkey` |
| `events` | `events_pkey` |
| `comments` | `comments_pkey` |

## 3. `events` 인덱스

| 인덱스명 | 컬럼 | 목적 |
| --- | --- | --- |
| `idx_events_detected_at` | `detected_at DESC` | 최신 이벤트 목록 조회 최적화 |
| `idx_events_status` | `status` | 미확인/확인 중/완료/오탐 상태별 조회 최적화 |
| `idx_events_equipment_id` | `equipment_id` | 장비별 이벤트 조회 및 FK 조회 최적화 |
| `idx_events_user_id` | `user_id` | 관제사 담당 이벤트 조회 및 FK 조회 최적화 |
| `idx_events_priority` | `priority` | 우선순위 기반 정렬/필터링 가능성 대비 |
| `idx_events_status_detected_at` | `(status, detected_at DESC)` | 미처리 이벤트 최신순 조회 최적화 |

## 4. `comments` 인덱스

| 인덱스명 | 컬럼 | 목적 |
| --- | --- | --- |
| `idx_comments_event_id` | `event_id` | 이벤트 상세에서 코멘트 목록 조회 |
| `idx_comments_user_id` | `user_id` | 사용자별 작성 기록 조회 가능성 대비 |
| `idx_comments_event_created_at` | `(event_id, created_at ASC)` | 이벤트별 코멘트 시간순 조회 |

## 5. `equipment` 인덱스

| 인덱스명 | 컬럼 | 목적 |
| --- | --- | --- |
| `idx_equipment_type` | `equipment_type` | 장비 종류별 조회 가능성 대비 |
| `idx_equipment_status` | `status` | 활성/비활성 장비 조회 가능성 대비 |

## 6. 인덱스 제외 항목

| 컬럼 | 제외 이유 |
| --- | --- |
| `events.latitude`, `events.longitude` | MVP에서는 공간 검색을 하지 않고 단순 표시만 한다. PostGIS/공간 인덱스는 과하다. |
| `events.image_url` | URL로 검색하는 요구사항이 없다. |
| `events.bbox_*` | bbox는 화면 표시용이며 검색 조건이 아니다. |
| `comments.content` | 전문 검색 요구사항이 없다. |

## 7. 성능 설계 원칙

| 원칙 | 설명 |
| --- | --- |
| 목록 조회 우선 | 관제 화면은 최신 이벤트와 미처리 이벤트 확인이 핵심이다. |
| FK 조회 보조 | FK 컬럼은 조인과 참조 조회가 잦으므로 인덱스를 둔다. |
| 과도한 인덱스 금지 | MVP에서 검색하지 않는 컬럼에는 인덱스를 만들지 않는다. |
| 공간 인덱스 보류 | 위치는 지도 표시용이며 반경 검색/공간 검색 요구가 확정되지 않았다. |

## 8. Step 4 결론

인덱스는 `events`의 최신순/상태별 조회와 `comments`의 이벤트별 조회에 집중한다.

위경도는 MVP에서 검색 조건이 아니라 표시 데이터이므로 일반 인덱스나 공간 인덱스를 만들지 않는다.
