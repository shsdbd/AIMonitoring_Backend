# Step 4. 검증 방법 및 제약 사항 정의

## 1. 검증 방법

이번 작업은 모델 계층 구현이므로, 검증은 API 동작보다 SQLAlchemy metadata와 DB 테이블 생성 가능성에 집중한다.

## 2. 필수 검증 항목

| 검증 | 방법 | 기대 결과 |
| --- | --- | --- |
| Python import 검증 | `python -m compileall database.py models` | 문법 오류 없이 컴파일 |
| 모델 import 검증 | Python에서 `from models import User, Equipment, Event, Comment` 실행 | 4개 모델 import 성공 |
| DB metadata 검증 | `Base.metadata.tables.keys()` 확인 | `users`, `equipment`, `events`, `comments` 포함 |
| 테이블 생성 검증 | 개발 DB 초기화 후 앱 startup 또는 `init_db()` 실행 | 4개 테이블 생성 |
| 테이블 구조 확인 | PostgreSQL에서 `\d users`, `\d equipment`, `\d events`, `\d comments` | 설계서와 컬럼/제약 일치 |

## 3. 이번 작업에서 실행하지 않아도 되는 검증

| 검증 | 제외 이유 |
| --- | --- |
| `POST /api/v1/events` 성공 검증 | 스키마/API/service가 아직 정리되지 않았으므로 후속 티켓에서 수행한다. |
| Swagger 전체 흐름 검증 | 라우터 분리와 스키마 정리 후 수행한다. |
| curl 통합 검증 | API 계층 구현 후 수행한다. |

## 4. 제약 사항

| 제약 | 내용 |
| --- | --- |
| Pydantic 스키마 수정 금지 | 이번 티켓은 모델 계층만 다룬다. |
| FastAPI 라우터 수정 금지 | `main.py`와 router/API 수정은 후속 티켓이다. |
| Alembic 도입 금지 | 현재 프로젝트는 `create_all` 기반이므로 Alembic은 별도 결정 전까지 도입하지 않는다. |
| MVP 제외 범위 금지 | Detection, EventStatusHistory, Equipment 좌표, 복잡한 권한 모델을 추가하지 않는다. |
| 위경도 타입 준수 | latitude/longitude는 반드시 `Float` 계열로 유지한다. |
| user_id nullability 준수 | `events.user_id`는 반드시 nullable이어야 한다. |
| equipment_type 위치 준수 | 장비 종류는 `equipment.equipment_type`에만 둔다. |

## 5. 스타일 및 패턴

| 항목 | 기준 |
| --- | --- |
| SQLAlchemy 스타일 | 기존 코드의 SQLAlchemy 2.0 `Mapped`, `mapped_column` 스타일을 유지한다. |
| Base | 기존 `database.Base`를 사용한다. |
| 테이블명 | 복수형 또는 설계서 기준 이름을 그대로 따른다: `users`, `equipment`, `events`, `comments` |
| 제약 조건 이름 | 설계서의 이름을 최대한 맞춘다. |
| 불필요한 추상화 금지 | repository 패턴 등 새 추상화는 도입하지 않는다. |

## 6. Step 4 결론

이번 구현 지시서는 모델 계층 정합성을 검증하는 데 집중한다.

API가 아직 깨져 있을 수 있어도 이번 작업의 실패로 보지 않는다. API 복구는 후속 `Event schema/service/router` 티켓에서 처리한다.
