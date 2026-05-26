# Step 1. 도메인 및 아키텍처 검토

## 1. 검토 목적

이 단계는 확정된 도메인 모델과 아키텍처 계획을 바탕으로 PostgreSQL 물리 DB 설계의 기준을 재확인한다.

이 문서는 DB 설계의 입력 검토이며, Python/SQLAlchemy/FastAPI 구현은 다루지 않는다.

## 2. 입력 문서

| 문서 | 역할 |
| --- | --- |
| `docs/domain/04_domain_modeling_06.md` | 최종 도메인 엔티티, 속성, 관계 기준 |
| `docs/architecture/05_architecture_planning_06.md` | 계층 구조와 모듈 책임 기준 |
| `docs/mvp/03_mvp_scope_planning_06.md` | MVP 포함/제외 범위 기준 |
| `docs/decisions/DECISIONS.md` | 확정 결정 기준 |
| `.agent/skills/context_packet.md` | 최신 맥락 요약 |

## 3. 최종 엔티티 재확인

| 엔티티 | 물리 테이블명 | MVP 역할 |
| --- | --- | --- |
| User | `users` | 관제사 또는 시스템 사용자 식별 |
| Equipment | `equipment` | CCTV/드론 등 탐지 장비 식별 |
| Event | `events` | AI가 탐지한 도로 장애물 이벤트 저장 |
| Comment | `comments` | 관제사의 처리 기록 또는 확인 메모 저장 |

## 4. 최종 관계 재확인

| 관계 | 물리 FK | Nullability | 설명 |
| --- | --- | --- | --- |
| User -> Event | `events.user_id -> users.id` | `NULL` 허용 | 최초 AI 탐지 시 관제사가 미배정될 수 있다. |
| Equipment -> Event | `events.equipment_id -> equipment.id` | `NOT NULL` | 이벤트는 탐지 장비를 반드시 가져야 한다. |
| User -> Comment | `comments.user_id -> users.id` | `NOT NULL` | 코멘트 작성자를 추적해야 한다. |
| Event -> Comment | `comments.event_id -> events.id` | `NOT NULL` | 코멘트는 반드시 특정 이벤트에 연결된다. |

## 5. MVP 제외 범위 재확인

다음 항목은 물리 테이블로 만들지 않는다.

| 제외 항목 | 이유 |
| --- | --- |
| `detections` | 다중 객체 탐지는 MVP 제외 범위다. |
| `event_status_history` | 별도 상태 이력 테이블은 MVP 제외 범위다. |
| `equipment_locations` | Equipment 자체 지도 좌표 관리는 MVP 제외 범위다. |
| `roles`, `permissions`, `user_roles` | 복잡한 권한 모델은 MVP 제외 범위다. |
| 통계/분석 테이블 | 고도화된 대시보드와 분석은 MVP 제외 범위다. |

## 6. 물리 설계에서 확정할 항목

| 항목 | 설계 방향 |
| --- | --- |
| 장비 종류 컬럼명 | `equipment.equipment_type`으로 통일한다. 기존 ERD의 `type`보다 의미가 명확하고 예약어 혼선을 줄인다. |
| 위도/경도 타입 | `FLOAT` 필수값으로 설계한다. |
| Event user_id | `NULL` 허용 FK로 설계한다. |
| bbox | `events` 테이블의 단일 이벤트 속성으로 둔다. 별도 Detection 테이블은 만들지 않는다. |
| priority | `INTEGER`로 설계하되 구체 등급 체계는 후속 협의 여지를 남긴다. |
| image_url | MVP에서는 탐지 근거 참조값으로 `VARCHAR(255)`를 사용한다. |

## 7. 현재 코드와의 주요 차이

| 현재 코드 | DB 설계 기준 |
| --- | --- |
| `Event` 모델만 존재 | `users`, `equipment`, `events`, `comments` 4개 테이블 설계 |
| `events.equipment_type`이 직접 있음 | 장비 종류는 `equipment.equipment_type`에서 관리 |
| `events.equipment_id`가 문자열 | `equipment.id`를 참조하는 정수 FK |
| `events.user_id`가 모델에 없음 | `events.user_id`는 `users.id`를 참조하는 nullable FK |
| bbox/priority 없음 | MVP 요구사항에 따라 `events`에 포함 |

## 8. Step 1 결론

물리 DB 설계는 `users`, `equipment`, `events`, `comments` 4개 테이블을 기준으로 한다.

MVP 핵심 흐름은 `equipment -> events`와 `users -> events` 관계를 중심으로 구성하고, 처리 기록을 포함할 경우 `comments`가 `users`와 `events`를 연결한다.

이후 단계에서는 이 구조를 PostgreSQL 컬럼, 제약 조건, 인덱스, DDL로 구체화한다.
