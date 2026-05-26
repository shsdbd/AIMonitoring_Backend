# Step 3. 백엔드 작업 분해: API & Logic

## 1. 분해 기준

API & Logic 작업은 FastAPI 라우터, 서비스 계층, 이미지 저장, 공통 dependency, 예외 처리, 검증 흐름을 구현 가능한 티켓으로 분해한다.

이 단계에서는 티켓만 정의하며, 실제 코드는 작성하지 않는다.

## 2. 구조/인프라 작업

- [ ] **API-01. `main.py` 앱 조립 책임 축소**
  - `main.py`에는 FastAPI 앱 생성, CORS, static 마운트, 라우터 등록, startup 초기화만 남기는 구조로 정리한다.

- [ ] **API-02. 공통 DB dependency 분리**
  - 기존 `get_db`를 `dependencies/database.py`로 분리한다.
  - 라우터는 `Depends(get_db)`만 사용하도록 한다.

- [ ] **API-03. 이미지 저장 모듈 분리**
  - 기존 `save_upload_image` 책임을 `storage/image_storage.py`로 분리한다.
  - 이미지 MIME 타입, 확장자, 날짜별 디렉터리, UUID 파일명, static URL 생성 정책을 유지한다.

- [ ] **API-04. 공통 비즈니스 에러 구조 도입**
  - `core/errors.py`에 공통 에러 코드/예외 개념을 둔다.
  - `EVENT_NOT_FOUND`, `INVALID_EVENT_STATUS`, `INVALID_EVENT_PAYLOAD`, `INVALID_IMAGE_FILE`, `EQUIPMENT_NOT_FOUND`를 우선 대상으로 한다.

- [ ] **API-05. 전역 예외 핸들러 설계 반영**
  - `core/exception_handlers.py`에서 공통 오류 응답 형식을 등록할 수 있도록 구조를 마련한다.

## 3. Event API 작업

- [ ] **API-06. Event 스키마 재정리**
  - `EventCreate`, `EventRead`, `EventStatusUpdate` 등 MVP에 필요한 스키마를 정리한다.
  - 포함 필드: `equipment_id`, `obstacle_type`, `confidence`, `latitude`, `longitude`, `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`, `priority`, `image_url/status/detected_at`

- [ ] **API-07. Event router 분리**
  - 기존 `main.py`의 `/api/v1/events` 관련 라우트를 `routers/events.py`로 분리한다.
  - 생성, 목록 조회, 상세 조회, 상태 변경 엔드포인트를 포함한다.

- [ ] **API-08. Event service 작성**
  - 이벤트 생성, 목록 조회, 상세 조회, 상태 변경 비즈니스 흐름을 `services/event_service.py`로 분리한다.
  - 라우터에는 비즈니스 로직을 두지 않는다.

- [ ] **API-09. Event 생성 흐름 정합성 복구**
  - 이벤트 생성 시 `equipment_id`가 존재하는 장비를 참조하도록 한다.
  - `user_id`는 최초 생성 시 `NULL`을 허용한다.
  - bbox와 priority를 필수 입력으로 반영한다.

- [ ] **API-10. Event 목록 조회 구현 범위 정리**
  - 최신순 목록 조회를 기본으로 한다.
  - 상태별 조회나 우선순위 정렬은 MVP 필요 시 옵션으로 분리한다.

- [ ] **API-11. Event 상세 조회 추가**
  - 관제사가 선택한 이벤트의 위치, 탐지 근거, bbox, priority, 상태를 확인할 수 있도록 상세 조회를 제공한다.

- [ ] **API-12. Event 상태 변경 흐름 정리**
  - 허용 상태: `UNCHECKED`, `CHECKING`, `COMPLETED`, `MISIDENTIFIED`
  - 존재하지 않는 이벤트와 잘못된 상태값을 공통 에러로 처리한다.

## 4. 기준 데이터/보조 API 작업

- [ ] **API-13. Equipment 기준 데이터 준비**
  - 이벤트 생성 전 사용할 기본 장비 데이터를 준비한다.
  - 방법은 seed 함수, 초기 생성 스크립트, 또는 임시 장비 생성 API 중 하나로 후속 구현 단계에서 선택한다.

- [ ] **API-14. Health router 분리**
  - 루트 상태 확인 또는 `/health` 성격의 엔드포인트를 `routers/health.py`로 분리한다.

- [ ] **API-15. Comment 조건부 API 설계**
  - 처리 기록을 MVP에 포함하는 경우 `comments` 작성/조회 API를 별도 router/service로 구현한다.
  - Must-have 안정화 이후 진행한다.

## 5. 검증 작업

- [ ] **API-16. Swagger 기반 핵심 흐름 검증**
  - 이벤트 생성, 목록 조회, 상세 조회, 상태 변경을 Swagger에서 확인한다.

- [ ] **API-17. curl 기반 통합 흐름 검증**
  - 이미지 업로드 포함 이벤트 생성
  - 목록 조회
  - 상세 조회
  - 상태 변경
  - 재조회

- [ ] **API-18. DB 직접 확인**
  - PostgreSQL에서 `events`, `equipment`, `users`, `comments` 테이블과 저장 데이터를 확인한다.

## 6. Step 3 결론

API & Logic 작업은 `Event` 흐름을 최우선으로 한다.

먼저 `main.py`를 앱 조립 전용으로 정리하고, `events router -> event service -> model/storage` 흐름을 만든 뒤 Swagger와 curl로 MVP Critical Path를 검증한다.
