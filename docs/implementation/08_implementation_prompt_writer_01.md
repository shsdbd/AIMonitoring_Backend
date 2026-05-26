# Step 1. 작업 티켓 분석

## 1. 대상 티켓

이번 구현 지시서의 대상은 최종 작업 백로그의 다음 티켓 묶음이다.

| 티켓 | 이름 | 포함 이유 |
| --- | --- | --- |
| T-02 | 모델 패키지 구조 정리 | 4개 도메인 모델 파일 구조가 선행되어야 한다. |
| T-03 | User 모델 작성 | Event와 Comment의 FK 대상이다. |
| T-04 | Equipment 모델 작성 | Event의 필수 FK 대상이다. |
| T-05 | Event 모델 재작성 | 현재 POST 500 오류의 핵심 원인과 직접 연결된다. |
| T-06 | Comment 모델 작성 | 확정 도메인 모델에 포함된 처리 기록 도메인이다. |
| T-07 | 모델 FK/인덱스/초기화 import 정리 | 4개 모델이 DB 초기화와 참조 무결성에 반영되어야 한다. |

## 2. 묶음 처리 이유

원칙적으로 티켓은 작게 유지해야 하지만, 이번 묶음은 FK 관계로 강하게 연결되어 있다.

`Event`는 `User`, `Equipment`를 참조하고, `Comment`는 `User`, `Event`를 참조한다. 따라서 개별 모델을 따로 구현하면 중간 상태에서 참조 오류와 초기화 누락이 발생하기 쉽다.

이번 지시서는 “DB/Model 정합성 1차 구현”으로 묶되, API 라우터/서비스/스키마 구현은 포함하지 않는다.

## 3. 참조 설계 문서

| 문서 | 사용 목적 |
| --- | --- |
| `docs/domain/04_domain_modeling_06.md` | 최종 엔티티와 관계 확인 |
| `docs/database/06_database_design_06.md` | 물리 테이블, 컬럼, FK, 제약, 인덱스 확인 |
| `docs/architecture/05_architecture_planning_06.md` | 계층 구조와 모듈 경계 확인 |
| `docs/tasks/07_task_breakdown_06.md` | 최종 작업 순서와 티켓 범위 확인 |
| `.agent/skills/context_packet.md` | 최신 결정 사항과 코드 상태 확인 |

## 4. 구현 범위에 포함되는 것

- `models/` 패키지 구조 정리
- `models/user.py` 작성
- `models/equipment.py` 작성
- `models/event.py` 재작성
- `models/comment.py` 작성
- `models/__init__.py` 정리
- `database.py`의 `init_db()` 모델 import 범위 정리
- SQLAlchemy 모델 레벨의 컬럼, FK, CheckConstraint, Index 반영

## 5. 구현 범위에서 제외되는 것

- FastAPI 라우터 구현
- 서비스 계층 구현
- Pydantic 스키마 구현
- API 요청/응답 변경
- 이미지 저장 모듈 분리
- 인증/인가 구현
- Comment API 구현
- Alembic 도입
- 실제 DB 볼륨 삭제 또는 마이그레이션 실행

## 6. Step 1 결론

이번 구현 지시서는 모델 계층만 최종 DB 설계와 맞추는 데 집중한다.

목표는 현재 `Event` 단일 모델 중심 구조를 `User`, `Equipment`, `Event`, `Comment` 4개 모델 구조로 확장하고, 기존 POST 500 오류의 근본 원인인 `Event` 모델 불일치를 해결할 기반을 마련하는 것이다.
