# Context Packet (현재 상태 핵심 요약)

> **주의:** 에이전트(LLM)는 작업을 시작하기 전 이 문서를 최우선으로 읽고 현재 프로젝트의 맥락과 제약 사항을 완벽히 숙지해야 합니다.

## 1. 현재 단계 (Current Stage)
- **진행 대기 중인 스킬:** `implementation-prompt-writer` (구현 지시서 작성)
- **현재 목표:** `implementation-prompt-writer` Step 1~5 산출물 저장 완료. 첫 구현 지시서는 DB/Model 정합성 1차 구현을 대상으로 한다.

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
- `Event`의 핵심 논리 속성은 `equipment_id`, `user_id`, `obstacle_type`, `confidence`, `latitude`, `longitude`, `status`, `image_url`, `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`, `priority`, `detected_at`이다.
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
- `events.equipment_id`는 `equipment.id`를 참조하는 `NOT NULL` FK이고, `events.user_id`는 `users.id`를 참조하는 nullable FK다.
- FK 삭제 정책은 `events.equipment_id ON DELETE RESTRICT`, `events.user_id ON DELETE SET NULL`, `comments.event_id ON DELETE CASCADE`, `comments.user_id ON DELETE RESTRICT`다.
- `events.latitude`, `events.longitude`, `events.bbox_x`, `events.bbox_y`, `events.bbox_width`, `events.bbox_height`는 모두 `FLOAT NOT NULL`로 설계한다.
- `events.priority`는 `INTEGER NOT NULL`이며 최소 제약은 `priority >= 1`이다.
- MVP에서는 위도/경도를 검색 조건이 아닌 지도 표시 데이터로 사용하므로 PostGIS 또는 공간 인덱스는 도입하지 않는다.
- 최종 구현 순서는 DB/Model 정합성 -> Schema 정리 -> 공통 인프라 분리 -> Event service/router 구현 -> 검증 순서다.
- Must-have 구현 중심은 Event 생성, 목록 조회, 상세 조회, 상태 변경, 이미지 저장, DB 저장/재조회 검증이다.
- 첫 구현 티켓은 기존 개발 DB와 새 설계 충돌을 피하기 위한 개발 DB 초기화 또는 마이그레이션 전략 확정이다.
- 조건부 티켓은 Comment 작성/조회 API, 단순 AI 요청 검증 dependency, 단순 관제사 접근 통제다.
- AI 모델 학습/추론, 프론트 디자인, 통계/분석, 대규모 인프라, 다중 객체 Detection, EventStatusHistory, Equipment 자체 좌표, 복잡한 권한 관리, 관리자용 사용자/장비 관리 고도화는 작업 티켓으로 만들지 않는다.
- 첫 구현 지시서 대상은 `T-02`~`T-07` 묶음인 DB/Model 정합성 1차 구현이다.
- 첫 구현 지시서의 변경 범위는 `models/user.py`, `models/equipment.py`, `models/comment.py` 생성과 `models/event.py`, `models/__init__.py`, `database.py` 수정이다.
- 첫 구현 지시서에서는 `main.py`, `schemas/`, `routers/`, `services/`, `storage/`, `docker-compose.yml`을 수정하지 않는다.
- 첫 구현 지시서의 완료 기준은 `python -m compileall database.py models` 성공 및 SQLAlchemy metadata에 `users`, `equipment`, `events`, `comments` 테이블 포함이다.

## 4. 범위 및 제외 범위 (Scope)
- **포함:** (진행하면서 확정할 예정)
- **제외 (Out of Scope):** (진행하면서 확정할 예정)

## 5. 활성 가정 및 미결정 질문
*(상세 내용은 `ASSUMPTIONS.md` 및 `OPEN_QUESTIONS.md` 참고)*
- **가정:** AI 모듈은 실시간 HTTP(POST) 통신이 가능하며 안정적인 네트워크를 사용함.
- **질문:** 프론트엔드 실시간 알림 방식(SSE vs Polling) 및 관제사 인증 방식 미정.
- **질문:** AI -> 백엔드 공식 요청 형식은 아직 미정이다. 현재 코드의 `multipart/form-data`는 프로토타입 입력 형식일 뿐 공식 합의 사항이 아니다.
- **질문:** bbox 좌표 기준(픽셀/정규화), bbox 기준점(좌상단/중심점), 프론트엔드 영상/이미지 매핑 방식은 AI/프론트엔드 파트와 협의가 필요하다.
- **질문:** `priority` 값 체계(숫자형 등급 또는 문자열 enum)는 아직 미정이다.
- **질문:** 관제 화면의 실시간 영상 소스를 백엔드가 관리할지, 프론트엔드가 별도로 연결할지 미정이다.
- **질문:** 처리 기록 작성/조회 기능을 MVP에 포함할지, 상태 변경 이후 후순위로 둘지 미정이다.
- **질문:** 프론트엔드 목록/상세 화면의 필수 표시 필드와 정보 부족 이벤트 처리 방식은 미정이다.
- **질문:** AI 파트가 MVP 통합 시점까지 준비되지 않은 경우 테스트 클라이언트나 샘플 요청 데이터로 AI 탐지 이벤트를 대체해 검증할지 미정이다.

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

## 7. 현재 코드 상태 메모
- 현재 구현은 `Event` 단일 리소스 중심 프로토타입이다.
- `POST /api/v1/events`, `GET /api/v1/events`, `PATCH /api/v1/events/{event_id}/status`, 정적 이미지 저장/서빙 로직이 있다.
- 동작 검증 중 `POST /api/v1/events`에서 `TypeError: 'user_id' is an invalid keyword argument for Event` 오류가 확인되었다.
- 원인: `main.py`와 `schemas/event.py`는 `user_id`를 참조하지만, `models/event.py`의 `Event` 모델에는 `user_id` 컬럼이 없다.
- 추가 불일치: `models/event.py`에는 필수 `equipment_type`이 있으나 현재 POST 입력 스키마와 생성 로직에는 없다.
- 아직 정식 구현 수정은 하지 않았다. 이후 `domain-modeling`, `database-design`, `backend-implementation` 단계에서 문서 기준으로 정합성을 맞춰야 한다.

## 8. 에이전트 행동 제약 및 지시 사항
- **[경고]** 현재는 기획/요구사항 정리 흐름이므로, 사용자가 구현 단계를 명시하기 전까지 코드를 작성하거나 API/DB 상세 설계를 확정하지 마라.
- **[지시]** 사용자의 지시가 있을 때까지 대기하며, 지시가 들어오면 한 번에 하나의 Step만 진행하라.
- **[지시]** 각 단계 산출물 승인 후 사용자가 요청하면 확정 사항은 `docs/decisions/DECISIONS.md`, 미결정 사항은 `docs/decisions/OPEN_QUESTIONS.md`, 다음 작업 맥락은 이 `context_packet.md`에 반영한다.
- **[지시]** 모든 Step 산출물은 `docs/` 하위에 단계별 Markdown 파일로 저장한다. 파일명은 `단계번호_스킬명_Step번호.md` 형식을 따른다.
