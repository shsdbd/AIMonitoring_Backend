from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.comment import Comment
from models.equipment import Equipment
from models.event import Event
from models.user import User
from schemas.event import BoundingBox, EventStatusUpdate, RoadkillEvent


STATUS_LABELS = {
    "UNCHECKED": "미확인",
    "CHECKING": "확인 중",
    "DISPATCH_REQUESTED": "출동 요청",
    "DISPATCHING": "출동 중",
    "COMPLETED": "처리 완료",
    "MISIDENTIFIED": "오탐 처리",
}

RISK_LEVELS = {
    1: "즉시 확인",
    2: "순차 확인",
    3: "후순위 확인",
}

SPECIES_LABELS = {
    "gorani": "고라니",
    "wild_boar": "멧돼지",
    "raccoon": "너구리",
}

SYSTEM_OPERATOR_USERNAME = "system_operator"


def list_events(db: Session) -> list[RoadkillEvent]:
    rows = (
        db.query(Event, Equipment)
        .join(Equipment, Event.equipment_id == Equipment.id)
        .order_by(Event.detected_at.desc(), Event.id.desc())
        .all()
    )
    return [_to_roadkill_event(event, equipment) for event, equipment in rows]


def get_event(db: Session, event_id: int) -> RoadkillEvent:
    event, equipment = _get_event_with_equipment(db, event_id)
    return _to_roadkill_event(event, equipment)


def update_event_status(
    db: Session,
    event_id: int,
    payload: EventStatusUpdate,
) -> RoadkillEvent:
    event, equipment = _get_event_with_equipment(db, event_id)
    event.status = payload.status

    if payload.comment:
        user_id = event.user_id or _get_system_operator_id(db)
        event.user_id = event.user_id or user_id
        db.add(
            Comment(
                event_id=event.id,
                user_id=user_id,
                content=payload.comment,
            )
        )

    db.commit()
    db.refresh(event)
    return _to_roadkill_event(event, equipment)


def _get_event_with_equipment(db: Session, event_id: int) -> tuple[Event, Equipment]:
    row = (
        db.query(Event, Equipment)
        .join(Equipment, Event.equipment_id == Equipment.id)
        .filter(Event.id == event_id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 이벤트를 찾을 수 없습니다.",
        )
    return row


def _to_roadkill_event(event: Event, equipment: Equipment) -> RoadkillEvent:
    species_label = SPECIES_LABELS.get(event.species, event.species)
    confidence_percent = round(event.confidence * 100)

    return RoadkillEvent(
        id=str(event.id),
        riskLevel=RISK_LEVELS[event.priority],
        detectedAt=event.detected_at,
        location=equipment.location_name,
        objectType=species_label,
        status=STATUS_LABELS[event.status],
        description=f"{species_label} 객체가 {confidence_percent}% 신뢰도로 감지되었습니다.",
        cameraId=equipment.camera_id,
        repeatDetection=event.repeat_detection,
        lastDetectedAt=event.last_detected_at,
        imageUrl=event.image_url,
        boundingBox=BoundingBox(
            x=event.bbox_x,
            y=event.bbox_y,
            width=event.bbox_width,
            height=event.bbox_height,
        ),
    )


def _get_system_operator_id(db: Session) -> int:
    user = db.query(User).filter(User.username == SYSTEM_OPERATOR_USERNAME).first()
    if user is None:
        user = User(username=SYSTEM_OPERATOR_USERNAME, role="OPERATOR")
        db.add(user)
        db.flush()
    return user.id
