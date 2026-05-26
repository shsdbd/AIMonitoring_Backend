# 01_DECISIONS (확정된 결정 사항)

이 문서는 AI 기반 도로 관제 시스템 개발 과정에서 합의된 기술 아키텍처, 데이터베이스 구조, 비즈니스 로직 정책 등의 확정 사항을 기록합니다. 여기에 기록된 사항은 상위 설계가 변경되지 않는 한 모든 구현 코드의 기준이 됩니다.

## 1. 기술 스택 및 인프라 (Tech Stack & Infrastructure)
- **백엔드 프레임워크:** Python 기반 FastAPI를 사용하여 비동기 REST API를 구축한다.
- **데이터베이스:** 관계형 데이터베이스로 PostgreSQL을 채택한다.
- **ORM & 데이터 검증:** 데이터베이스 매핑은 SQLAlchemy를 사용하고, API 요청/응답 검증은 Pydantic v2를 사용한다.
- **컨테이너 인프라:** 개발 및 배포 환경의 일관성을 위해 FastAPI와 PostgreSQL을 Docker 및 Docker Compose 환경으로 묶어 관리한다.

## 2. 서비스 목표 정의 단계 결정
- **핵심 탐지 대상:** MVP의 우선 탐지 대상은 도로 위 **동물 사체**로 정의한다.
- **핵심 사용자:** 1차 사용자는 **도로 관제사**로 정의한다.
- **핵심 문제:** 기존 도로 장애물 발견은 사람이 직접 순찰하거나 CCTV 영상을 감시하는 방식에 의존하므로 발견이 늦어질 수 있다.
- **백엔드 핵심 가치:** 백엔드는 AI 모델과 프론트엔드 사이에서 탐지 데이터를 안정적으로 전달하는 것을 최우선 가치로 두고, 빠른 데이터 처리를 2순위 가치로 둔다.
- **완성 장면:** AI가 도로 장애물을 감지하면 백엔드 데이터 처리를 거쳐 프론트 화면에 관제사 알림이 뜨고, 관제사는 실시간 영상과 장애물 강조 표시 화면을 통해 상황을 확인한다.

## 3. 요구사항 분해 단계 결정
- **요구사항 중심 시나리오:** 요구사항은 단순 기능 목록이 아니라 **도로 관제사가 AI 탐지 이벤트를 인지, 확인, 판단, 처리, 종결하는 업무 흐름**을 중심으로 정의한다.
- **대표 관제사 흐름:** AI가 동물 사체를 탐지하면 백엔드가 이벤트로 등록하고, 관제사는 신규 이벤트를 확인한 뒤 위치, 신뢰도, 탐지 근거 화면, 장애물 강조 박스를 보고 상태를 변경한다.
- **핵심 유스케이스:** AI 탐지 이벤트 등록, 신규 이벤트 인지, 이벤트 목록 확인, 이벤트 상세 확인, 장애물 강조 영역 확인, 이벤트 상태 변경, 처리 기록 작성, 오탐 이벤트 구분을 요구사항 기준 유스케이스로 둔다.
- **MVP Must-have:** AI 탐지 결과 수신, 신규 이벤트 등록, 이벤트 목록/상세 확인, 위치 정보 제공, 탐지 근거 이미지 또는 영상 참조 제공, bbox 기반 강조 표시 데이터 제공, priority 제공, 이벤트 상태 변경, 오탐 이벤트 구분, 상태 변경 결과 저장 및 재조회를 MVP 필수 요구사항으로 둔다.
- **MVP Should-have:** 관제사 처리 기록 작성/조회, 관제사 식별 정보 관리, 장비 식별 정보 관리, 관제사 권한 통제, AI 요청 신뢰성 확인은 중요하지만 구현 일정에 따라 단계화할 수 있다.
- **MVP 제외:** AI 모델 학습 및 추론 로직, 프론트엔드 화면 디자인 세부 구현, 대규모 분산 처리 인프라, 완전한 고가용성 구성, 다중 객체 탐지를 위한 별도 Detection 도메인, 별도 EventStatusHistory 이력 테이블, Equipment 자체 지도 좌표 관리는 이번 MVP에서 제외한다.
- **최종 요구사항 명세서:** 요구사항 분해 최종 산출물은 `docs/requirements/02_requirements_decomposition_11.md`를 기준으로 한다.

## 4. MVP 범위 계획 단계 결정
- **MVP 핵심 목표:** AI가 탐지한 도로 위 동물 사체 이벤트가 백엔드를 통해 관제사 화면에 전달되고, 관제사가 위치와 탐지 근거를 확인한 뒤 이벤트 상태를 관리할 수 있어야 한다.
- **MVP Critical Path:** AI 탐지 결과 발생 -> 백엔드 이벤트 등록 -> 프론트엔드 신규 이벤트 표시 -> 관제사 목록/상세 확인 -> 위치, 신뢰도, 탐지 근거, bbox 강조 정보, priority 확인 -> 상태 변경 -> 최신 상태 저장 및 재조회.
- **MVP 포함 범위:** AI 탐지 결과 수신, 신규 이벤트 등록, 이벤트 목록 제공, 이벤트 상세 제공, 위치 정보 제공, 탐지 근거 제공, bbox 정보 제공, priority 제공, 이벤트 상태 변경, 오탐 구분, 최신 상태 재조회, 필수 정보 검증을 포함한다.
- **MVP 조건부 포함 범위:** 처리 기록/코멘트 작성 및 조회, 관제사 식별 정보 관리, 장비 식별 정보 관리, 단순 접근 통제, AI 요청 신뢰성 확인은 Must-have 구현 안정화 이후 일정이 허용될 때 포함한다.
- **MVP 제외 범위:** AI 모델 학습 및 추론 로직, 프론트엔드 화면 디자인 세부 구현, 고도화된 통계/분석 대시보드, 대규모 분산 처리 인프라, 완전한 고가용성 구성, 다중 객체 Detection 도메인, 별도 EventStatusHistory 이력 테이블, Equipment 자체 지도 좌표 관리, 복잡한 역할/권한 관리, 관리자용 사용자/장비 관리 고도화는 이번 MVP에서 제외한다.
- **릴리스 마일스톤:** 1주차 이벤트 기본 흐름 복구, 2주차 관제사 확인 흐름 강화, 3주차 AI/프론트 연계 계약 확정 및 통합 검증, 4주차 MVP 시연 안정화 및 문서 정리 순서로 진행한다.
- **최종 MVP 범위 정의서:** MVP 범위 계획 최종 산출물은 `docs/mvp/03_mvp_scope_planning_06.md`를 기준으로 한다.

## 5. 도메인 모델링 단계 결정
- **최종 도메인 엔티티:** `User`, `Equipment`, `Event`, `Comment` 네 엔티티를 최종 도메인 모델로 정의한다.
- **중심 엔티티:** MVP의 중심 엔티티는 `Event`이며, AI가 탐지한 도로 장애물 이벤트를 관제사가 확인하고 처리하는 단위로 사용한다.
- **User 역할:** `User`는 도로 관제사 또는 시스템 사용자를 나타내며, 이벤트 담당자와 코멘트 작성자를 식별하는 데 사용한다.
- **Equipment 역할:** `Equipment`는 CCTV 또는 드론 등 탐지 장비를 나타내며, 이벤트 발생 장비를 식별하는 데 사용한다.
- **Comment 역할:** `Comment`는 관제사가 이벤트에 남기는 처리 기록, 확인 메모, 오탐 사유를 나타내며, MVP 조건부 포함 기능으로 둔다.
- **최종 관계:** `User -> Event`, `Equipment -> Event`, `User -> Comment`, `Event -> Comment` 네 관계만 정의한다.
- **Equipment 핵심 표시 속성:** 프론트 `cameraId` 응답을 위해 `camera_id`를 Equipment의 핵심 속성으로 둔다.
- **Event 핵심 속성:** `equipment_id`, `user_id`, `obstacle_type`, `species`, `confidence`, `latitude`, `longitude`, `status`, `image_url`, `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`, `priority`, `detected_at`, `repeat_detection`, `repeat_count`, `last_detected_at`을 Event의 핵심 논리 속성으로 둔다.
- **도메인 제외:** `Detection`, `EventStatusHistory`, `Equipment` 자체 지도 좌표, 복잡한 권한/권한 그룹 모델은 MVP 제외 범위에 따라 도메인 모델에 포함하지 않는다.
- **최종 도메인 모델 명세서:** 도메인 모델링 최종 산출물은 `docs/domain/04_domain_modeling_06.md`를 기준으로 한다.

## 6. 아키텍처 계획 단계 결정
- **목표 아키텍처:** FastAPI 백엔드는 `main.py`, `core/`, `dependencies/`, `models/`, `schemas/`, `routers/`, `services/`, `storage/`, `static/` 계층으로 분리한다.
- **main.py 책임:** FastAPI 앱 생성, CORS 미들웨어 등록, `/static` 마운트, 라우터 등록, startup 초기화만 담당하고 도메인 비즈니스 로직은 포함하지 않는다.
- **라우터 계층:** `routers/`는 HTTP 엔드포인트 선언과 요청/응답 연결만 담당한다.
- **서비스 계층:** `services/`는 이벤트 등록, 조회, 상태 변경 등 유스케이스와 비즈니스 흐름을 담당한다.
- **스토리지 계층:** `storage/image_storage.py`는 이미지 저장, 파일 형식 검증, 정적 URL 생성 책임을 가진다.
- **공통 의존성:** `dependencies/database.py`에서 요청 단위 DB 세션 dependency를 제공하고, 인증/AI 검증 dependency는 조건부 포함 범위에 맞춰 `dependencies/auth.py`에서 확장한다.
- **공통 예외 처리:** `core/errors.py`와 `core/exception_handlers.py`를 통해 공통 비즈니스 에러와 전역 예외 응답 구조를 둔다.
- **기존 자산 보존:** CORS 설정, `/static` 마운트, `static/images/{YYYY}/{MM}/{DD}/` 이미지 저장 정책, `DATABASE_URL` 기반 DB 연결은 보존한다.
- **모듈 경계:** `models`는 `schemas/routers/services`를 참조하지 않고, `schemas`는 `models`를 참조하지 않으며, `services`는 `routers`를 참조하지 않는다.
- **최종 아키텍처 정의서:** 아키텍처 계획 최종 산출물은 `docs/architecture/05_architecture_planning_06.md`를 기준으로 한다.

## 7. 데이터베이스 설계 단계 결정
- **최종 물리 테이블:** PostgreSQL 물리 테이블은 `users`, `equipment`, `events`, `comments` 네 개로 설계한다.
- **PK 정책:** 모든 테이블은 `SERIAL PRIMARY KEY` 형식의 독립 `id`를 가진다.
- **장비 종류 컬럼명:** 장비 종류 컬럼은 `equipment.equipment_type`으로 통일한다.
- **장비 표시 식별자:** 프론트 `cameraId` 응답을 위해 `equipment.camera_id`를 `VARCHAR(50) NOT NULL UNIQUE`로 둔다.
- **Event 핵심 FK:** `events.equipment_id`는 `equipment.id`를 참조하는 `NOT NULL` FK이고, `events.user_id`는 `users.id`를 참조하는 nullable FK다.
- **FK 삭제 정책:** `events.equipment_id`는 `ON DELETE RESTRICT`, `events.user_id`는 `ON DELETE SET NULL`, `comments.event_id`는 `ON DELETE CASCADE`, `comments.user_id`는 `ON DELETE RESTRICT`로 설계한다.
- **Event 좌표 타입:** `events.latitude`와 `events.longitude`는 `FLOAT NOT NULL`로 설계한다.
- **Event species 타입:** AI 모델이 탐지한 세부 종(`gorani`, `wild_boar`, `raccoon`)은 `events.species`에 저장하고, `events.obstacle_type`은 상위 유형인 `ANIMAL`로 저장한다.
- **Event bbox 타입:** `events.bbox_x`, `events.bbox_y`, `events.bbox_width`, `events.bbox_height`는 `FLOAT NOT NULL`로 설계하고, 프론트 계약에 따라 0~100 퍼센트 좌표/좌상단 기준으로 관리한다.
- **Event priority 타입:** `events.priority`는 `INTEGER NOT NULL`로 설계하고, 허용값은 `1`, `2`, `3`으로 둔다.
- **Event 반복 감지 필드:** `events.repeat_detection`은 `BOOLEAN NOT NULL DEFAULT FALSE`, `events.repeat_count`는 `INTEGER NOT NULL DEFAULT 0`, `events.last_detected_at`은 `TIMESTAMPTZ NOT NULL DEFAULT NOW()`로 둔다.
- **Event 상태값:** 프론트 관제 흐름에 맞춰 `UNCHECKED`, `CHECKING`, `DISPATCH_REQUESTED`, `DISPATCHING`, `COMPLETED`, `MISIDENTIFIED` 6개를 허용한다.
- **주요 인덱스:** 최신 이벤트 목록, 상태별 이벤트 조회, 장비/사용자별 이벤트 조회, 이벤트별 코멘트 조회를 위해 `events.detected_at`, `events.status`, `events.equipment_id`, `events.user_id`, `events.priority`, `(events.status, events.detected_at)`, `comments.event_id`, `comments.user_id`, `(comments.event_id, comments.created_at)`에 인덱스를 둔다.
- **공간 인덱스 제외:** MVP에서는 위도/경도를 검색 조건이 아닌 지도 표시 데이터로 사용하므로 PostGIS 또는 공간 인덱스는 도입하지 않는다.
- **최종 데이터베이스 설계서:** 데이터베이스 설계 최종 산출물은 `docs/database/06_database_design_06.md`를 기준으로 한다.

## 8. 작업 분해 단계 결정
- **최종 구현 순서:** DB/Model 정합성 -> Schema 정리 -> 공통 인프라 분리 -> Event service/router 구현 -> 검증 순서로 진행한다.
- **Must-have 구현 중심:** Event 생성, 목록 조회, 상세 조회, 상태 변경, 이미지 저장, DB 저장/재조회 검증을 최우선 구현 범위로 둔다.
- **첫 번째 구현 티켓:** 기존 개발 DB와 새 설계 충돌을 피하기 위해 개발 DB 초기화 또는 마이그레이션 전략을 먼저 확정한다.
- **핵심 모델 티켓:** `User`, `Equipment`, `Event`, `Comment` 모델을 최종 DB 설계에 맞춰 작성/수정한다.
- **핵심 API 티켓:** Event 스키마, Event service, Event router, 공통 DB dependency, 이미지 저장 모듈, 공통 에러 처리를 구현 티켓으로 둔다.
- **검증 티켓:** Swagger 검증, curl 통합 검증, PostgreSQL 직접 확인을 별도 티켓으로 둔다.
- **조건부 티켓:** Comment 작성/조회 API, 단순 AI 요청 검증 dependency, 단순 관제사 접근 통제는 Must-have 흐름 안정화 이후 포함 여부를 결정한다.
- **제외 티켓:** AI 모델 학습, 프론트 디자인, 통계/분석 대시보드, 대규모 분산 처리/고가용성, 다중 객체 Detection 테이블, EventStatusHistory, Equipment 자체 좌표, 복잡한 권한 관리, 관리자용 사용자/장비 관리 고도화는 티켓으로 만들지 않는다. 단, 전달받은 `ai_model`의 추론 코드와 `best.pt`를 FastAPI 내부 모듈로 통합하는 작업은 백엔드 구현 범위에 포함할 수 있다.
- **최종 작업 백로그:** 작업 분해 최종 산출물은 `docs/tasks/07_task_breakdown_06.md`를 기준으로 한다.

## 9. 구현 지시서 작성 단계 결정
- **첫 구현 지시서 대상:** `T-02`~`T-07`을 묶어 “DB/Model 정합성 1차 구현” 지시서로 작성한다.
- **묶음 처리 이유:** `Event`가 `User`, `Equipment`를 참조하고 `Comment`가 `User`, `Event`를 참조하므로 모델 계층은 FK 관계상 함께 정리하는 것이 안전하다.
- **구현 지시 범위:** `models/user.py`, `models/equipment.py`, `models/comment.py` 생성, `models/event.py`, `models/__init__.py`, `database.py` 수정만 포함한다.
- **구현 제외 범위:** `main.py`, `schemas/`, `routers/`, `services/`, `storage/`, `docker-compose.yml` 수정은 첫 구현 지시서에서 제외한다.
- **검증 기준:** `python -m compileall database.py models` 성공 및 SQLAlchemy metadata에 `users`, `equipment`, `events`, `comments` 테이블 포함을 완료 기준으로 둔다.
- **최종 개발 지시서:** 첫 구현 프롬프트 최종 산출물은 `docs/implementation/08_implementation_prompt_writer_05.md`를 기준으로 한다.

## 10. 프론트엔드 API 계약 결정
- **프론트 응답 기준:** 프론트엔드는 기존 `RoadkillEvent` 타입을 유지하고, 백엔드는 API 응답 DTO에서 내부 DB 값을 프론트 타입에 맞게 가공해 내려준다.
- **API prefix:** 공식 프론트 연동 API prefix는 `/api`로 정한다. 기존 `/api/v1` 경로는 초기 프로토타입 산물이며, 필요하면 개발 기간 동안 호환 라우트로 유지할 수 있다.
- **이벤트 목록 API:** 이벤트 목록 조회 공식 경로는 `GET /api/events`로 정한다.
- **이벤트 상세 API:** 이벤트 상세 조회 공식 경로는 `GET /api/events/{eventId}`로 정한다.
- **상태 변경 API:** 이벤트 상태 변경 공식 경로는 `PATCH /api/events/{eventId}/status`로 정한다.
- **AI 탐지 이벤트 생성 API:** AI 탐지 이벤트 생성 공식 경로는 `POST /api/events/detect`로 정한다. 요청은 `multipart/form-data`로 받으며 `cameraId`, `latitude`, `longitude`, 선택 `locationName`, `image`를 사용한다.
- **장비 자동 생성 정책:** `POST /api/events/detect`에서 `cameraId`에 해당하는 장비가 없으면 백엔드가 `Equipment`를 자동 생성한다. 기본 `equipment_type`은 `CCTV`, `status`는 `ACTIVE`, `location_name`은 요청의 `locationName` 또는 `미지정 위치`로 저장한다.
- **상태 변경 body:** 상태 변경 요청 body는 `{ status, comment? }` 형태로 정한다. `comment`는 선택값이며, 값이 있으면 처리 기록으로 저장하는 방향을 기본으로 한다.
- **상태 enum:** 백엔드 내부 상태값은 `UNCHECKED`, `CHECKING`, `DISPATCH_REQUESTED`, `DISPATCHING`, `COMPLETED`, `MISIDENTIFIED` 6개로 정한다. 프론트 `RoadkillEvent.status` 응답에서는 반드시 `미확인`, `확인 중`, `출동 요청`, `출동 중`, `처리 완료`, `오탐 처리` 한글 상태값으로 매핑해 내려준다.
- **상태 변경 입력값:** 상태 변경 요청 body의 `status`는 프론트가 한글 상태값을 영문 enum으로 변환해서 보내며, 백엔드는 영문 enum을 입력으로 받는다.
- **priority/riskLevel 매핑:** `priority=1`은 `즉시 확인`, `priority=2`는 `순차 확인`, `priority=3`은 `후순위 확인`으로 매핑한다.
- **location 응답:** 프론트 `RoadkillEvent.location`은 `Equipment.location_name`을 내려주는 방향으로 정한다.
- **cameraId 응답:** 프론트 `RoadkillEvent.cameraId` 제공을 위해 `Equipment`에 표시용 장비 식별자 필드(`camera_id`)를 추가하는 방향으로 정한다.
- **imageUrl 응답:** 백엔드는 `/static/images/...` 상대경로를 내려주고, 프론트가 백엔드 origin을 붙여 처리한다.
- **boundingBox 기준:** bbox는 0~100 퍼센트 좌표, 좌상단 기준으로 정한다. DB에는 `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`로 저장하고 응답에서는 `{ x, y, width, height }`로 묶어 내려준다.
- **AI 모델 통합 방식:** AI 서버를 별도로 띄우지 않고, 전달받은 `ai_model` 폴더의 YOLOv8 추론 코드를 백엔드 내부 모듈로 분리 통합하는 방향으로 정한다. 서버는 하나로 유지하되, AI 추론 코드는 `main.py`나 DB 모델에 섞지 않고 별도 모듈로 둔다.
- **사용 모델:** 추론에는 `ai_model/runs/animal_detector_yolov8n/weights/best.pt`를 사용한다.
- **confidence threshold:** AI 탐지 인정 기준은 우선 `0.3`으로 정한다.
- **AI 입력 이미지 형식:** 백엔드 내장 YOLO 추론 입력 이미지는 우선 `png`, `jpeg/jpg` 포맷을 허용한다.
- **AI 출력 bbox 변환:** 전달받은 `test.py`의 bbox는 중심점 기준 0~1 정규화 좌표이므로, 백엔드 저장/프론트 응답 전 좌상단 기준 0~100 퍼센트 좌표로 변환한다.
- **다중 객체 처리:** 한 이미지에서 여러 객체가 탐지되면 객체별로 여러 Event를 생성한다. 같은 이미지에서 파생된 Event들은 동일한 `image_url`을 공유한다.
- **반복 감지 판정:** 반복 감지는 백엔드가 수행한다. 같은 `camera_id`, 같은 `species`, 같은 bbox 중심점의 객체가 1분 이상 간격으로 다시 감지되면 기존 이벤트를 갱신한다.
- **반복 감지 이벤트 갱신:** 최초 감지는 `repeat_count=0`, `repeat_detection=false`, `priority=3`으로 생성한다. 1회 반복 감지 시 기존 이벤트를 `repeat_count=1`, `repeat_detection=true`, `priority=2`, `last_detected_at=현재 시각`으로 갱신한다. 2회 이상 반복 감지 시 기존 이벤트를 `repeat_count>=2`, `repeat_detection=true`, `priority=1`, `last_detected_at=현재 시각`으로 갱신한다.
- **priority 산출 기준:** priority는 백엔드가 반복 감지 횟수 기준으로 산출한다. `repeat_count=0 -> priority=3`, `repeat_count=1 -> priority=2`, `repeat_count>=2 -> priority=1`로 정한다.
- **RoadkillEvent 필수 응답 필드:** 최종 이벤트 목록/상세 응답 DTO에는 `cameraId`, `repeatDetection`, `lastDetectedAt`을 반드시 포함한다.
- **프론트 계약 문서:** 프론트 API 계약 패치 문서는 `docs/contracts/09_frontend_api_contract_01.md`를 기준으로 한다.

## 11. 데이터베이스 아키텍처 및 데이터 모델 정책
- **테이블 관계 표준:** 모든 테이블 관계는 부모 엔티티의 식별자가 자식 엔티티의 기본키(PK)에 포함되지 않는 **비식별 관계(Non-Identifying Relationship, 분홍색 점선)**를 따르며, 모든 테이블은 독립적인 대리키(`id`, SERIAL/INTEGER PK)를 가진다.
- **카디널리티 표준:** 부모 데이터가 생성될 때 자식 데이터가 존재하지 않는 상태를 인정하기 위해 모든 관계선의 카디널리티는 **`Zero or Many` (0개 이상 허용)**로 통일한다.
- **기준 ERD 문서:** `erd0519.jpg`를 판독해 `docs/erd/erd0519_extracted.md`로 추출했으며, 이후 도메인/DB 설계 단계의 참고 자료로 사용한다.
- **실시간 장애물 탐지(Event) 스키마:**
  - AI 모듈이 최초로 이벤트를 전송할 때 관제사가 배정되지 않으므로, `user_id` 외래키(FK) 컬럼은 **`NULL` 허용(Nullable)**으로 설정한다.
  - 관제 장비 식별을 위해 `equipment_id` 외래키(FK) 컬럼은 **`NOT NULL`**이어야 한다.
  - 지도 컴포넌트와의 연동 및 위치 추적을 위해 위도(`latitude`)와 경도(`longitude`) 필드는 소수점 표현이 가능한 **`FLOAT` 타입의 필수값(`NOT NULL`)**으로 명시한다.
  - AI가 탐지한 장애물 위치를 프론트엔드가 강조 박스로 그릴 수 있도록 `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`를 Event 데이터에 포함하는 방향으로 한다.
  - 이벤트 처리 우선순위를 나타내는 `priority` 필드를 Event 데이터에 포함하는 방향으로 한다.
- **정적 이미지 관리:** 탐지된 도로 장애물 이미지 파일은 서버 내부의 `/static/images/{YYYY}/{MM}/{DD}/` 경로에 UUID 기반의 고유 파일명으로 저장하며, API는 접근 가능한 웹 URL 주소(`image_url`)를 반환한다.
