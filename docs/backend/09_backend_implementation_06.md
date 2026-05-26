# Step 6. 백엔드 API 사용법 가이드

## 1. 기본 정보

### EC2 Base URL

```text
http://3.27.181.100:8000
```

### Swagger

```text
http://3.27.181.100:8000/docs
```

### 공식 API prefix

```text
/api
```

### 호환 API prefix

기존 개발 경로와의 호환을 위해 `/api/v1` 경로도 유지한다.

```text
/api/v1
```

공식 연동은 `/api`를 기준으로 한다.

## 2. 전체 엔드포인트

| 기능 | Method | 공식 경로 | 호환 경로 |
| --- | --- | --- | --- |
| 서버 상태 확인 | `GET` | `/` | 없음 |
| 이벤트 목록 조회 | `GET` | `/api/events` | `/api/v1/events` |
| 이벤트 상세 조회 | `GET` | `/api/events/{event_id}` | `/api/v1/events/{event_id}` |
| 이벤트 상태 변경 | `PATCH` | `/api/events/{event_id}/status` | `/api/v1/events/{event_id}/status` |
| AI 탐지 이벤트 생성 | `POST` | `/api/events/detect` | `/api/v1/events/detect` |
| 정적 이미지 조회 | `GET` | `/static/images/...` | 없음 |

## 3. 이벤트 응답 형식

목록, 상세, 상태 변경, 탐지 생성 API는 프론트 `RoadkillEvent` 타입에 맞춰 응답한다.

```json
{
  "id": "2",
  "riskLevel": "즉시 확인",
  "detectedAt": "2026-05-26T11:22:10.338011Z",
  "location": "테스트영역",
  "objectType": "멧돼지",
  "status": "출동 요청",
  "description": "멧돼지 객체가 86% 신뢰도로 감지되었습니다.",
  "cameraId": "CCTV-001",
  "repeatDetection": true,
  "lastDetectedAt": "2026-05-26T11:29:05.008186Z",
  "imageUrl": "/static/images/2026/05/26/example.jpeg",
  "boundingBox": {
    "x": 37.240786,
    "y": 63.989122,
    "width": 26.300697,
    "height": 23.523227
  }
}
```

`imageUrl`은 상대경로다. 프론트에서는 백엔드 base URL을 붙여 사용한다.

```text
http://3.27.181.100:8000/static/images/...
```

## 4. 서버 상태 확인

### Request

```bash
curl http://3.27.181.100:8000/
```

### Response

```json
{
  "status": "running",
  "message": "도로 관제 시스템 백엔드 서버가 정상 가동 중입니다."
}
```

## 5. 이벤트 목록 조회

### Request

```bash
curl http://3.27.181.100:8000/api/events
```

### Response

```json
[
  {
    "id": "2",
    "riskLevel": "즉시 확인",
    "detectedAt": "2026-05-26T11:22:10.338011Z",
    "location": "테스트영역",
    "objectType": "멧돼지",
    "status": "출동 요청",
    "description": "멧돼지 객체가 86% 신뢰도로 감지되었습니다.",
    "cameraId": "CCTV-001",
    "repeatDetection": true,
    "lastDetectedAt": "2026-05-26T11:29:05.008186Z",
    "imageUrl": "/static/images/2026/05/26/example.jpeg",
    "boundingBox": {
      "x": 37.240786,
      "y": 63.989122,
      "width": 26.300697,
      "height": 23.523227
    }
  }
]
```

## 6. 이벤트 상세 조회

### Request

```bash
curl http://3.27.181.100:8000/api/events/2
```

### Response

`RoadkillEvent` 단일 객체를 반환한다.

존재하지 않는 이벤트는 `404 EVENT_NOT_FOUND`를 반환한다.

## 7. 이벤트 상태 변경

### Request

```bash
curl -X PATCH http://3.27.181.100:8000/api/events/2/status \
  -H "Content-Type: application/json" \
  -d '{"status":"DISPATCH_REQUESTED","comment":"현장 확인 요청"}'
```

### Request Body

```json
{
  "status": "DISPATCH_REQUESTED",
  "comment": "현장 확인 요청"
}
```

`status`는 영문 enum으로 보낸다.

| 요청 status | 응답 status |
| --- | --- |
| `UNCHECKED` | `미확인` |
| `CHECKING` | `확인 중` |
| `DISPATCH_REQUESTED` | `출동 요청` |
| `DISPATCHING` | `출동 중` |
| `COMPLETED` | `처리 완료` |
| `MISIDENTIFIED` | `오탐 처리` |

`comment`는 선택값이다. 값이 있으면 처리 기록으로 저장한다.

## 8. AI 탐지 이벤트 생성

### Swagger 사용법

Swagger에서 `POST /api/events/detect`를 열고 `Try it out`을 누른 뒤 아래 값을 입력한다.

| 필드 | 예시 | 설명 |
| --- | --- | --- |
| `camera_id` | `CCTV-001` | CCTV/장비 표시 식별자 |
| `latitude` | `37.5665` | 위도 |
| `longitude` | `126.9780` | 경도 |
| `location_name` | `테스트영역` | 프론트 `location` 표시값 |
| `image` | 이미지 파일 선택 | `png`, `jpg`, `jpeg` |

Swagger 테스트에서는 `camera_id`, `location_name`을 사용하면 된다. 프론트 또는 외부 클라이언트가 `cameraId`, `locationName`으로 보내는 요청도 백엔드가 호환 처리한다.

### curl 예시

```bash
curl -X POST http://3.27.181.100:8000/api/events/detect \
  -F camera_id=CCTV-001 \
  -F latitude=37.5665 \
  -F longitude=126.9780 \
  -F location_name=테스트영역 \
  -F image=@sample.jpeg
```

### 처리 방식

- 업로드 이미지는 `/static/images/{YYYY}/{MM}/{DD}/`에 저장된다.
- 백엔드가 내부 YOLO 모델 `best.pt`로 추론한다.
- 탐지 클래스는 `gorani`, `wild_boar`, `raccoon`이다.
- 응답의 `objectType`은 한글 표시명으로 변환된다.
- 탐지 객체가 없으면 빈 배열 `[]`를 반환한다.
- 한 이미지에서 여러 객체가 감지되면 여러 이벤트를 반환한다.
- 없는 `camera_id`는 `Equipment`로 자동 생성한다.

## 9. 반복 감지 테스트

반복 감지는 다음 조건을 만족하면 기존 이벤트를 갱신한다.

- 같은 `camera_id`
- 같은 `species`
- bbox 중심점 완전 동일
- 마지막 감지 이후 1분 이상 경과

테스트 방법:

1. `POST /api/events/detect`로 이미지 업로드
2. 1분 이상 대기
3. 같은 `camera_id`와 같은 이미지를 다시 업로드
4. 응답에서 `repeatDetection`, `riskLevel` 확인

격상 규칙:

| repeat_count | riskLevel |
| ---: | --- |
| `0` | `후순위 확인` |
| `1` | `순차 확인` |
| `2 이상` | `즉시 확인` |

## 10. 정적 이미지 조회

이벤트 응답의 `imageUrl`은 상대경로다.

```json
{
  "imageUrl": "/static/images/2026/05/26/example.jpeg"
}
```

브라우저나 프론트에서는 다음처럼 접근한다.

```text
http://3.27.181.100:8000/static/images/2026/05/26/example.jpeg
```

Docker 환경에서는 `/app/static/images`가 `static_images` 볼륨으로 마운트되어, 새로 업로드된 이미지는 컨테이너 재생성 후에도 유지된다.

## 11. 공통 에러 응답

주요 오류는 다음 형식을 사용한다.

```json
{
  "error_code": "ERROR_CODE",
  "message": "오류 메시지",
  "detail": {}
}
```

| HTTP Status | error_code | 의미 |
| --- | --- | --- |
| `400` | `UNSUPPORTED_IMAGE_CONTENT_TYPE` | 허용되지 않은 이미지 content type |
| `400` | `UNSUPPORTED_IMAGE_EXTENSION` | 허용되지 않은 이미지 확장자 |
| `404` | `EVENT_NOT_FOUND` | 요청한 이벤트가 없음 |
| `422` | `REQUIRED_FORM_FIELD_MISSING` | 필수 form 필드 누락 |
| `422` | `VALIDATION_ERROR` | 요청 검증 실패 |
| `503` | `YOLO_MODEL_NOT_FOUND` | YOLO 모델 파일 누락 |
| `503` | `YOLO_INFERENCE_UNAVAILABLE` | YOLO 추론 의존성/환경 문제 |

## 12. CORS

기본 허용 origin:

- `https://roadkill-detection.vercel.app`
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5174`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`

추가 origin은 `CORS_ORIGINS` 환경변수에 콤마 구분 문자열로 지정한다.

```text
CORS_ORIGINS=https://example.vercel.app,http://localhost:3001
```

## 13. 프론트 연동 주의사항

- 공식 API는 `/api` prefix를 사용한다.
- `/api/v1`은 개발 호환 경로로만 유지한다.
- `PATCH /status` 요청은 영문 enum을 보낸다.
- 응답의 `status`는 한글 표시값이다.
- 응답의 `imageUrl`은 상대경로이므로 프론트에서 백엔드 base URL을 붙인다.
- bbox는 0~100 퍼센트 좌표, 좌상단 기준이다.
- AI 모델 클래스에 없는 동물은 탐지되지 않거나 다른 클래스에 오인식될 수 있다.
