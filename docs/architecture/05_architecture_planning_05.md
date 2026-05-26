# Step 5. 의존성 주입(DI) 인프라 설계

## 1. 설계 목적

FastAPI의 `Depends` 패턴을 사용해 DB 세션, 인증 정보, 공통 리소스를 라우터에 주입한다.

현재 `main.py`에 있는 `get_db`는 여러 라우터에서 재사용 가능하도록 별도 dependency 모듈로 분리하는 방향으로 설계한다.

## 2. DI 모듈 구조

```text
dependencies/
├── __init__.py
├── database.py
└── auth.py
```

| 파일 | 책임 |
| --- | --- |
| `dependencies/database.py` | DB 세션 생성/종료 dependency 제공 |
| `dependencies/auth.py` | 관제사 인증, AI 모듈 인증 dependency 제공 |

## 3. DB 세션 Dependency

| 항목 | 설계 |
| --- | --- |
| 이름 | `get_db` |
| 위치 | `dependencies/database.py` |
| 책임 | 요청 단위 DB 세션을 생성하고 요청 종료 후 닫는다. |
| 사용 위치 | 모든 router에서 DB 접근이 필요한 service 호출 시 사용 |
| 보존 사항 | 현재 `SessionLocal` 기반 세션 생성/종료 흐름을 유지한다. |

## 4. 인증/인가 Dependency

인증 방식은 아직 미정이므로 설계상 확장 지점만 둔다.

| Dependency | 목적 | MVP 상태 |
| --- | --- | --- |
| `get_current_user` | 관제사 기능 접근자 식별 | 조건부 포함 |
| `require_operator` | 관제사 권한 확인 | 조건부 포함 |
| `verify_ai_source` | AI 이벤트 등록 요청 신뢰성 확인 | 조건부 포함 |

## 5. Router에서의 DI 사용 원칙

| 원칙 | 설명 |
| --- | --- |
| Router는 dependency만 선언 | DB 세션 생성/종료를 직접 하지 않는다. |
| Service는 필요한 리소스를 인자로 받음 | FastAPI에 직접 의존하지 않도록 한다. |
| 인증 미정 기능은 stub 가능 | MVP에서는 단순 통과 dependency로 시작 가능하다. |
| DB 세션은 요청 단위 | 요청이 끝나면 반드시 세션이 닫혀야 한다. |

## 6. DI 흐름

```text
HTTP Request
  ↓
FastAPI Router
  ↓ Depends(get_db), Depends(get_current_user)
Service Function
  ↓
SQLAlchemy Session / Domain Models
```

AI 이벤트 등록 흐름:

```text
AI Request
  ↓
events router
  ↓ Depends(get_db), optional Depends(verify_ai_source)
event_service
  ↓
storage + models
```

## 7. Startup/Shutdown 인프라

| 항목 | 설계 |
| --- | --- |
| DB 초기화 | 기존 `init_db()` 호출 흐름은 보존하되 앱 초기화 책임으로 유지한다. |
| static 디렉터리 생성 | 앱 시작 또는 storage 모듈 초기화에서 보장한다. |
| static 마운트 | `main.py`에서 `/static` 마운트를 유지한다. |

## 8. Step 5 결론

DI 설계의 핵심은 `get_db`를 `main.py`에서 분리하고, 인증/AI 검증 dependency를 후속 확장 지점으로 마련하는 것이다.

MVP에서는 DB 세션 dependency를 우선 안정화하고, 인증 관련 dependency는 조건부 포함 범위에 맞춰 최소 수준으로 설계한다.
