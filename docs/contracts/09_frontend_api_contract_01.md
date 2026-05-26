# Frontend API Contract Patch 01

## 1. 문서 목적

이 문서는 프론트엔드 팀의 `RoadkillEvent` 타입 및 1차 연동 API 피드백을 반영하여, 백엔드 설계/구현 전에 확정하거나 보정해야 할 API 계약을 정리한다.

본 문서는 기존 기획/설계 산출물을 전면 대체하지 않고, `domain-modeling`, `database-design`, `task-breakdown`, `implementation-prompt-writer` 산출물에 반영할 패치 기준으로 사용한다.

## 2. 프론트엔드 현황

- 프론트엔드는 목업 기반 대시보드와 상세 화면을 구현했다.
- 프론트엔드는 화면 컴포넌트에서 기존 `RoadkillEvent` 타입을 유지한다.
- 백엔드는 API 응답 DTO에서 프론트 타입에 맞도록 데이터를 가공해서 내려준다.
- 프론트 배포 URL: `https://roadkill-detection.vercel.app/`
- 프론트 저장소: `https://github.com/haruby2357/Roadkill-Detection`

## 3. 확정 API 경로

공식 프론트 연동 API prefix는 `/api`로 둔다.

백엔드는 프론트 배포 URL `https://roadkill-detection.vercel.app`과 로컬 개발 URL(`localhost`, `127.0.0.1`)을 CORS 허용 origin으로 둔다. 추가 프론트 배포 URL이 생기면 `CORS_ORIGINS` 환경변수에 콤마 구분 문자열로 추가한다.

| 기능 | Method | Path |
| --- | --- | --- |
| 이벤트 목록 조회 | `GET` | `/api/events` |
| 이벤트 상세 조회 | `GET` | `/api/events/{eventId}` |
| 이벤트 상태 변경 | `PATCH` | `/api/events/{eventId}/status` |
| AI 탐지 이벤트 생성 | `POST` | `/api/events/detect` |
| 정적 이미지 조회 | `GET` | `/static/images/...` |

기존 프로토타입의 `/api/v1/events` 계열 경로는 초기 개발 산물이다. 구현 시 `/api/events`를 공식 경로로 맞추며, 필요하면 개발 기간 동안 `/api/v1/events`를 호환 라우트로 유지할 수 있다.

## 4. 프론트 응답 타입

프론트는 다음 `RoadkillEvent` 구조를 유지한다.

```ts
type RiskLevel = '즉시 확인' | '순차 확인' | '후순위 확인';

type EventStatus =
  | '미확인'
  | '확인 중'
  | '출동 요청'
  | '출동 중'
  | '처리 완료'
  | '오탐 처리';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface RoadkillEvent {
  id: string;
  riskLevel: RiskLevel;
  detectedAt: string;
  location: string;
  objectType: string;
  status: EventStatus;
  description: string;
  cameraId: string;
  repeatDetection: boolean;
  lastDetectedAt: string;
  imageUrl: string;
  boundingBox: BoundingBox;
}
```

백엔드는 내부 DB 컬럼명을 그대로 노출하지 않고, 응답 스키마에서 위 타입에 맞춰 변환한다.

## 5. 상태값 계약

백엔드 내부 상태 enum은 다음 6개를 지원한다.

| 내부 상태 | 프론트 표시 상태 |
| --- | --- |
| `UNCHECKED` | `미확인` |
| `CHECKING` | `확인 중` |
| `DISPATCH_REQUESTED` | `출동 요청` |
| `DISPATCHING` | `출동 중` |
| `COMPLETED` | `처리 완료` |
| `MISIDENTIFIED` | `오탐 처리` |

API 응답의 `RoadkillEvent.status`는 프론트 타입에 맞춰 반드시 한글 표시 상태로 내려준다.

상태 변경 요청 body의 `status`는 프론트가 한글 상태값을 백엔드 내부 영문 enum으로 변환해서 보낸다. 따라서 백엔드는 상태 변경 요청에서 영문 enum 문자열을 입력으로 받는다.

## 6. 상태 변경 요청

상태 변경 API는 다음 body를 사용한다.

```json
{
  "status": "DISPATCH_REQUESTED",
  "comment": "현장 확인 요청"
}
```

- `status`: 필수
- `comment`: 선택
- `comment`가 있으면 이벤트 처리 기록으로 저장하는 방향을 기본으로 한다.

## 7. priority / riskLevel 매핑

백엔드는 내부적으로 `priority`를 숫자로 저장하고, 프론트 응답에서는 `riskLevel`로 변환한다.

| priority | riskLevel |
| --- | --- |
| `1` | `즉시 확인` |
| `2` | `순차 확인` |
| `3` | `후순위 확인` |

## 8. location 계약

프론트 `RoadkillEvent.location`은 `Equipment.location_name`을 내려주는 방향으로 한다.

이벤트의 실제 좌표 정보인 `latitude`, `longitude`는 백엔드 내부 이벤트 위치 데이터로 유지한다. 프론트가 좌표 표시를 별도로 요구하면 후속 응답 필드 확장을 검토한다.

## 9. cameraId 계약

프론트 `RoadkillEvent.cameraId`를 안정적으로 제공하기 위해 `Equipment`에 표시용 장비 식별자 필드를 추가하는 방향으로 한다.

권장 컬럼명은 `equipment.camera_id`다.

`cameraId`는 최종 이벤트 목록/상세 응답 DTO에 반드시 포함한다.

## 10. imageUrl 계약

백엔드는 이미지 경로를 `/static/images/...` 상대경로로 내려준다.

프론트는 백엔드 origin을 붙여 실제 이미지 URL로 사용한다.

## 11. boundingBox 계약

프론트 `RoadkillEvent.boundingBox`는 다음 기준을 사용한다.

- 좌표 기준: 0~100 퍼센트 좌표
- 기준점: 박스 좌상단
- 형태: `{ x, y, width, height }`

백엔드 DB에는 `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`로 저장하고, API 응답에서 `boundingBox` 객체로 묶어서 내려준다.

## 12. 반복 감지 계약

`repeatDetection`과 `lastDetectedAt`은 백엔드가 이벤트 이력을 조회해 판단한다.

역할 분리는 다음과 같다.

| 파트 | 역할 |
| --- | --- |
| AI 모듈 | 이미지에서 객체, confidence, bbox를 탐지 |
| 백엔드 | 같은 `cameraId`, 같은 `species`, 같은 bbox 중심점의 객체가 1분 이상 간격으로 다시 감지되면 기존 이벤트를 갱신하고 `repeatDetection`, `lastDetectedAt`, `riskLevel` 응답을 갱신 |
| 프론트엔드 | 반복 감지 여부와 마지막 감지 시각 표시 |

이를 위해 `events.repeat_detection`, `events.repeat_count`, `events.last_detected_at` 필드를 추가하는 방향으로 한다.

priority 격상 규칙은 다음과 같다.

| 조건 | repeat_count | priority | riskLevel |
| --- | ---: | ---: | --- |
| 최초 감지 | 0 | 3 | `후순위 확인` |
| 1분 이상 뒤 같은 위치 반복 감지 1회 | 1 | 2 | `순차 확인` |
| 추가 1분 이상 뒤 같은 위치 반복 감지 2회 이상 | 2 이상 | 1 | `즉시 확인` |

`repeatDetection`, `lastDetectedAt`은 최종 이벤트 목록/상세 응답 DTO에 반드시 포함한다.

## 13. description 계약

프론트 `RoadkillEvent.description`은 1차 구현에서 별도 저장 컬럼 없이 백엔드 응답 DTO에서 생성할 수 있다.

예시:

```text
동물 사체가 92% 신뢰도로 감지되었습니다.
```

AI 또는 관제사가 작성한 설명 원문을 보존해야 하는 요구가 생기면 `events.description` 추가 또는 `comments` 활용 정책을 다시 결정한다.

## 14. AI 모델 통합 계약

AI 서버를 별도로 띄우지 않고, 전달받은 `ai_model` 폴더의 YOLOv8 추론 코드를 백엔드 내부 모듈로 통합한다.

- 사용 모델: `ai_model/runs/animal_detector_yolov8n/weights/best.pt`
- confidence threshold: `0.3`
- 탐지 클래스: `gorani`, `wild_boar`, `raccoon`
- 입력 이미지 형식: `png`, `jpeg/jpg`
- 저장 방식: `obstacle_type`은 `ANIMAL`, 세부 종은 `species`로 별도 저장
- 다중 객체: 한 이미지에서 여러 객체가 탐지되면 객체별로 여러 Event 생성
- 이미지 URL: 같은 이미지에서 파생된 Event들은 동일한 `imageUrl` 공유
- bbox 변환: `ai_model/test.py`의 중심점 기준 0~1 정규화 bbox를 좌상단 기준 0~100 퍼센트 좌표로 변환
- priority: 백엔드가 반복 감지 횟수 기준으로 산출

## 15. AI 탐지 이벤트 생성 API

`POST /api/events/detect`는 백엔드 내부 YOLO 모델을 실행해 이벤트를 생성한다.

요청 형식은 `multipart/form-data`다.

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `cameraId` | 필수 | CCTV/장비 표시 식별자 |
| `latitude` | 필수 | 탐지 위치 위도 |
| `longitude` | 필수 | 탐지 위치 경도 |
| `locationName` | 선택 | 프론트 `location`으로 내려줄 위치명 |
| `image` | 필수 | `png`, `jpg`, `jpeg` 이미지 |

Swagger 테스트 화면에서는 `camera_id`, `location_name`으로 표시되며, 프론트 요청의 `cameraId`, `locationName`도 호환 처리한다.

`cameraId`에 해당하는 장비가 없으면 백엔드가 `equipment` 데이터를 자동 생성한다.

- `equipment_type`: `CCTV`
- `location_name`: `locationName`이 있으면 해당 값, 없으면 `미지정 위치`
- `status`: `ACTIVE`

응답은 `RoadkillEvent[]`다. 한 이미지에서 여러 객체가 탐지되면 여러 이벤트가 생성될 수 있다. 탐지 객체가 없으면 빈 배열을 반환한다.

## 16. 공통 에러 응답

백엔드 주요 오류는 다음 형식을 사용한다.

```json
{
  "error_code": "ERROR_CODE",
  "message": "오류 메시지",
  "detail": {}
}
```

대표 에러 코드는 다음과 같다.

| HTTP Status | error_code | 의미 |
| --- | --- | --- |
| `400` | `UNSUPPORTED_IMAGE_CONTENT_TYPE` | 허용되지 않은 이미지 content type |
| `400` | `UNSUPPORTED_IMAGE_EXTENSION` | 허용되지 않은 이미지 확장자 |
| `404` | `EVENT_NOT_FOUND` | 요청한 이벤트가 없음 |
| `422` | `REQUIRED_FORM_FIELD_MISSING` | 필수 form 필드 누락 |
| `422` | `VALIDATION_ERROR` | 요청 검증 실패 |
| `503` | `YOLO_MODEL_NOT_FOUND` | YOLO 모델 파일 누락 |
| `503` | `YOLO_INFERENCE_UNAVAILABLE` | YOLO 추론 의존성/환경 문제 |
