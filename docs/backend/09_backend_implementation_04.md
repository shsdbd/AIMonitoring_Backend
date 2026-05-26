# Step 4. CORS 설정 정리

## 구현 목표

프론트엔드 배포 URL과 로컬 개발 URL에서 백엔드 API를 안정적으로 호출할 수 있도록 CORS 설정을 명시적으로 정리한다.

## 변경 내용

- `main.py`의 `allow_origins=["*"]`를 명시적 origin 목록으로 변경했다.
- 기본 허용 origin:
  - `https://roadkill-detection.vercel.app`
  - `http://localhost:3000`
  - `http://localhost:5173`
  - `http://localhost:5174`
  - `http://127.0.0.1:3000`
  - `http://127.0.0.1:5173`
  - `http://127.0.0.1:5174`
- 추가 origin이 필요하면 `CORS_ORIGINS` 환경변수에 콤마 구분 문자열로 지정할 수 있게 했다.

## 기대 효과

- 프론트 Vercel 배포본에서 `GET /api/events`, `GET /api/events/{eventId}`, `PATCH /api/events/{eventId}/status` 호출 시 브라우저 CORS 차단 가능성을 줄인다.
- 향후 프론트 배포 URL이 바뀌어도 코드 수정 없이 환경변수로 허용 origin을 확장할 수 있다.
