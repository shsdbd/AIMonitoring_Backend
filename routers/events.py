from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.database import get_db
from schemas.event import EventStatusUpdate, RoadkillEvent
from services.event_service import (
    get_event,
    list_events,
    update_event_status,
)


router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[RoadkillEvent])
def read_events(db: Session = Depends(get_db)) -> list[RoadkillEvent]:
    return list_events(db)


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
