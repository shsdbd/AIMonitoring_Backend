# Step 1. 설계 산출물 검토

## 1. 검토 목적

이 단계는 지금까지 확정된 요구사항, MVP 범위, 도메인 모델, 아키텍처, 데이터베이스 설계를 종합하여 실제 구현이 필요한 에픽과 기능 모듈을 식별한다.

이 문서는 작업 분해의 입력 검토이며, 실제 코드는 작성하지 않는다.

## 2. 입력 산출물

| 문서 | 사용 목적 |
| --- | --- |
| `docs/requirements/02_requirements_decomposition_11.md` | 관제사 시나리오와 기능/비기능 요구사항 확인 |
| `docs/mvp/03_mvp_scope_planning_06.md` | MVP 포함/조건부 포함/제외 범위 확인 |
| `docs/domain/04_domain_modeling_06.md` | User, Equipment, Event, Comment 도메인 확인 |
| `docs/architecture/05_architecture_planning_06.md` | FastAPI 계층 구조와 모듈 경계 확인 |
| `docs/database/06_database_design_06.md` | 물리 테이블, 컬럼, FK, 제약 조건, 인덱스 확인 |
| `.agent/skills/context_packet.md` | 현재 코드 상태와 진행 단계 확인 |

## 3. 구현 대상 에픽

| Epic ID | 에픽 | 설명 | MVP 우선순위 |
| --- | --- | --- | --- |
| E-01 | 프로젝트 구조 재정리 | `main.py` 중심 구조를 계층형 FastAPI 구조로 분리 | Must-have |
| E-02 | DB 모델 정합성 복구 | `users`, `equipment`, `events`, `comments` 모델을 DB 설계에 맞게 정리 | Must-have |
| E-03 | Pydantic 스키마 정리 | 요청/응답 스키마를 MVP 필드와 DB 설계에 맞게 정리 | Must-have |
| E-04 | Event 핵심 API 구현 | AI 이벤트 등록, 목록 조회, 상세 조회, 상태 변경 | Must-have |
| E-05 | 이미지 저장 책임 분리 | 이미지 저장/검증/URL 생성 로직을 `storage` 계층으로 분리 | Must-have |
| E-06 | 공통 DI 및 DB 세션 분리 | `get_db`를 공통 dependency로 분리 | Must-have |
| E-07 | 공통 에러 처리 | 이벤트 없음, 잘못된 상태값, 잘못된 이미지 등 공통 오류 체계 정리 | Must-have |
| E-08 | 기준 데이터 준비 | 이벤트 생성 전 필요한 기본 장비/사용자 데이터 준비 방식 마련 | Must-have |
| E-09 | Comment 조건부 기능 | 처리 기록 작성/조회 기능 | Should-have |
| E-10 | 단순 검증 및 시연 안정화 | 핵심 API 흐름 검증과 Swagger/curl 시연 정리 | Must-have |

## 4. MVP에서 티켓으로 만들지 않을 항목

| 제외 항목 | 이유 |
| --- | --- |
| AI 모델 학습/추론 구현 | AI 파트 책임 |
| 프론트엔드 화면 디자인 구현 | 프론트엔드 파트 책임 |
| 통계/분석 대시보드 | MVP 제외 범위 |
| 대규모 분산 처리/고가용성 | MVP 제외 범위 |
| 다중 객체 Detection 도메인 | MVP 제외 범위 |
| EventStatusHistory 테이블 | MVP 제외 범위 |
| Equipment 자체 지도 좌표 | MVP 제외 범위 |
| 복잡한 권한/역할 관리 | MVP 제외 범위 |
| 관리자용 사용자/장비 관리 고도화 | MVP 제외 범위 |

## 5. 현재 코드 기준 주요 구현 리스크

| 리스크 | 영향 | 대응 방향 |
| --- | --- | --- |
| `Event` 모델과 API 입력/응답 불일치 | `POST /api/v1/events`가 500 오류 발생 | 모델/스키마/서비스를 DB 설계 기준으로 재정렬 |
| `main.py` 책임 과다 | 기능 확장 시 유지보수 어려움 | 라우터, 서비스, 스토리지, dependency로 분리 |
| `User`, `Equipment`, `Comment` 미구현 | 도메인/DB 설계와 코드 불일치 | 모델/스키마부터 작은 티켓으로 추가 |
| 장비 기준 데이터 없음 | FK 설계 후 이벤트 생성 실패 가능 | 기본 장비 seed 또는 사전 생성 티켓 필요 |
| AI/프론트 연계 형식 미정 | API 입력 형식이 바뀔 수 있음 | MVP는 현재 파일 업로드 기반 흐름을 유지하되 변경 가능 지점 명시 |

## 6. Step 1 결론

구현 백로그는 `Event` 핵심 흐름 복구를 중심으로 구성한다.

가장 먼저 계층 구조와 DB 모델 정합성을 맞추고, 그 다음 Event 생성/조회/상태 변경 API를 서비스 계층으로 분리한다.

Comment, 인증, AI 요청 검증은 조건부 또는 후순위 티켓으로 둔다.
