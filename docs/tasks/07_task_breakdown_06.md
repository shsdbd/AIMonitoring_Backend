# Step 6. 최종 작업 백로그

## 1. 문서 목적

이 문서는 `task-breakdown` 단계의 최종 산출물이다.

앞서 확정된 요구사항, MVP 범위, 도메인 모델, 아키텍처, 데이터베이스 설계를 실제 구현 가능한 작은 작업 티켓으로 분해하고, 구현 순서를 정리한다.

## 2. 구현 원칙

| 원칙 | 내용 |
| --- | --- |
| MVP 우선 | Event 생성, 조회, 상세, 상태 변경 흐름을 가장 먼저 안정화한다. |
| 작은 티켓 | 한 티켓은 한 가지 목적만 가진다. |
| 계층 분리 | 모델, 스키마, 라우터, 서비스, 스토리지를 분리한다. |
| 제외 범위 준수 | Detection, EventStatusHistory, 통계, 복잡한 권한 관리는 티켓으로 만들지 않는다. |
| 기존 자산 보존 | CORS, static 마운트, 이미지 저장 정책, DB 연결 방식은 유지한다. |

## 3. 최종 구현 순서

- [ ] **T-01. 개발 DB 초기화 전략 결정 및 적용 준비**
  - 목표: 기존 DB와 새 설계 충돌을 방지한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: 볼륨 초기화 또는 마이그레이션 절차가 명확하다.

- [ ] **T-02. 모델 패키지 구조 정리**
  - 목표: `User`, `Equipment`, `Event`, `Comment` 모델 파일 구조를 준비한다.
  - 참조: `docs/domain/04_domain_modeling_06.md`
  - DoD: 4개 모델 파일과 import 전략이 정리된다.

- [ ] **T-03. User 모델 작성**
  - 목표: `users` 테이블 모델을 작성한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: `id`, `username`, `role`, `created_at`과 제약이 반영된다.

- [ ] **T-04. Equipment 모델 작성**
  - 목표: `equipment` 테이블 모델을 작성한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: `camera_id`, `equipment_type`, `location_name`, `status`와 제약이 반영된다.

- [ ] **T-05. Event 모델 재작성**
  - 목표: 기존 Event 모델을 최종 설계에 맞게 수정한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: `user_id`, `species`, bbox, priority, 반복 감지 필드, 정수 FK `equipment_id`가 반영되고 직접 `equipment_type` 컬럼은 제거된다.

- [ ] **T-06. Comment 모델 작성**
  - 목표: `comments` 테이블 모델을 작성한다.
  - 참조: `docs/domain/04_domain_modeling_06.md`
  - DoD: `event_id`, `user_id`, `content`, `created_at`과 제약이 반영된다.

- [ ] **T-07. 모델 FK/인덱스/초기화 import 정리**
  - 목표: FK, 삭제 정책, 주요 인덱스, `init_db()` import를 정리한다.
  - 참조: `docs/database/06_database_design_03.md`, `docs/database/06_database_design_04.md`
  - DoD: `create_all` 기준 4개 테이블과 주요 제약/인덱스가 반영된다.

- [ ] **T-08. Event 스키마 재정리**
  - 목표: Event 생성/조회/상태 변경 스키마를 최종 필드 기준으로 정리한다.
  - 참조: `docs/requirements/02_requirements_decomposition_11.md`
  - DoD: `species`, bbox, priority, nullable user_id, 반복 감지 필드, 6개 상태값 검증이 반영된다.

- [ ] **T-09. User/Equipment/Comment 스키마 작성**
  - 목표: 보조 도메인 기본 스키마를 작성한다.
  - 참조: `docs/domain/04_domain_modeling_06.md`
  - DoD: 각 도메인의 기본 응답 스키마가 준비된다.

- [ ] **T-10. 공통 DB dependency 분리**
  - 목표: `get_db`를 `dependencies/database.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_05.md`
  - DoD: router에서 공통 dependency를 사용할 수 있다.

- [ ] **T-11. 이미지 저장 모듈 분리**
  - 목표: 이미지 검증/저장/URL 생성을 `storage/image_storage.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_02.md`
  - DoD: 기존 날짜별 UUID 이미지 저장 정책이 유지된다.

- [ ] **T-12. 공통 에러 및 예외 처리 구조 도입**
  - 목표: 공통 비즈니스 에러와 전역 예외 응답 구조를 마련한다.
  - 참조: `docs/architecture/05_architecture_planning_04.md`
  - DoD: 주요 오류가 일관된 `error_code`, `message`, `detail` 구조로 응답 가능하다.

- [ ] **T-13. Event service 작성**
  - 목표: 이벤트 생성, 목록 조회, 상세 조회, 상태 변경 비즈니스 로직을 service로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: 라우터에 DB 쿼리/비즈니스 로직이 직접 남지 않고, 내부 Event 데이터를 프론트 `RoadkillEvent` 응답 형태로 변환할 수 있다. 응답에는 한글 `status`, `cameraId`, `repeatDetection`, `lastDetectedAt`이 포함된다.

- [ ] **T-13A. YOLO 추론 모듈 통합**
  - 목표: `ai_model`의 `best.pt`와 추론 로직을 백엔드 내부 AI 모듈로 분리 통합한다.
  - 참조: `ai_model/test.py`, `docs/contracts/09_frontend_api_contract_01.md`
  - DoD: 이미지 입력에 대해 `species`, `confidence`, 중심점 기준 bbox를 얻고, 이를 좌상단 기준 0~100 퍼센트 bbox로 변환할 수 있다. confidence threshold는 `0.3`, 모델은 `best.pt`를 사용한다.

- [ ] **T-13B. 반복 감지 및 priority 계산 서비스 작성**
  - 목표: 같은 `camera_id`에서 1분 이후 bbox 중심점이 완전히 동일한 객체가 다시 감지되는지 판단하고 Event에 반영한다.
  - 참조: `docs/decisions/DECISIONS.md`
  - DoD: 같은 `camera_id`, 같은 `species`, 1분 이상 간격, bbox 중심점 완전 동일 조건에서 기존 이벤트를 갱신한다. 최초 감지는 `repeat_count=0`, `priority=3`; 1회 반복 감지는 `repeat_count=1`, `priority=2`; 2회 이상 반복 감지는 `repeat_count>=2`, `priority=1`로 반영한다.

- [ ] **T-14. Event router 작성**
  - 목표: Event 엔드포인트를 `routers/events.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_02.md`
  - DoD: 공식 경로 `GET /api/events`, `GET /api/events/{eventId}`, `PATCH /api/events/{eventId}/status`가 동작한다. 상태 변경 요청은 `{ status, comment? }` 형태이며 `status`는 영문 enum으로 받는다.

- [ ] **T-15. Equipment 기준 데이터 준비**
  - 목표: 이벤트 생성 테스트에 필요한 기본 장비 데이터를 준비한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: 이벤트 생성 시 참조 가능한 장비 ID가 존재한다.

- [ ] **T-16. Health router 분리**
  - 목표: 서버 상태 확인 엔드포인트를 `routers/health.py`로 분리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: 기존 서버 정상 응답 의미가 유지된다.

- [ ] **T-17. main.py 앱 조립 구조 정리**
  - 목표: `main.py`를 앱 생성, CORS, static, 라우터 등록, startup 초기화 중심으로 정리한다.
  - 참조: `docs/architecture/05_architecture_planning_06.md`
  - DoD: `main.py`에 도메인 비즈니스 로직이 남지 않는다.

- [ ] **T-18. Swagger 핵심 흐름 검증**
  - 목표: Swagger에서 MVP Critical Path를 확인한다.
  - 참조: `docs/mvp/03_mvp_scope_planning_06.md`
  - DoD: 이벤트 생성, 목록, 상세, 상태 변경이 Swagger에서 검증된다.

- [ ] **T-19. curl 통합 흐름 검증**
  - 목표: 실제 HTTP 요청으로 MVP Critical Path를 검증한다.
  - 참조: `docs/database/06_database_design_06.md`
  - DoD: 생성 -> 목록 -> 상세 -> 상태 변경 -> 재조회가 성공한다.

- [ ] **T-20. PostgreSQL 직접 확인**
  - 목표: DB에 테이블과 데이터가 설계대로 저장되는지 확인한다.
  - 참조: `docs/database/06_database_design_05.md`
  - DoD: `users`, `equipment`, `events`, `comments` 테이블과 이벤트 데이터가 확인된다.

## 4. 조건부 백로그

- [ ] **OPT-01. Comment 작성/조회 API 구현**
  - 조건: 처리 기록 기능을 이번 MVP에 포함하기로 결정한 경우
  - DoD: 이벤트별 코멘트 작성과 조회가 가능하다.

- [ ] **OPT-02. 단순 AI 요청 검증 dependency 추가**
  - 조건: AI 요청 인증이 이번 MVP에 필요하다고 결정된 경우
  - DoD: 허가되지 않은 AI 요청을 거부할 수 있다.

- [ ] **OPT-03. 단순 관제사 접근 통제 추가**
  - 조건: 관제사 인증/인가를 이번 MVP에 포함하기로 결정한 경우
  - DoD: 허가된 사용자만 상태 변경/코멘트 작성이 가능하다.

## 5. 제외 백로그

다음 항목은 이번 MVP 작업 티켓으로 만들지 않는다.

- [ ] AI 모델 학습 구현
- [ ] 프론트엔드 화면 디자인 구현
- [ ] 통계/분석 대시보드
- [ ] 대규모 분산 처리/고가용성 구성
- [ ] 다중 객체 Detection 도메인
- [ ] EventStatusHistory 테이블
- [ ] Equipment 자체 지도 좌표
- [ ] 복잡한 역할/권한 관리
- [ ] 관리자용 사용자/장비 관리 고도화

## 6. 최종 결론

최종 작업 백로그는 Event 핵심 흐름 복구를 중심으로 한다.

우선순위는 `DB/Model 정합성 -> Schema -> 공통 인프라 -> Event service/router -> 검증` 순서다.

조건부 기능인 Comment, AI 요청 검증, 관제사 접근 통제는 Must-have 흐름이 안정화된 뒤 포함 여부를 결정한다.
