# Step 3. AI 탐지 이벤트 생성 API 및 YOLO 추론 모듈 구현

## 구현 목표

이미지를 업로드하면 백엔드가 내부 YOLO 모델을 실행하고, 탐지 결과를 `Event`로 저장한 뒤 프론트 `RoadkillEvent[]` 형식으로 반환하는 API를 추가한다.

## 변경 대상

- `ai/yolo_detector.py`
- `storage/image_storage.py`
- `routers/events.py`
- `services/event_service.py`
- `requirements.txt`

## 추가 API

```http
POST /api/events/detect
Content-Type: multipart/form-data
```

요청 필드:

- `cameraId`: 필수
- `latitude`: 필수
- `longitude`: 필수
- `locationName`: 선택
- `image`: 필수, `png`, `jpg`, `jpeg`

## 처리 방식

- `ai_model` 원본 파일은 수정하지 않는다.
- 백엔드 전용 `ai/yolo_detector.py`에서 `ai_model/runs/animal_detector_yolov8n/weights/best.pt`를 로드한다.
- confidence threshold는 `0.3`을 사용한다.
- YOLO의 `xyxy` 픽셀 좌표를 프론트 계약에 맞는 좌상단 기준 0~100 퍼센트 bbox로 변환한다.
- 없는 `cameraId`는 `Equipment`로 자동 생성한다.
- `locationName`이 없으면 `미지정 위치`로 저장한다.
- 한 이미지에서 여러 객체가 탐지되면 여러 `Event`를 생성하고 같은 `imageUrl`을 공유한다.
- 같은 장비, 같은 종, bbox 중심점 완전 동일, 1분 이상 간격이면 기존 이벤트를 반복 감지로 갱신한다.

## 주의 사항

- 실제 EC2/Docker 실행 환경에는 `ultralytics`와 그 하위 의존성이 설치되어야 한다.
- 모델 파일 `best.pt`가 배포 환경에 없으면 `/api/events/detect`는 `503`을 반환한다.
