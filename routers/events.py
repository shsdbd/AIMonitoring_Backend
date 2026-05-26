from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from sqlalchemy.orm import Session

from ai.yolo_detector import YoloDetector
from core.errors import service_unavailable, unprocessable_entity
from dependencies.database import get_db
from schemas.event import CommentCreate, CommentRead, EventStatusUpdate, RoadkillEvent
from storage.image_storage import save_upload_image
from services.event_service import (
    create_event_comment,
    create_detected_events,
    get_event,
    list_event_comments,
    list_events,
    update_event_status,
)


router = APIRouter(prefix="/api/events", tags=["events"])
compat_router = APIRouter(prefix="/api/v1/events", tags=["events-compat"])
detector = YoloDetector()


def read_events(db: Session = Depends(get_db)) -> list[RoadkillEvent]:
    return list_events(db)


async def detect_events(
    request: Request,
    camera_id: str | None = Form(default=None),
    latitude: float = Form(..., ge=-90.0, le=90.0),
    longitude: float = Form(..., ge=-180.0, le=180.0),
    location_name: str | None = Form(default=None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> list[RoadkillEvent]:
    form = await request.form()
    resolved_camera_id = _required_form_value(
        field_name="cameraId",
        value=_first_form_value(form.get("cameraId"), camera_id),
    )
    resolved_location_name = _first_form_value(form.get("locationName"), location_name)

    image_path, image_url = await save_upload_image(image)

    try:
        detected_objects = detector.detect(image_path)
    except FileNotFoundError as exc:
        raise service_unavailable(
            error_code="YOLO_MODEL_NOT_FOUND",
            message="YOLO 모델 파일을 찾을 수 없습니다.",
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise service_unavailable(
            error_code="YOLO_INFERENCE_UNAVAILABLE",
            message="YOLO 추론 환경을 사용할 수 없습니다.",
            detail=str(exc),
        ) from exc

    return create_detected_events(
        db=db,
        camera_id=resolved_camera_id,
        latitude=latitude,
        longitude=longitude,
        image_url=image_url,
        detected_objects=detected_objects,
        location_name=resolved_location_name,
    )


def read_event(event_id: int, db: Session = Depends(get_db)) -> RoadkillEvent:
    return get_event(db, event_id)


def patch_event_status(
    event_id: int,
    payload: EventStatusUpdate,
    db: Session = Depends(get_db),
) -> RoadkillEvent:
    return update_event_status(db, event_id, payload)


def list_comments(event_id: int, db: Session = Depends(get_db)) -> list[CommentRead]:
    return list_event_comments(db, event_id)


def create_comment(
    event_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
) -> CommentRead:
    return create_event_comment(db, event_id, payload)


def _required_form_value(field_name: str, value: str | None) -> str:
    if value is None or not value.strip():
        raise unprocessable_entity(
            error_code="REQUIRED_FORM_FIELD_MISSING",
            message=f"{field_name} 값은 필수입니다.",
            detail={"field": field_name},
        )
    return value.strip()


def _first_form_value(*values: object) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


router.get("", response_model=list[RoadkillEvent])(read_events)
router.post(
    "/detect",
    response_model=list[RoadkillEvent],
    status_code=status.HTTP_201_CREATED,
)(detect_events)
router.get("/{event_id}", response_model=RoadkillEvent)(read_event)
router.patch("/{event_id}/status", response_model=RoadkillEvent)(patch_event_status)
router.get("/{event_id}/comments", response_model=list[CommentRead])(list_comments)
router.post(
    "/{event_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)(create_comment)

compat_router.get("", response_model=list[RoadkillEvent])(read_events)
compat_router.post(
    "/detect",
    response_model=list[RoadkillEvent],
    status_code=status.HTTP_201_CREATED,
)(detect_events)
compat_router.get("/{event_id}", response_model=RoadkillEvent)(read_event)
compat_router.patch("/{event_id}/status", response_model=RoadkillEvent)(patch_event_status)
compat_router.get("/{event_id}/comments", response_model=list[CommentRead])(list_comments)
compat_router.post(
    "/{event_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)(create_comment)
