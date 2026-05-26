# Step 7. 테스트 코드 작성

## 테스트 목표

백엔드 핵심 흐름이 실제 HTTP 레벨에서 동작하는지 확인한다.

## 추가 파일

- `tests/test_backend_api.py`

## 추가 의존성

- `httpx==0.27.0`

## 테스트 범위

- `GET /`
- `GET /api/events`
- `GET /api/v1/events`
- `GET /api/events/{event_id}`
- `PATCH /api/events/{event_id}/status`
- `POST /api/events/detect`
- 표준 에러 응답 형식
- 반복 감지 갱신
- 상태 변경 시 Comment 저장

## 검증 방식

- `unittest` 기반 통합 테스트
- 임시 SQLite DB 사용
- YOLO 추론은 mock 처리
- 이미지 저장은 mock 처리

## 검증 결과

- 테스트 4개 모두 통과
- 공통 에러 응답 형식 확인
- detect API 생성/반복 감지 확인
- status 변경 및 Comment 생성 확인
