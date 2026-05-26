# Step 2. 기존 코드베이스 영향도 분석

## 현재 영향

DB/Model 정합성 1차 구현으로 `Event` 모델이 최종 설계 기준에 맞게 바뀌었다.

그 결과 기존 `main.py`와 `schemas/event.py`는 더 이상 현재 모델과 직접 맞지 않는다.

## 충돌 지점

- 기존 `main.py`의 `POST /api/v1/events`는 `species`, bbox, `priority`, 정수 FK 기반 `equipment_id`를 채우지 못한다.
- 기존 `schemas/event.py`의 `EventRead`는 프론트 `RoadkillEvent` 응답 타입과 다르다.
- 기존 상태 변경 API는 `DISPATCH_REQUESTED`, `DISPATCHING` 상태를 허용하지 않는다.
- 기존 공식 API 경로는 `/api/v1/events`였지만, 프론트 연동 공식 경로는 `/api/events`다.
- `cameraId`, `location`, `riskLevel`, `repeatDetection`, `lastDetectedAt`, `boundingBox`는 DB 컬럼을 그대로 반환해서는 만들 수 없고, `Event`와 `Equipment`를 조합해 응답 DTO로 변환해야 한다.

## 다음 구현 방향

- `schemas/event.py`를 프론트 `RoadkillEvent` 계약에 맞게 재정리한다.
- DB 세션 dependency를 `dependencies/database.py`로 분리한다.
- 이벤트 조회/상태 변경 로직을 `services/event_service.py`에 둔다.
- 공식 프론트 연동 경로 `GET /api/events`, `GET /api/events/{eventId}`, `PATCH /api/events/{eventId}/status`를 `routers/events.py`에 구현한다.
- `main.py`는 앱 생성, CORS, static mount, 라우터 등록, startup 초기화만 담당하도록 정리한다.

## 이번 단계에서 아직 하지 않는 일

- `ai_model` 원본 수정
- YOLO 모델 로드 및 이미지 추론
- AI 탐지 이벤트 생성 API
- 실제 반복 감지 계산 서비스
- 관리자/관제사 인증
