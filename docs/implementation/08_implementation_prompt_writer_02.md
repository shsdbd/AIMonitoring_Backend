# Step 2. 구현 목표 및 현재 상태 정의

## 1. 구현 목표

이번 구현 목표는 SQLAlchemy 모델 계층을 최종 데이터베이스 설계와 일치시키는 것이다.

구현 후에는 `users`, `equipment`, `events`, `comments` 4개 테이블이 SQLAlchemy metadata에 등록되어야 하며, `Base.metadata.create_all()` 기준으로 최종 DB 설계에 맞는 테이블 생성이 가능해야 한다.

## 2. 현재 코드 상태

현재 프로젝트에는 다음 파일만 존재한다.

```text
database.py
main.py
models/
├── __init__.py
└── event.py
schemas/
├── __init__.py
└── event.py
```

현재 `models/event.py`는 다음 문제를 가진다.

| 문제 | 영향 |
| --- | --- |
| `Event` 모델에 `user_id`가 없음 | `main.py`에서 `user_id=None` 전달 시 500 오류 발생 |
| `equipment_type`이 Event 직접 컬럼으로 존재 | 최종 DB 설계에서는 `equipment.equipment_type`으로 관리해야 함 |
| `equipment_id`가 문자열 | 최종 DB 설계에서는 `equipment.id`를 참조하는 정수 FK |
| bbox 필드 없음 | 프론트 강조 박스 요구사항 미충족 |
| priority 필드 없음 | MVP 우선순위 요구사항 미충족 |
| User/Equipment/Comment 모델 없음 | 최종 도메인/DB 설계와 불일치 |
| `init_db()`가 `models.event`만 import | 4개 모델 create_all 대상 누락 |

## 3. 반드시 유지할 기존 자산

| 자산 | 유지 방향 |
| --- | --- |
| `database.Base` | 모든 SQLAlchemy 모델은 기존 `Base`를 사용한다. |
| `database.SessionLocal` | 이번 작업에서는 변경하지 않는다. |
| `database.init_db()` | 함수는 유지하되 모든 모델을 import하도록 수정한다. |
| `main.py` | 이번 작업에서는 수정하지 않는다. API는 후속 티켓에서 정리한다. |
| `schemas/` | 이번 작업에서는 수정하지 않는다. 스키마는 후속 티켓에서 정리한다. |

## 4. 구현 후 기대 상태

- `models/user.py`가 존재한다.
- `models/equipment.py`가 존재한다.
- `models/event.py`가 최종 DB 설계 기준으로 정리된다.
- `models/comment.py`가 존재한다.
- `models/__init__.py`가 4개 모델을 export한다.
- `database.init_db()`가 4개 모델을 모두 import한다.
- SQLAlchemy metadata에 `users`, `equipment`, `events`, `comments` 테이블이 모두 등록된다.

## 5. Step 2 결론

현재 상태는 아키텍처/DB 설계와 코드 모델이 불일치한 상태다.

이번 구현은 API를 건드리지 않고 모델 계층 정합성만 먼저 맞추는 작업이다.
