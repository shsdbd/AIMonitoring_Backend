# Step 3. 참조 무결성 및 무결성 제약 조건 설계

## 1. 설계 기준

이 단계에서는 Primary Key, Foreign Key, Unique, Check 제약 조건과 FK 삭제 정책을 정의한다.

모든 관계는 비식별 관계이며, 각 테이블은 독립적인 `id` PK를 가진다.

## 2. Primary Key

| 테이블 | PK |
| --- | --- |
| `users` | `id` |
| `equipment` | `id` |
| `events` | `id` |
| `comments` | `id` |

## 3. Foreign Key

| FK | 참조 | Nullability | 삭제 정책 | 이유 |
| --- | --- | --- | --- | --- |
| `events.equipment_id` | `equipment.id` | `NOT NULL` | `ON DELETE RESTRICT` | 이벤트는 탐지 장비 이력을 보존해야 하므로 장비 삭제를 제한한다. |
| `events.user_id` | `users.id` | `NULL` | `ON DELETE SET NULL` | 관제사 계정 삭제 시 이벤트 이력은 남기고 담당자만 비운다. |
| `comments.event_id` | `events.id` | `NOT NULL` | `ON DELETE CASCADE` | 이벤트가 삭제되면 해당 처리 기록도 함께 삭제한다. |
| `comments.user_id` | `users.id` | `NOT NULL` | `ON DELETE RESTRICT` | 작성자 추적을 위해 코멘트가 있는 사용자는 삭제를 제한한다. |

## 4. Unique 제약 조건

| 테이블 | 제약 | 이유 |
| --- | --- | --- |
| `users` | `username` unique | 사용자 이름 중복으로 인한 식별 혼선을 방지한다. |

MVP에서는 `equipment.location_name`이나 `image_url`에는 unique를 걸지 않는다.

## 5. Check 제약 조건

### `users`

| 제약 | 조건 |
| --- | --- |
| `ck_users_role` | `role IN ('ADMIN', 'OPERATOR')` |

### `equipment`

| 제약 | 조건 |
| --- | --- |
| `ck_equipment_type` | `equipment_type IN ('CCTV', 'DRONE')` |
| `ck_equipment_status` | `status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')` |

### `events`

| 제약 | 조건 |
| --- | --- |
| `ck_events_confidence` | `confidence >= 0.0 AND confidence <= 1.0` |
| `ck_events_latitude` | `latitude >= -90.0 AND latitude <= 90.0` |
| `ck_events_longitude` | `longitude >= -180.0 AND longitude <= 180.0` |
| `ck_events_status` | `status IN ('UNCHECKED', 'CHECKING', 'COMPLETED', 'MISIDENTIFIED')` |
| `ck_events_bbox_x` | `bbox_x >= 0.0` |
| `ck_events_bbox_y` | `bbox_y >= 0.0` |
| `ck_events_bbox_width` | `bbox_width > 0.0` |
| `ck_events_bbox_height` | `bbox_height > 0.0` |
| `ck_events_priority` | `priority >= 1` |

### `comments`

| 제약 | 조건 |
| --- | --- |
| `ck_comments_content_not_blank` | `LENGTH(BTRIM(content)) > 0` |

## 6. Enum 값을 Check로 관리하는 이유

MVP에서는 PostgreSQL enum type 대신 `VARCHAR` + `CHECK` 제약을 사용한다.

| 이유 | 설명 |
| --- | --- |
| 변경 용이성 | enum type보다 값 추가/변경이 상대적으로 단순하다. |
| SQLAlchemy 연동 단순성 | Pydantic/SQLAlchemy 문자열 enum과 맞추기 쉽다. |
| 졸업 작품 범위 적합성 | 명확한 제약을 유지하면서 과도한 DB 타입 고도화를 피한다. |

## 7. 미결정 사항을 고려한 제약 설계

| 미결정 항목 | 이번 설계의 처리 |
| --- | --- |
| bbox 좌표 기준 | 픽셀/정규화 모두 수용 가능하도록 음수 금지와 크기 양수만 강제한다. |
| priority 값 체계 | 구체 등급은 미정이므로 `priority >= 1`만 강제한다. |
| image_url 의미 | 이미지 파일 경로/영상 참조 모두 수용하도록 문자열 참조로 둔다. |
| 정보 부족 이벤트 처리 | 필수 컬럼 `NOT NULL`과 CHECK로 정상 이벤트의 최소 품질을 보장한다. |

## 8. Step 3 결론

참조 무결성은 이벤트 이력 보존을 우선한다.

장비 삭제는 제한하고, 관제사 삭제 시 이벤트의 `user_id`는 `NULL`로 설정한다. 이벤트 삭제 시 연결된 코멘트는 함께 삭제한다.

상태값, 좌표, 신뢰도, bbox, priority는 DB 레벨 Check 제약으로 최소 데이터 품질을 보장한다.
