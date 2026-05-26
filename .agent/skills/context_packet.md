# Context Packet (현재 상태 핵심 요약)

> **주의:** 에이전트(LLM)는 작업을 시작하기 전 이 문서를 최우선으로 읽고 현재 프로젝트의 맥락과 제약 사항을 완벽히 숙지해야 합니다.

## 1. 현재 단계 (Current Stage)
- **진행 중인 스킬:** `backend-implementation`
- **현재 목표:** DB/Model 정합성, 공식 프론트 연동 API 골격, AI 탐지 이벤트 생성 API, YOLO 추론 모듈 통합, 반복 감지/priority 계산 실제 적용을 구현했다. 다음 작업은 EC2 Docker 환경에서 `ultralytics` 설치/모델 로드/실제 이미지 업로드 검증이다.
- **주의:** 현재 코드 기준 공식 API 경로는 `/api/events` 계열이다. 기존 `/api/v1/events` 계열은 제거되었으며, 필요하면 호환 라우트를 별도 결정해야 한다. 기존 PostgreSQL 볼륨에 예전 스키마가 남아 있으면 `create_all()`만으로는 새 컬럼이 반영되지 않으므로 실제 서버 검증 전 DB 초기화 또는 마이그레이션 전략이 필요하다.

## 2. 프로젝트 개요 및 초기 아이디어
- **프로젝트 명:** AI 기반 실시간 도로 장애물 관제 시스템
- **초기 아이디어:** 드론 및 CCTV(AI 모듈)가 도로 위 장애물, 특히 동물 사체를 실시간 탐지하여 백엔드로 전송하면, 프론트엔드 대시보드에 알림과 확인 화면을 띄우고 관제사가 상황을 확인하는 시스템.
- **1차 사용자:** 도로 관제사.
- **핵심 문제:** 사람이 직접 순찰하거나 CCTV 영상을 감시해야 하므로 도로 장애물 발견이 늦어진다.
- **백엔드 우선 가치:** AI 모델과 프론트엔드 사이의 안정적인 데이터 전달을 최우선, 빠른 데이터 처리를 2순위로 둔다.

## 3. 확정된 핵심 결정 (Decisions)
*(상세 내용은 `docs/decisions/DECISIONS.md` 참고)*
- FastAPI + PostgreSQL 기반 비동기 REST API 구축.
- 모든 DB 테이블은 독립적인 PK(`id`)를 가지며, 비식별 관계(Non-Identifying, `Zero or Many`)로 연결됨.
- `Event` 테이블에 위도(`latitude`)와 경도(`longitude`)는 소수점(`FLOAT`) 필수값으로 포함.
- `erd0519.jpg`를 판독해 `docs/erd/erd0519_extracted.md`로 추출했으며, `User`, `Equipment`, `Event`, `Comment` 4개 테이블 구조를 참고한다.
- `Event`에는 프론트엔드가 장애물 강조 박스를 그릴 수 있도록 `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`를 포함하는 방향으로 한다.
- `Event`에는 이벤트 처리 우선순위를 나타내는 `priority`를 포함하는 방향으로 한다.
- 요구사항은 도로 관제사가 AI 탐지 이벤트를 인지, 확인, 판단, 처리, 종결하는 업무 흐름을 중심으로 정의한다.
- 핵심 유스케이스는 AI 탐지 이벤트 등록, 신규 이벤트 인지, 이벤트 목록/상세 확인, 장애물 강조 영역 확인, 이벤트 상태 변경, 처리 기록 작성, 오탐 이벤트 구분이다.
- MVP 필수 요구사항은 AI 탐지 결과 수신, 이벤트 등록, 목록/상세 확인, 위치/탐지 근거/bbox/priority 제공, 상태 변경, 오탐 구분, 변경 결과 저장 및 재조회다.
- 처리 기록 작성/조회, 관제사/장비 식별 정보 관리, 관제사 권한 통제, AI 요청 신뢰성 확인은 Should-have로 둔다.
- AI 모델 구현, 프론트 화면 디자인 세부 구현, 대규모 분산 처리, 고가용성 구성, 다중 객체 Detection 도메인, 별도 EventStatusHistory, Equipment 자체 좌표 관리는 MVP에서 제외한다.
- MVP 핵심 목표는 AI가 탐지한 도로 위 동물 사체 이벤트가 백엔드를 통해 관제사 화면에 전달되고, 관제사가 위치와 탐지 근거를 확인한 뒤 이벤트 상태를 관리할 수 있게 하는 것이다.
- MVP 포함 범위는 AI 탐지 결과 수신, 신규 이벤트 등록, 이벤트 목록/상세 제공, 위치 정보 제공, 탐지 근거 제공, bbox 정보 제공, priority 제공, 이벤트 상태 변경, 오탐 구분, 최신 상태 재조회, 필수 정보 검증이다.
- MVP 조건부 포함 범위는 처리 기록/코멘트 작성 및 조회, 관제사 식별 정보 관리, 장비 식별 정보 관리, 단순 접근 통제, AI 요청 신뢰성 확인이다.
- MVP 제외 범위는 AI 모델 학습/추론, 프론트 디자인 세부 구현, 통계/분석 대시보드, 대규모 분산 처리, 완전한 고가용성, 다중 객체 Detection, 별도 EventStatusHistory, Equipment 자체 지도 좌표, 복잡한 역할/권한 관리, 관리자용 사용자/장비 관리 고도화다.
- 릴리스 마일스톤은 1주차 이벤트 기본 흐름 복구, 2주차 관제사 확인 흐름 강화, 3주차 AI/프론트 연계 계약 확정 및 통합 검증, 4주차 시연 안정화 및 문서 정리다.
- 최종 도메인 엔티티는 `User`, `Equipment`, `Event`, `Comment` 네 가지다.
- 최종 도메인 관계는 `User -> Event`, `Equipment -> Event`, `User -> Comment`, `Event -> Comment` 네 가지이며 모두 비식별 관계다.
- `Equipment`에는 프론트 `cameraId` 응답에 사용할 `camera_id`를 포함한다.
- `Event`의 핵심 논리 속성은 `equipment_id`, `user_id`, `obstacle_type`, `species`, `confidence`, `latitude`, `longitude`, `status`, `image_url`, `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`, `priority`, `detected_at`, `repeat_detection`, `repeat_count`, `last_detected_at`이다.
- `Comment`는 처리 기록/코멘트 기능을 포함할 때 사용하는 조건부 MVP 도메인이다.
- `Detection`, `EventStatusHistory`, `Equipment` 자체 지도 좌표, 복잡한 권한/권한 그룹 모델은 도메인 모델에 포함하지 않는다.
- FastAPI 백엔드는 `main.py`, `core/`, `dependencies/`, `models/`, `schemas/`, `routers/`, `services/`, `storage/`, `static/` 계층으로 분리하는 방향으로 설계한다.
- `main.py`는 앱 생성, CORS, `/static` 마운트, 라우터 등록, startup 초기화만 담당하고 도메인 로직은 두지 않는다.
- `routers/`는 HTTP 엔드포인트, `services/`는 비즈니스 유스케이스, `storage/`는 이미지 저장, `dependencies/`는 DB 세션과 인증/AI 검증 dependency, `core/`는 설정/예외 처리를 담당한다.
- 기존 CORS 설정, `/static` 마운트, `static/images/{YYYY}/{MM}/{DD}/` 이미지 저장 정책, `DATABASE_URL` 기반 DB 연결은 보존한다.
- 모듈 경계 규칙: `models`는 `schemas/routers/services`를 참조하지 않고, `schemas`는 `models`를 참조하지 않으며, `services`는 `routers`를 참조하지 않는다.
- PostgreSQL 물리 테이블은 `users`, `equipment`, `events`, `comments` 네 개로 설계한다.
- 모든 테이블은 `SERIAL PRIMARY KEY` 형식의 독립 `id`를 가진다.
- 장비 종류 컬럼명은 `equipment.equipment_type`으로 통일한다.
- 프론트 `cameraId` 응답을 위해 `equipment.camera_id`를 추가한다.
- `events.equipment_id`는 `equipment.id`를 참조하는 `NOT NULL` FK이고, `events.user_id`는 `users.id`를 참조하는 nullable FK다.
- FK 삭제 정책은 `events.equipment_id ON DELETE RESTRICT`, `events.user_id ON DELETE SET NULL`, `comments.event_id ON DELETE CASCADE`, `comments.user_id ON DELETE RESTRICT`다.
- `events.latitude`, `events.longitude`, `events.bbox_x`, `events.bbox_y`, `events.bbox_width`, `events.bbox_height`는 모두 `FLOAT NOT NULL`로 설계한다.
- `events.priority`는 `INTEGER NOT NULL`이며 허용값은 `1`, `2`, `3`이다.
- `events.repeat_detection`, `events.repeat_count`, `events.last_detected_at`을 추가한다.
- `events.obstacle_type`은 상위 유형 `ANIMAL`로 저장하고, YOLO가 탐지한 세부 종(`gorani`, `wild_boar`, `raccoon`)은 `events.species`에 별도 저장한다.
- MVP에서는 위도/경도를 검색 조건이 아닌 지도 표시 데이터로 사용하므로 PostGIS 또는 공간 인덱스는 도입하지 않는다.
- 최종 구현 순서는 DB/Model 정합성 -> Schema 정리 -> 공통 인프라 분리 -> Event service/router 구현 -> 검증 순서다.
- Must-have 구현 중심은 Event 생성, 목록 조회, 상세 조회, 상태 변경, 이미지 저장, DB 저장/재조회 검증이다.
- 첫 구현 티켓은 기존 개발 DB와 새 설계 충돌을 피하기 위한 개발 DB 초기화 또는 마이그레이션 전략 확정이다.
- 조건부 티켓은 Comment 작성/조회 API, 단순 AI 요청 검증 dependency, 단순 관제사 접근 통제다.
- AI 모델 학습, 프론트 디자인, 통계/분석, 대규모 인프라, 다중 객체 Detection 테이블, EventStatusHistory, Equipment 자체 좌표, 복잡한 권한 관리, 관리자용 사용자/장비 관리 고도화는 작업 티켓으로 만들지 않는다. 단, 전달받은 `ai_model`의 추론 코드와 `best.pt`를 백엔드 내부 AI 모듈로 통합하는 작업은 구현 범위에 포함할 수 있다.
- 첫 구현 지시서 대상은 `T-02`~`T-07` 묶음인 DB/Model 정합성 1차 구현이다.
- 첫 구현 지시서의 변경 범위는 `models/user.py`, `models/equipment.py`, `models/comment.py` 생성과 `models/event.py`, `models/__init__.py`, `database.py` 수정이다.
- 첫 구현 지시서에서는 `main.py`, `schemas/`, `routers/`, `services/`, `storage/`, `docker-compose.yml`을 수정하지 않는다.
- 첫 구현 지시서의 완료 기준은 `python -m compileall database.py models` 성공 및 SQLAlchemy metadata에 `users`, `equipment`, `events`, `comments` 테이블 포함이다.
- 프론트엔드 팀은 1차 목업 배포 및 GitHub 저장소를 공유했다.
  - 배포: `https://roadkill-detection.vercel.app/`
  - 저장소: `https://github.com/haruby2357/Roadkill-Detection`
- CORS는 프론트 배포 URL `https://roadkill-detection.vercel.app`과 로컬 개발 URL을 기본 허용한다. 추가 origin은 `CORS_ORIGINS` 환경변수로 관리한다.
- 프론트엔드가 요구한 1차 최소 API는 `GET /api/events`, `GET /api/events/{eventId}`, `PATCH /api/events/{eventId}/status`이며, 공식 프론트 연동 경로는 `/api` prefix로 정한다.
- 현재 프로토타입 API 경로는 `/api/v1/events` 계열이므로, 실제 연동 시 공식 경로는 `/api/events`로 맞춘다. `/api/v1/events` 호환 유지 여부는 남은 결정 사항이다.
- 프론트엔드 `RoadkillEvent` 타입은 `id`, `riskLevel`, `detectedAt`, `location`, `objectType`, `status`, `description`, `cameraId`, `repeatDetection`, `lastDetectedAt`, `imageUrl`, `boundingBox`를 요구한다.
- `priority`는 `riskLevel`로 변환한다. `1=즉시 확인`, `2=순차 확인`, `3=후순위 확인`으로 정한다.
- `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`는 프론트의 `boundingBox: { x, y, width, height }`로 변환하며, 0~100 퍼센트 좌표/좌상단 기준으로 정한다.
- 프론트 `RoadkillEvent.location`은 `Equipment.location_name`을 내려주는 방향으로 정한다.
- `repeatDetection`, `lastDetectedAt`은 기존 백엔드 설계에서 충분히 고려되지 않은 필드였으나, AI 팀 논의 후 백엔드가 반복 감지를 계산하고 저장/응답하는 방향으로 바뀌었다.
- 프론트 `RoadkillEvent.cameraId` 제공을 위해 `equipment.camera_id` 필드를 추가하는 방향으로 정한다.
- `description`은 별도 컬럼 없이 자동 생성 가능하지만, AI/관제사가 제공한 설명을 보존하려면 `events.description` 또는 `comments` 사용 기준을 정해야 한다.
- 프론트 `RoadkillEvent.status` 응답은 `미확인`, `확인 중`, `출동 요청`, `출동 중`, `처리 완료`, `오탐 처리` 한글 상태값으로 내려준다.
- 상태 변경 요청 body의 `status`는 프론트가 한글 상태값을 백엔드 내부 영문 enum으로 변환해서 보낸다. 백엔드는 `UNCHECKED`, `CHECKING`, `DISPATCH_REQUESTED`, `DISPATCHING`, `COMPLETED`, `MISIDENTIFIED` 6개 영문 enum을 입력으로 받는다.
- 최종 이벤트 목록/상세 응답 DTO에는 `cameraId`, `repeatDetection`, `lastDetectedAt`을 반드시 포함한다.
- AI 모델 통합은 별도 AI 서버가 아니라 FastAPI 백엔드 내부 모듈로 진행하는 방향이다. 서버는 하나로 유지하되, YOLO 추론 코드는 `main.py`나 DB 모델에 섞지 않고 별도 모듈로 분리한다.
- 사용할 AI 모델은 `ai_model/runs/animal_detector_yolov8n/weights/best.pt`다.
- 전달받은 `ai_model/` 원본 파일은 AI 파트 산출물로 보존하고 직접 수정하지 않는다. 백엔드 구현 시 `ai_model/test.py`의 추론 로직을 참고해 별도 백엔드 모듈(예: `ai/yolo_detector.py`)을 만들고, 그 모듈에서 `best.pt`를 로드한다.
- 전달받은 `ai_model/test.py`는 현재 `last.pt`와 conf `0.3`을 사용하지만, 원본 파일을 고치지 말고 백엔드 추론 모듈에서 모델 경로를 `best.pt`로 지정한다.
- confidence threshold는 우선 `0.3`으로 확정한다.
- 백엔드 내장 YOLO 추론 입력 이미지는 우선 `png`, `jpeg/jpg` 포맷을 허용한다.
- `ai_model/test.py`의 bbox는 중심점 기준 0~1 정규화 좌표이므로, 백엔드 저장/프론트 응답 전 좌상단 기준 0~100 퍼센트 좌표로 변환한다.
- 한 이미지에서 여러 객체가 감지되면 객체별로 여러 Event를 생성하고, 같은 이미지에서 파생된 Event들은 동일한 `image_url`을 공유한다.
- 반복 감지는 백엔드가 계산한다. 같은 `camera_id`, 같은 `species`, bbox 중심점이 완전히 동일한 객체가 1분 이상 간격으로 다시 감지되면 기존 이벤트를 갱신한다.
- priority는 백엔드가 반복 감지 횟수 기준으로 산출한다. 최초 감지는 `repeat_count=0`, `priority=3`; 1회 반복 감지는 `repeat_count=1`, `priority=2`; 2회 이상 반복 감지는 `repeat_count>=2`, `priority=1`로 정한다.
- AI/백엔드 팀원 의견으로 confidence 임계값 미만은 `미확인`, 임계값 이상은 `출동 요청`으로 초기 상태를 잡는 방안이 제안되었으나, 현재 priority/riskLevel은 반복 감지 횟수 기준으로 확정했다. status 초기값과 priority는 별도 개념으로 관리한다.
- `POST /api/events/detect`에서 없는 `cameraId`는 백엔드가 `Equipment`로 자동 생성한다. 기본 `equipment_type`은 `CCTV`, `status`는 `ACTIVE`, `locationName`이 없으면 `location_name`은 `미지정 위치`로 저장한다.

## 4. 범위 및 제외 범위 (Scope)
- **포함:** (진행하면서 확정할 예정)
- **제외 (Out of Scope):** (진행하면서 확정할 예정)

## 5. 활성 가정 및 미결정 질문
*(상세 내용은 `ASSUMPTIONS.md` 및 `OPEN_QUESTIONS.md` 참고)*
- **가정:** AI 서버를 별도로 띄우지 않고, 전달받은 `ai_model`의 YOLO 추론 로직을 FastAPI 백엔드 내부 모듈로 통합한다. 단, `ai_model` 원본 파일은 수정하지 않고 참조용/원본 산출물로 보존한다.
- **가정:** 반복 감지 여부(`repeatDetection`), 반복 횟수(`repeat_count`), 마지막 감지 시각(`lastDetectedAt`)은 백엔드가 동일 `camera_id`, 동일 `species`, 1분 이상 간격, bbox 중심점 완전 동일 기준으로 계산한다.
- **질문:** 프론트엔드 실시간 알림 방식(SSE vs Polling) 및 관제사 인증 방식 미정.
- **확정:** 백엔드 내장 YOLO 추론 API는 `multipart/form-data`로 이미지를 받는다. 공식 경로는 `POST /api/events/detect`다.
- **질문:** `ai_model` 실행에 필요한 Python, `ultralytics`, `torch` 버전 및 EC2 CPU 추론 속도는 아직 확인해야 한다.
- **질문:** 관제 화면의 실시간 영상 소스를 백엔드가 관리할지, 프론트엔드가 별도로 연결할지 미정이다.
- **질문:** 처리 기록 작성/조회 기능을 MVP에 포함할지, 상태 변경 이후 후순위로 둘지 미정이다.
- **질문:** `RoadkillEvent.description`은 응답 DTO에서 자동 생성하는 방향이나, 생성 문장 규칙은 아직 미정이다.
- **질문:** 공식 프론트 연동 경로는 `/api/events`로 확정했으나, 기존 `/api/v1/events`를 호환 유지할지 제거할지 미정이다.
- **질문:** 프론트엔드 목록/상세 화면의 필수 표시 필드와 정보 부족 이벤트 처리 방식은 프론트 목업 기준으로 더 구체화되었으나, 백엔드 응답 계약으로 최종 확정해야 한다.

## 6. 산출물 저장 현황
- `requirements-decomposition` Step 1~11 산출물은 `docs/requirements/02_requirements_decomposition_01.md`부터 `docs/requirements/02_requirements_decomposition_11.md`까지 저장되어 있다.
- 최종 요구사항 명세서는 `docs/requirements/02_requirements_decomposition_11.md`이다.
- `mvp-scope-planning` Step 1~6 산출물은 `docs/mvp/03_mvp_scope_planning_01.md`부터 `docs/mvp/03_mvp_scope_planning_06.md`까지 저장되어 있다.
- 최종 MVP 범위 정의서는 `docs/mvp/03_mvp_scope_planning_06.md`이다.
- `domain-modeling` Step 1~6 산출물은 `docs/domain/04_domain_modeling_01.md`부터 `docs/domain/04_domain_modeling_06.md`까지 저장되어 있다.
- 최종 도메인 모델 명세서는 `docs/domain/04_domain_modeling_06.md`이다.
- `architecture-planning` Step 1~6 산출물은 `docs/architecture/05_architecture_planning_01.md`부터 `docs/architecture/05_architecture_planning_06.md`까지 저장되어 있다.
- 최종 아키텍처 정의서는 `docs/architecture/05_architecture_planning_06.md`이다.
- `database-design` Step 1~6 산출물은 `docs/database/06_database_design_01.md`부터 `docs/database/06_database_design_06.md`까지 저장되어 있다.
- 최종 데이터베이스 설계서는 `docs/database/06_database_design_06.md`이다.
- `task-breakdown` Step 1~6 산출물은 `docs/tasks/07_task_breakdown_01.md`부터 `docs/tasks/07_task_breakdown_06.md`까지 저장되어 있다.
- 최종 작업 백로그는 `docs/tasks/07_task_breakdown_06.md`이다.
- `implementation-prompt-writer` Step 1~5 산출물은 `docs/implementation/08_implementation_prompt_writer_01.md`부터 `docs/implementation/08_implementation_prompt_writer_05.md`까지 저장되어 있다.
- 최종 개발 지시서는 `docs/implementation/08_implementation_prompt_writer_05.md`이다.
- 프론트 API 계약 패치 문서는 `docs/contracts/09_frontend_api_contract_01.md`에 저장되어 있다.
- 백엔드 API 사용법 가이드는 `docs/backend/09_backend_implementation_06.md`에 저장되어 있다.
- 백엔드 테스트 코드는 `tests/test_backend_api.py`에 저장되어 있고, 테스트 산출물 문서는 `docs/backend/09_backend_implementation_07.md`에 저장되어 있다.
- 이벤트 메모 API는 `GET /api/events/{eventId}/comments`, `POST /api/events/{eventId}/comments`로 추가되었다.
- AI 파트 전달 폴더는 `ai_model/`이며, 학습 코드(`main.py`), 추론 코드(`test.py`), 테스트 이미지, 학습 결과, `best.pt`/`last.pt`, 테스트 결과 JSON을 포함한다.
- resume 이후 대화 요약 로그는 `codex-session_2.log`에 저장되어 있다.

## 7. 현재 코드 상태 메모
- 현재 구현은 `Event` 단일 리소스 중심 프로토타입이다.
- `POST /api/v1/events`, `GET /api/v1/events`, `PATCH /api/v1/events/{event_id}/status`, 정적 이미지 저장/서빙 로직이 있다.
- 프론트 요청 공식 경로는 `/api/events` 계열로 확정되었으므로 현재 `/api/v1/events`와 차이가 있다.
- 동작 검증 중 `POST /api/v1/events`에서 `TypeError: 'user_id' is an invalid keyword argument for Event` 오류가 확인되었다.
- 원인: `main.py`와 `schemas/event.py`는 `user_id`를 참조하지만, `models/event.py`의 `Event` 모델에는 `user_id` 컬럼이 없다.
- 추가 불일치: `models/event.py`에는 필수 `equipment_type`이 있으나 현재 POST 입력 스키마와 생성 로직에는 없다.
- 추가 불일치: 현재 코드에는 프론트 `RoadkillEvent`의 `repeatDetection`, `lastDetectedAt`, 표시용 `cameraId`, 한글 상태값 응답 체계가 아직 반영되어 있지 않다. 문서와 구현지시서는 해당 계약을 반영하도록 패치되었다.
- DB/Model 정합성 1차 구현을 완료했다.
  - `models/user.py`, `models/equipment.py`, `models/comment.py`를 추가했다.
  - `models/event.py`를 최종 설계 기준으로 재작성했다.
  - `models/__init__.py`, `database.py`에서 4개 모델이 metadata에 등록되도록 수정했다.
- 공식 프론트 연동 API 골격 구현을 완료했다.
  - `schemas/event.py`를 프론트 `RoadkillEvent` 응답 계약 기준으로 재정리했다.
  - `dependencies/database.py`, `services/event_service.py`, `routers/events.py`, `routers/health.py`를 추가했다.
  - `main.py`는 CORS, static mount, router 등록, startup 초기화 중심으로 정리했다.
  - 현재 라우트는 `/`, `/api/events`, `/api/events/{event_id}`, `/api/events/{event_id}/status`, `/static`이다.
- AI 탐지 이벤트 생성 API 및 YOLO 추론 모듈 통합을 구현했다.
  - `ai/yolo_detector.py`를 추가하고 `ai_model/runs/animal_detector_yolov8n/weights/best.pt`를 로드하도록 했다.
  - `storage/image_storage.py`를 추가하고 `png`, `jpg`, `jpeg` 업로드 이미지를 `/static/images/{YYYY}/{MM}/{DD}/`에 저장하도록 했다.
  - `POST /api/events/detect`를 추가했다. 입력은 `cameraId`, `latitude`, `longitude`, 선택 `locationName`, `image`다.
  - 없는 `cameraId`는 `Equipment`로 자동 생성한다.
  - 같은 장비, 같은 종, bbox 중심점 완전 동일, 1분 이상 간격이면 기존 이벤트의 `repeat_count`, `repeat_detection`, `priority`, `last_detected_at`을 갱신한다.
  - `requirements.txt`에 `ultralytics==8.3.38`을 추가했다.
- 에러 응답 정리를 구현했다.
  - `core/errors.py`, `core/exception_handlers.py`를 추가했다.
  - 주요 오류 응답은 `{ error_code, message, detail }` 구조를 사용한다.
  - FastAPI/Pydantic validation 오류도 `VALIDATION_ERROR` 코드로 감싼다.
- 검증 결과:
  - `venv/bin/python -m compileall database.py models schemas dependencies services routers main.py` 성공.
  - `venv/bin/python -c "from main import app; print(sorted([route.path for route in app.routes]))"` 결과에 공식 API 경로와 `/api/events/detect`가 포함됨.
  - `venv/bin/python -c "import models; from database import Base; print(sorted(Base.metadata.tables.keys()))"` 결과: `['comments', 'equipment', 'events', 'users']`.
- EC2에서 Docker DB 초기화 후 `GET /api/events`가 `[]`를 반환하는 것을 사용자가 확인했다.
- EC2에서 실제 이미지 업로드를 통한 YOLO 추론, Event 생성, 반복 감지 priority 격상, 상태 변경 API를 확인했다.
- 검증 중 기존 업로드 이미지가 Docker 재빌드 후 404가 되는 문제가 확인되어 `docker-compose.yml`에 `static_images:/app/static/images` 볼륨을 추가했다. 기존에 사라진 이미지 파일은 복구되지 않지만, 이후 업로드 이미지는 컨테이너 재생성 후에도 유지된다.
- `httpx==0.27.0`을 추가해 `unittest` 기반 통합 테스트를 작성했다.
- 최근 커밋:
  - `56b132b docs: add implementation prompt artifacts`
  - `239cc23 chore: remove tracked venv and pycache`
- `venv/`, `.venv/`, `__pycache__/`, `*.py[cod]`는 `.gitignore`에 추가되었고 Git 추적에서 제거되었다. 로컬 `venv` 디렉터리는 삭제하지 않았다.

## 8. 에이전트 행동 제약 및 지시 사항
- **[경고]** 현재는 구현 단계에 진입했으며 DB/Model 및 공식 프론트 API 골격이 수정된 상태다. 다음 코드 변경 전에는 기존 DB 볼륨 초기화/마이그레이션 필요 여부를 확인해야 한다.
- **[지시]** 사용자의 지시가 있을 때까지 대기하며, 지시가 들어오면 한 번에 하나의 Step만 진행하라.
- **[지시]** 각 단계 산출물 승인 후 사용자가 요청하면 확정 사항은 `docs/decisions/DECISIONS.md`, 미결정 사항은 `docs/decisions/OPEN_QUESTIONS.md`, 다음 작업 맥락은 이 `context_packet.md`에 반영한다.
- **[지시]** 모든 Step 산출물은 `docs/` 하위에 단계별 Markdown 파일로 저장한다. 파일명은 `단계번호_스킬명_Step번호.md` 형식을 따른다.
