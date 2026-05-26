from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from ai.yolo_detector import YoloDetector
from core.errors import service_unavailable, unprocessable_entity
from dependencies.database import get_db
from schemas.event import EventStatusUpdate, RoadkillEvent
from storage.image_storage import save_upload_image
from services.event_service import (
    create_detected_events,
    get_event,
    list_events,
    update_event_status,
)


router = APIRouter(prefix="/api/events", tags=["events"])
compat_router = APIRouter(prefix="/api/v1/events", tags=["events-compat"])
detector = YoloDetector()


def read_events(db: Session = Depends(get_db)) -> list[RoadkillEvent]:
    return list_events(db)


async def detect_events(
    camera_id: str | None = Form(default=None),
    camera_id_camel: str | None = Form(default=None, alias="cameraId"),
    latitude: float = Form(..., ge=-90.0, le=90.0),
    longitude: float = Form(..., ge=-180.0, le=180.0),
    location_name: str | None = Form(default=None),
    location_name_camel: str | None = Form(default=None, alias="locationName"),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> list[RoadkillEvent]:
    resolved_camera_id = _required_form_value(
        field_name="cameraId",
        value=camera_id_camel or camera_id,
    )
    resolved_location_name = location_name_camel or location_name

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


def _required_form_value(field_name: str, value: str | None) -> str:
    if value is None or not value.strip():
        raise unprocessable_entity(
            error_code="REQUIRED_FORM_FIELD_MISSING",
            message=f"{field_name} 값은 필수입니다.",
            detail={"field": field_name},
        )
    return value.strip()


router.get("", response_model=list[RoadkillEvent])(read_events)
router.post(
    "/detect",
    response_model=list[RoadkillEvent],
    status_code=status.HTTP_201_CREATED,
)(detect_events)
router.get("/{event_id}", response_model=RoadkillEvent)(read_event)
router.patch("/{event_id}/status", response_model=RoadkillEvent)(patch_event_status)

compat_router.get("", response_model=list[RoadkillEvent])(read_events)
compat_router.post(
    "/detect",
    response_model=list[RoadkillEvent],
    status_code=status.HTTP_201_CREATED,
)(detect_events)
compat_router.get("/{event_id}", response_model=RoadkillEvent)(read_event)
compat_router.patch("/{event_id}/status", response_model=RoadkillEvent)(patch_event_status)
