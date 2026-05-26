# Step 5. 에러 응답 정리

## 구현 목표

프론트엔드가 백엔드 오류를 일관되게 처리할 수 있도록 주요 에러 응답을 공통 구조로 정리한다.

## 공통 에러 형식

```json
{
  "error_code": "ERROR_CODE",
  "message": "사용자 또는 개발자가 이해할 수 있는 메시지",
  "detail": {}
}
```

## 적용 범위

- 이미지 형식 오류: `400`
- 이벤트 없음: `404`
- 필수 form 필드 누락: `422`
- FastAPI/Pydantic validation 오류: `422`
- YOLO 모델 파일 없음: `503`
- YOLO 추론 환경 문제: `503`

## 주요 에러 코드

| HTTP Status | error_code | 의미 |
| --- | --- | --- |
| `400` | `UNSUPPORTED_IMAGE_CONTENT_TYPE` | 허용되지 않은 이미지 content type |
| `400` | `UNSUPPORTED_IMAGE_EXTENSION` | 허용되지 않은 이미지 확장자 |
| `404` | `EVENT_NOT_FOUND` | 요청한 이벤트가 없음 |
| `422` | `REQUIRED_FORM_FIELD_MISSING` | 필수 form 필드 누락 |
| `422` | `VALIDATION_ERROR` | FastAPI/Pydantic 요청 검증 실패 |
| `503` | `YOLO_MODEL_NOT_FOUND` | 모델 파일 누락 |
| `503` | `YOLO_INFERENCE_UNAVAILABLE` | YOLO 추론 의존성/환경 문제 |

## 변경 파일

- `core/errors.py`
- `core/exception_handlers.py`
- `main.py`
- `routers/events.py`
- `services/event_service.py`
- `storage/image_storage.py`
