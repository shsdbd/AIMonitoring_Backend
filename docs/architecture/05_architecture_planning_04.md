# Step 4. 공통 비즈니스 에러 및 전역 예외 처리 설계

## 1. 설계 목적

현재 코드는 각 라우터에서 `HTTPException`을 직접 발생시키는 단순 구조다.

MVP가 확장되면 이벤트 없음, 잘못된 상태값, 필수 데이터 부족, 파일 업로드 오류 등 공통 오류를 일관된 응답으로 처리해야 한다.

## 2. 에러 처리 원칙

| 원칙 | 설명 |
| --- | --- |
| 일관된 응답 형식 | 프론트엔드가 오류를 안정적으로 해석할 수 있어야 한다. |
| 도메인 오류와 HTTP 표현 분리 | service는 비즈니스 오류를 발생시키고, handler가 HTTP 응답으로 변환한다. |
| 사용자 메시지와 내부 원인 분리 | 사용자에게 필요한 메시지만 응답하고 내부 상세는 로그로 남긴다. |
| MVP 단순성 유지 | 과도한 오류 계층은 만들지 않고 필수 오류 유형만 정의한다. |

## 3. 공통 에러 응답 형식

```json
{
  "error_code": "EVENT_NOT_FOUND",
  "message": "해당 이벤트를 찾을 수 없습니다.",
  "detail": null
}
```

| 필드 | 의미 |
| --- | --- |
| `error_code` | 프론트엔드가 분기할 수 있는 안정적인 오류 코드 |
| `message` | 사용자 또는 개발자가 이해할 수 있는 오류 설명 |
| `detail` | 선택적 상세 정보. MVP에서는 최소화 |

## 4. 비즈니스 에러 후보

| 에러 코드 | HTTP 상태 | 발생 상황 |
| --- | --- | --- |
| `EVENT_NOT_FOUND` | 404 | 요청한 이벤트가 존재하지 않음 |
| `EQUIPMENT_NOT_FOUND` | 404 | 이벤트 등록 시 참조 장비가 존재하지 않음 |
| `USER_NOT_FOUND` | 404 | 담당자 또는 코멘트 작성자 참조가 존재하지 않음 |
| `COMMENT_NOT_FOUND` | 404 | 요청한 코멘트가 존재하지 않음 |
| `INVALID_EVENT_STATUS` | 400 | 허용되지 않은 이벤트 상태값 |
| `INVALID_EVENT_PAYLOAD` | 422 | AI 탐지 이벤트 필수 정보 부족 또는 형식 오류 |
| `INVALID_IMAGE_FILE` | 400 | 업로드 파일이 이미지가 아니거나 허용되지 않는 형식 |
| `UNAUTHORIZED_AI_SOURCE` | 401 | 허가되지 않은 AI 모듈 요청 |
| `FORBIDDEN_OPERATOR_ACTION` | 403 | 권한 없는 관제 기능 접근 |

## 5. 예외 처리 모듈 배치

```text
core/
├── errors.py
└── exception_handlers.py
```

| 파일 | 책임 |
| --- | --- |
| `core/errors.py` | 공통 비즈니스 예외 클래스와 error_code 정의 |
| `core/exception_handlers.py` | FastAPI 전역 exception handler 등록 함수 정의 |

## 6. 계층별 오류 처리 책임

| 계층 | 책임 |
| --- | --- |
| `routers/` | 요청을 service로 넘기고 정상 응답 스키마를 반환한다. |
| `services/` | 비즈니스 규칙 위반 시 도메인 예외를 발생시킨다. |
| `storage/` | 이미지 형식/저장 실패 등 파일 관련 예외를 발생시킨다. |
| `core/exception_handlers.py` | 도메인 예외를 표준 HTTP 응답으로 변환한다. |
| FastAPI/Pydantic | 기본 요청 검증 오류를 처리한다. |

## 7. MVP 우선 적용 범위

| 우선순위 | 에러 |
| --- | --- |
| 1 | `EVENT_NOT_FOUND` |
| 2 | `INVALID_EVENT_STATUS` |
| 3 | `INVALID_EVENT_PAYLOAD` |
| 4 | `INVALID_IMAGE_FILE` |
| 5 | `EQUIPMENT_NOT_FOUND` |

인증 관련 오류는 접근 통제 기능을 MVP에 포함하는 경우 추가한다.

## 8. Step 4 결론

전역 예외 처리는 MVP에서 프론트엔드 연동 안정성을 높이기 위한 공통 기반이다.

라우터는 `HTTPException` 직접 사용을 최소화하고, service/storage 계층에서 발생한 도메인 오류를 전역 핸들러가 일관된 응답으로 변환하는 구조를 지향한다.
