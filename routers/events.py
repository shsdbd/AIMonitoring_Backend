from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ai.yolo_detector import YoloDetector
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
detector = YoloDetector()


@router.get("", response_model=list[RoadkillEvent])
def read_events(db: Session = Depends(get_db)) -> list[RoadkillEvent]:
    return list_events(db)


@router.post("/detect", response_model=list[RoadkillEvent], status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
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


@router.get("/{event_id}", response_model=RoadkillEvent)
def read_event(event_id: int, db: Session = Depends(get_db)) -> RoadkillEvent:
    return get_event(db, event_id)


@router.patch("/{event_id}/status", response_model=RoadkillEvent)
def patch_event_status(
    event_id: int,
    payload: EventStatusUpdate,
    db: Session = Depends(get_db),
) -> RoadkillEvent:
    return update_event_status(db, event_id, payload)


def _required_form_value(field_name: str, value: str | None) -> str:
    if value is None or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} is required.",
        )
    return value.strip()
