# Step 5. 티켓 명세화

## 1. 티켓 명세 기준

각 티켓은 한 번에 하나의 구현 목적만 갖도록 작게 나눈다.

각 티켓에는 목표, 참조 문서, 완료 기준(DoD)을 명시한다.

## 2. DB & Model 티켓

- [ ] **DBM-01. 모델 패키지 구조 정리**
  - 목표: `models/`를 User, Equipment, Event, Comment 모델을 수용할 수 있는 구조로 정리한다.
  - 참조: `docs/domain/04_domain_modeling_06.md`, `docs/database/06_database_design_06.md`
  - DoD: 4개 도메인 모델 파일 구조와 import 전략이 마련된다.

- [ ] **DBM-02. User 모델 작성**
  - 목표: `users` 테이블 설계를 모델로 반영한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: `id`, `username`, `role`, `created_at`, unique/check/default 정책이 반영된다.

- [ ] **DBM-03. Equipment 모델 작성**
  - 목표: `equipment` 테이블 설계를 모델로 반영한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: `equipment_type`, `location_name`, `status`와 check/default 정책이 반영된다.

- [ ] **DBM-04. Event 모델 재작성**
  - 목표: 기존 `Event` 모델을 최종 DB 설계 기준으로 수정한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: `user_id`, bbox, priority가 추가되고 `equipment_id`가 정수 FK로 정리되며 `equipment_type` 직접 컬럼은 제거된다.

- [ ] **DBM-05. Comment 모델 작성**
  - 목표: `comments` 테이블 설계를 모델로 반영한다.
  - 참조: `docs/domain/04_domain_modeling_06.md`, `docs/database/06_database_design_06.md`
  - DoD: `event_id`, `user_id`, `content`, `created_at`과 FK/check 정책이 반영된다.

- [ ] **DBM-06. 모델 관계/FK/인덱스 정리**
  - 목표: FK, 삭제 정책, 인덱스를 DB 설계와 맞춘다.
  - 참조: `docs/database/06_database_design_03.md`, `docs/database/06_database_design_04.md`
  - DoD: FK 정책과 주요 인덱스가 모델 또는 마이그레이션 전략에 반영된다.

- [ ] **DBM-07. DB 초기화 import 정리**
  - 목표: `init_db()`가 모든 모델을 인식하도록 정리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: `create_all` 실행 시 4개 테이블이 생성 대상에 포함된다.

- [ ] **DBM-08. 개발 DB 초기화 전략 실행 준비**
  - 목표: 기존 테이블과 새 설계 충돌을 피할 개발 환경 초기화 절차를 준비한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: 볼륨 초기화 또는 마이그레이션 중 하나의 절차가 명확해진다.

## 3. Schema 티켓

- [ ] **SCH-01. Event 요청/응답 스키마 재정리**
  - 목표: Event 생성/조회/상태 변경 스키마를 MVP 필드에 맞춘다.
  - 참조: `docs/requirements/02_requirements_decomposition_11.md`, `docs/database/06_database_design_06.md`
  - DoD: bbox, priority, nullable user_id, status 값이 스키마에 반영된다.

- [ ] **SCH-02. User/Equipment/Comment 스키마 작성**
  - 목표: 보조 도메인의 기본 요청/응답 스키마를 작성한다.
  - 참조: `docs/domain/04_domain_modeling_06.md`
  - DoD: 각 도메인 조회/생성에 필요한 최소 스키마가 정의된다.

## 4. API & Service 티켓

- [ ] **API-01. 공통 DB dependency 분리**
  - 목표: `get_db`를 `dependencies/database.py`로 이동한다.
  - 참조: `docs/architecture/05_architecture_planning_05.md`
  - DoD: 라우터에서 공통 `get_db`를 import해 사용할 수 있다.

- [ ] **API-02. 이미지 저장 모듈 분리**
  - 목표: 이미지 검증/저장/URL 생성 책임을 `storage/image_storage.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_02.md`
  - DoD: 기존 `/static/images/{YYYY}/{MM}/{DD}/` 저장 정책이 유지된다.

- [ ] **API-03. 공통 에러와 전역 예외 처리 도입**
  - 목표: 공통 비즈니스 오류와 표준 오류 응답 구조를 마련한다.
  - 참조: `docs/architecture/05_architecture_planning_04.md`
  - DoD: Event not found, invalid status, invalid payload, invalid image 오류를 일관된 구조로 처리할 수 있다.

- [ ] **API-04. Event service 작성**
  - 목표: 이벤트 생성, 목록 조회, 상세 조회, 상태 변경 로직을 service 계층으로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: 라우터에 DB 쿼리와 비즈니스 로직이 직접 남지 않는다.

- [ ] **API-05. Event router 작성**
  - 목표: Event 관련 엔드포인트를 `routers/events.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_02.md`
  - DoD: 생성, 목록, 상세, 상태 변경 라우트가 router에 모인다.

- [ ] **API-06. Equipment 기준 데이터 준비**
  - 목표: Event 생성에 필요한 기본 장비 데이터를 준비한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: 테스트 이벤트 생성 시 참조 가능한 장비 ID가 존재한다.

- [ ] **API-07. Health router 분리**
  - 목표: 서버 상태 확인 엔드포인트를 `routers/health.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: 루트 또는 health 엔드포인트가 기존 메시지 의미를 유지한다.

- [ ] **API-08. main.py 앱 조립 구조 정리**
  - 목표: `main.py`를 앱 생성, 미들웨어, static, 라우터 등록 중심으로 정리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: `main.py`에 도메인 비즈니스 로직이 남지 않는다.

## 5. 검증 티켓

- [ ] **TST-01. Swagger 핵심 흐름 검증**
  - 목표: Swagger에서 이벤트 생성, 목록, 상세, 상태 변경 흐름을 확인한다.
  - 참조: `docs/mvp/03_mvp_scope_planning_06.md`
  - DoD: MVP Critical Path가 Swagger로 검증된다.

- [ ] **TST-02. curl 통합 흐름 검증**
  - 목표: 실제 multipart 요청으로 이벤트 생성과 상태 변경 흐름을 검증한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: 생성 -> 목록 -> 상세 -> 상태 변경 -> 재조회가 성공한다.

- [ ] **TST-03. DB 직접 확인**
  - 목표: PostgreSQL에서 테이블과 저장 데이터를 확인한다.
  - 참조: `docs/database/06_database_design_05.md`
  - DoD: `users`, `equipment`, `events`, `comments` 테이블과 이벤트 데이터가 확인된다.

## 6. 조건부 티켓

- [ ] **OPT-01. Comment 작성/조회 API 구현**
  - 목표: 처리 기록 기능을 MVP에 포함하기로 결정되면 Comment API를 구현한다.
  - 참조: `docs/requirements/02_requirements_decomposition_11.md`
  - DoD: 이벤트별 코멘트 작성과 조회가 가능하다.

- [ ] **OPT-02. 단순 AI 요청 검증 dependency 추가**
  - 목표: AI 요청 신뢰성 확인이 필요할 경우 최소 검증 dependency를 추가한다.
  - 참조: `docs/architecture/05_architecture_planning_05.md`
  - DoD: 허가되지 않은 AI 요청을 거부할 수 있다.

## 7. Step 5 결론

최종 티켓은 DB/Model, Schema, API/Service, 검증, 조건부 기능으로 분류한다.

Must-have 티켓은 Event 핵심 흐름 복구에 집중하고, Comment와 AI 검증은 조건부 티켓으로 둔다.
