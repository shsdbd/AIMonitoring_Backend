# Step 3. 모듈별 책임 및 경계 정의

## 1. 경계 정의 목적

도메인별 모듈이 서로의 내부 구현을 직접 침범하지 않도록 책임과 참조 방향을 정의한다.

이 단계는 모듈 간 결합도를 낮추고, 후속 구현 단계에서 무분별한 순환 참조를 방지하기 위한 설계다.

## 2. 도메인 모듈 책임

| 모듈 | 책임 |
| --- | --- |
| `events` | AI 탐지 이벤트 등록, 이벤트 목록/상세 제공, 상태 변경, 오탐 구분 |
| `equipment` | 탐지 장비 식별 정보 관리, Event가 참조할 장비 존재성 제공 |
| `users` | 관제사/사용자 식별 정보 관리, Event와 Comment 작성자 참조 지원 |
| `comments` | 이벤트별 처리 기록 또는 확인 메모 관리 |
| `storage` | 이미지 파일 저장, 정적 URL 생성, 파일 형식 검증 |
| `core` | 설정, 공통 에러, 전역 예외 정책 |
| `dependencies` | DB 세션, 인증/인가, 공통 request dependency 제공 |

## 3. 레이어별 참조 규칙

| 호출 주체 | 참조 가능 | 참조 금지 |
| --- | --- | --- |
| `routers/` | `schemas`, `services`, `dependencies` | 다른 router의 내부 함수 직접 호출 |
| `services/` | `models`, `schemas` 일부, `storage`, `core.errors` | FastAPI `Request`/`Response` 직접 의존 |
| `models/` | `database.Base`, SQLAlchemy 공통 요소 | `routers`, `services`, `schemas` |
| `schemas/` | Pydantic, 표준 타입 | `models`, `routers`, `services` |
| `dependencies/` | `database`, `core`, 인증 관련 유틸 | 도메인 service의 비즈니스 로직 |
| `storage/` | 파일 시스템, 설정 | router 또는 DB 모델 |
| `core/` | 표준 라이브러리, 설정 | 도메인 모듈 |

## 4. 도메인 간 화이트리스트 참조

| 모듈 | 참조 가능한 도메인 | 이유 |
| --- | --- | --- |
| `event_service` | `Event`, `Equipment`, `User` | 이벤트 등록 시 장비 참조, 상태 변경 시 관제사 참조 가능 |
| `comment_service` | `Comment`, `Event`, `User` | 코멘트는 이벤트와 작성자에 연결됨 |
| `equipment_service` | `Equipment` | 장비 자체 책임만 관리 |
| `user_service` | `User` | 사용자 자체 책임만 관리 |

## 5. 금지할 참조 패턴

| 금지 패턴 | 이유 |
| --- | --- |
| `models`가 `schemas`를 import | 영속성 모델이 API 표현 계층에 의존하게 된다. |
| `services`가 `routers`를 import | 비즈니스 계층이 HTTP 계층에 종속된다. |
| `schemas`가 `models`를 import | 요청/응답 스키마가 DB 구현에 묶인다. |
| `event_service`가 `comment_service`를 직접 호출 | 이벤트 상태 변경과 코멘트 작성은 별도 유스케이스로 유지한다. |
| `main.py`에 도메인 로직 작성 | 앱 조립 지점이 다시 비대해진다. |

## 6. Event 중심 MVP 경계

MVP에서 `Event`는 중심 도메인이지만 모든 책임을 가져서는 안 된다.

| 책임 | 위치 |
| --- | --- |
| 이벤트 등록 요청 수신 | `routers/events.py` |
| 이벤트 등록 비즈니스 흐름 | `services/event_service.py` |
| 이미지 저장 | `storage/image_storage.py` |
| 이벤트 데이터 구조 | `models/event.py`, `schemas/event.py` |
| 상태값 검증 정책 | `schemas/event.py` 및 service validation |
| DB 세션 제공 | `dependencies/database.py` |
| 전역 오류 응답 | `core/exception_handlers.py` |

## 7. Step 3 결론

아키텍처 경계의 핵심은 HTTP 계층, 비즈니스 계층, 영속성 계층을 분리하는 것이다.

`Event`는 MVP의 중심 도메인이지만 이미지 저장, DB 세션, 전역 예외, 사용자/장비 관리 책임을 직접 소유하지 않는다.
