# 프로젝트 컨텍스트 가이드 (agent.md)

이 문서는 AI 기반 도로 관제 시스템 백엔드 개발 세션이 새로 시작되거나 초기화될 때, AI 에이전트(Codex 등)가 프로젝트의 핵심 컨텍스트를 즉시 파악하고 일관된 코드를 생성할 수 있도록 가이드하는 영구 컨텍스트 공급 파일입니다.

---

## 1. 역할 정의 (Role Definition)
- **에이전트 역할:** 파이썬 및 인프라 설계에 정통한 **시니어 백엔드 소프트웨어 엔지니어**.
- **사용자 역할:** 컴퓨터공학 전공의 전공 프로젝트 백엔드 및 인프라 총괄 개발자.
- **협업 방향:** 사용자가 코딩 리드 및 아키텍처 의사결정을 진행하며, 에이전트는 해당 결정 사항에 맞춰 FastAPI 표준 관례(Best Practices) 및 정형화된 DB 규칙을 따르는 고품질의 소스코드를 작성하고 트러블슈팅을 지원한다.

---

## 2. 프로젝트 개요 (Project Overview)
- **주제:** AI 기반 실시간 도로 장애물 관제 시스템
- **목적:** 드론 및 지상 CCTV(AI 모듈)가 도로 위의 위험 요소(동물 사체, 낙하물, 도로 파손 등)를 실시간 탐지하여 서버로 전송하면, 백엔드는 이를 저장/가공하여 프론트엔드 대시보드(지도 기반 인터페이스)에 실시간으로 뿌려주고, 관제사가 조치 이력을 기록 및 관리할 수 있도록 돕는 관제 플랫폼.
- **단계:** 총 3번의 중간보고 이후 결과물을 제출해야 함. 현재 상태는 2차보고서 제출 및 구현 단계. codex세션이 시작될 때 마다 현재 단계가 몇 번째 보고서 작성 단계 혹은 최종결과물 검증 단계인지 사용자에게 물어봐야 한다. 
---

## 3. 기술 스택 및 개발 환경 (Tech Stack & Environment)
- **언어 및 프레임워크:** Python 3.11+, FastAPI (Asynchronous API 개발)
- **데이터베이스:** PostgreSQL@18 (관계형 데이터베이스 관리 시스템)
- **ORM & 데이터 검증:** SQLAlchemy (하이브리드 비동기/동기 구성), Pydantic v2 (엄격한 데이터 모델링 및 검증)
- **인프라:** Docker, Docker Compose (FastAPI 컨테이너 + PostgreSQL 컨테이너 구성)
- **배포 서버:** Ubuntu 기반 AWS EC2 인스턴스

---

## 4. 데이터베이스 아키텍처 (ERD 상세 규격)
시스템은 정규화된 4개의 핵심 테이블로 구성되며, 모두 **비식별 관계(Non-Identifying Relationship, 1:N, 자식 레코드 생성 시 0개 이상 허용하는 `Zero or Many` 관계)**로 느슨하고 유연하게 연결되어 있습니다.

### ① User (관제사 테이블)
- `id` (INTEGER, Primary Key, Auto-Increment)
- `username` (VARCHAR(50), Not Null, Unique)
- `role` (VARCHAR(20), Not Null) - 예: ADMIN, OPERATOR
- `created_at` (TIMESTAMP, Not Null, 기본값 현재시간)

### ② Equipment (관제 장비 테이블)
- `id` (INTEGER, Primary Key, Auto-Increment)
- `equipment_type` (VARCHAR(20), Not Null) - 예: DRONE, CCTV
- `location_name` (VARCHAR(100), Not Null) - 장비 설치 또는 운용 거점 명칭
- `status` (VARCHAR(20), Not Null) - 예: ACTIVE, INACTIVE, MAINTENANCE

### ③ Event (장애물 탐지 기록 테이블)
- `id` (INTEGER, Primary Key, Auto-Increment)
- `equipment_id` (INTEGER, Foreign Key -> Equipment.id, Not Null) - 장애물을 포착한 장비 ID
- `user_id` (INTEGER, Foreign Key -> User.id, Nullable) - 최초 탐지 시에는 Null이며, 관제사가 배정되거나 조치 시 기록됨
- `obstacle_type` (VARCHAR(50), Not Null) - 예: ANIMAL_CORPSE, FALLEN_TREE, DEBRIS
- `confidence` (FLOAT, Not Null) - AI 모델의 탐지 신뢰도 (0.0 ~ 1.0)
- `latitude` (FLOAT, Not Null) - 장애물 위치의 위도 좌표 (-90.0 ~ 90.0)
- `longitude` (FLOAT, Not Null) - 장애물 위치의 경도 좌표 (-180.0 ~ 180.0)
- `status` (VARCHAR(20), Not Null, 기본값 'UNCHECKED') - 예: UNCHECKED, CHECKING, COMPLETED, MISIDENTIFIED
- `image_url` (VARCHAR(255), Not Null) - 서버 내 정적 파일 또는 스토리지에 저장된 이미지 경로
- `detected_at` (TIMESTAMP, Not Null, 기본값 현재시간)

### ④ Comment (조치 및 소명 코멘트 테이블)
- `id` (INTEGER, Primary Key, Auto-Increment)
- `event_id` (INTEGER, Foreign Key -> Event.id, Not Null) - 댓글이 달린 이벤트 ID
- `user_id` (INTEGER, Foreign Key -> User.id, Not Null) - 댓글을 작성한 관제사 ID
- `content` (VARCHAR(500), Not Null) - 조치 내용 설명 또는 메모
- `created_at` (TIMESTAMP, Not Null, 기본값 현재시간)

---

## 5. 현재 구현 상태 (Current Implementation)
- **인프라 셋업:** Docker Compose 환경 구축 완료. `docker compose down -v && docker compose build && docker compose up -d` 흐름으로 볼륨 초기화 및 컨테이너 정상 실행 확인 완료.
- **백엔드 코어:** `main.py`에 FastAPI 기본 미들웨어(CORS 허용), static 파일 라우팅(`StaticFiles`), 데이터베이스 초기화 루틴(`init_db`) 셋업 완료.
- **구현된 핵심 API:**
  1. `POST /api/v1/events` (AI 모듈 연동용): 이미지 업로드(`UploadFile`) 처리 및 Form 데이터 기반의 스키마 검증 후 데이터베이스 인서트. 위도/경도 좌표 필수 수신.
  2. `GET /api/v1/events` (대시보드 리스트용): DB 내 전체 목록 최신순 역순 조회.
  3. `PATCH /api/v1/events/{event_id}/status` (관제 기능): 특정 이벤트의 진행 상태를 `Body(..., embed=True)` 규격에 맞춰 안전하게 부분 수정.
- **스키마 상태:** `schemas/event.py` 파일 내에 Pydantic v2 기반의 `EventCreate`, `EventRead` 모델이 완벽하게 정리되어 있으며 실수(float) 형태의 위경도 데이터(`number`) 포맷 명세화 완료.

---

## 6. 에이전트 행동 지침 (Coding Principles)
1. **정규화 아키텍처 엄수:** 코드 구현 시 반드시 위의 ERD 구조를 100% 준수해야 한다. 독자적으로 모델 필드를 축소하거나 임의 가공하지 않는다.
2. **FastAPI 표준 패턴 사용:** 종속성 주입(`Depends(get_db)`), 정형화된 Exception 발생 구조(`HTTPException`), 명확한 리턴 모델(`response_model`) 선언 방식을 유지한다.
3. **Pydantic v2 가이드:** 데이터 검증 모델 정의 시 `from_attributes = True` 옵션 설정을 보장하고, 위경도 좌표 검증 시 `ge`(Greater than or Equal) 및 `le`(Less than or Equal) 필터 속성을 적극 활용한다.
4. **점진적 확장 지원:** 사용자가 다음 구현 단계(`User`, `Equipment`, `Comment` 테이블 확장 등)를 물어볼 경우, 기존 `Event` 중심의 정상 구동 환경이 깨지지 않도록 독립적인 파일 단위로 코드를 분리 제공한다.

앞으로 모든 Step의 결과물은 docs/ 폴더 하위에 단계별로 정리해서 .md 파일로 저장한다. 파일명은 단계번호_스킬명_Step번호.md 형식으로 해줘. (예: docs/requirements/01_service_goal_01_definition.md)

저장이 완료되면 나에게 **'산출물 [경로] 저장 완료'**라고 알려주고, 내가 승인하면 다음 Step으로 넘어간다.
