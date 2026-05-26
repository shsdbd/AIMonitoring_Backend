# Step 2. 엔티티 핵심 속성 정의

## 1. 속성 정의 기준

이 단계에서는 각 엔티티가 가져야 할 논리적 속성과 식별자를 정의한다.

물리 DB 타입, DDL, 인덱스, API 요청/응답 형식은 정의하지 않는다. 속성 타입은 개념 이해를 돕기 위한 논리 타입으로만 표현한다.

## 2. User 엔티티

| 속성 | 논리 타입 | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| id | Identifier | 필수 | User의 고유 식별자 |
| username | Text | 필수 | 관제사 또는 사용자의 표시/로그인 이름 |
| role | Enum/Text | 필수 | 사용자 역할. 예: 관제사, 관리자 |
| created_at | DateTime | 필수 | 사용자가 등록된 시각 |

### User 설명

`User`는 도로 관제사를 표현하는 엔티티다. MVP에서는 단일 관제사 가정으로 단순화할 수 있지만, 이벤트 배정자나 코멘트 작성자를 추적하려면 유지해야 하는 도메인이다.

## 3. Equipment 엔티티

| 속성 | 논리 타입 | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| id | Identifier | 필수 | Equipment의 고유 식별자 |
| equipment_type | Enum/Text | 필수 | 장비 종류. 예: CCTV, DRONE |
| location_name | Text | 필수 | 장비 설치 또는 운용 거점 이름 |
| status | Enum/Text | 필수 | 장비 상태. 예: 활성, 비활성, 점검 중 |

### Equipment 설명

`Equipment`는 AI 탐지 결과를 발생시키는 CCTV 또는 드론 장비를 표현한다. MVP에서는 장비 관리 기능을 고도화하지 않지만, 이벤트가 어떤 장비에서 발생했는지 식별하기 위해 도메인으로 유지한다.

`Equipment` 자체 지도 좌표는 MVP 제외 범위이므로 속성에 포함하지 않는다.

## 4. Event 엔티티

| 속성 | 논리 타입 | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| id | Identifier | 필수 | Event의 고유 식별자 |
| equipment_id | Reference | 필수 | 이벤트를 탐지한 Equipment 참조 |
| user_id | Reference | 선택 | 이벤트를 확인하거나 담당한 User 참조. 최초 탐지 시 비어 있을 수 있다. |
| obstacle_type | Enum/Text | 필수 | 장애물 종류. MVP 우선 대상은 동물 사체 |
| confidence | Decimal Number | 필수 | AI 탐지 신뢰도 |
| latitude | Decimal Number | 필수 | 장애물 발생 위치의 위도 |
| longitude | Decimal Number | 필수 | 장애물 발생 위치의 경도 |
| status | Enum/Text | 필수 | 이벤트 처리 상태 |
| image_url | Text | 필수 | 탐지 근거 이미지 또는 영상 참조 정보 |
| bbox_x | Decimal Number | 필수 | 장애물 강조 박스 x 좌표 |
| bbox_y | Decimal Number | 필수 | 장애물 강조 박스 y 좌표 |
| bbox_width | Decimal Number | 필수 | 장애물 강조 박스 너비 |
| bbox_height | Decimal Number | 필수 | 장애물 강조 박스 높이 |
| priority | Number/Enum | 필수 | 이벤트 처리 우선순위 |
| detected_at | DateTime | 필수 | AI가 장애물을 탐지한 시각 또는 이벤트 등록 시각 |

### Event 설명

`Event`는 MVP의 중심 엔티티다. AI가 탐지한 도로 장애물 정보를 관제사가 확인하고 처리할 수 있는 단위로 표현한다.

`Event`는 위치, 신뢰도, 탐지 근거, bbox, priority, 상태 정보를 포함해야 한다.

## 5. Comment 엔티티

| 속성 | 논리 타입 | 필수 여부 | 설명 |
| --- | --- | --- | --- |
| id | Identifier | 필수 | Comment의 고유 식별자 |
| event_id | Reference | 필수 | 코멘트가 연결된 Event 참조 |
| user_id | Reference | 필수 | 코멘트를 작성한 User 참조 |
| content | Text | 필수 | 처리 기록, 확인 메모, 오탐 사유 등 |
| created_at | DateTime | 필수 | 코멘트 작성 시각 |

### Comment 설명

`Comment`는 관제사가 이벤트에 남기는 처리 기록 또는 확인 메모다.

MVP에서는 조건부 포함 기능이지만, 요구사항과 ERD에 포함된 핵심 도메인이므로 논리 모델에는 포함한다.

## 6. MVP 제외 속성

| 제외 속성/엔티티 | 제외 이유 |
| --- | --- |
| Detection 관련 속성 | 다중 객체 탐지는 MVP 제외다. |
| EventStatusHistory 관련 속성 | 별도 상태 이력 테이블은 MVP 제외다. |
| Equipment latitude/longitude | Equipment 자체 지도 좌표 관리는 MVP 제외다. |
| 복잡한 권한/권한 그룹 속성 | 복잡한 역할/권한 관리는 MVP 제외다. |

## 7. Step 2 결론

논리 도메인 모델은 네 개의 엔티티와 각 엔티티의 식별자를 중심으로 구성한다.

MVP 중심 속성은 `Event`의 위치, 탐지 근거, bbox, priority, status이며, `User`, `Equipment`, `Comment`는 이벤트 관제 흐름을 보조하는 참조 도메인으로 둔다.
