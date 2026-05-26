from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ai.yolo_detector import DetectedObject
from core.errors import not_found
from models.comment import Comment
from models.equipment import Equipment
from models.event import Event
from models.user import User
from schemas.event import BoundingBox, CommentCreate, CommentRead, EventStatusUpdate, RoadkillEvent


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


def create_detected_events(
    db: Session,
    camera_id: str,
    latitude: float,
    longitude: float,
    image_url: str,
    detected_objects: list[DetectedObject],
    location_name: str | None = None,
    equipment_type: str = "CCTV",
) -> list[RoadkillEvent]:
    equipment = _get_or_create_equipment(
        db=db,
        camera_id=camera_id,
        location_name=location_name,
        equipment_type=equipment_type,
    )

    roadkill_events: list[RoadkillEvent] = []
    now = datetime.now(timezone.utc)

    for detected_object in detected_objects:
        event = _find_repeat_event(
            db=db,
            equipment_id=equipment.id,
            detected_object=detected_object,
            now=now,
        )

        if event is None:
            event = Event(
                equipment_id=equipment.id,
                user_id=None,
                obstacle_type="ANIMAL",
                species=detected_object.species,
                confidence=detected_object.confidence,
                latitude=latitude,
                longitude=longitude,
                status="UNCHECKED",
                image_url=image_url,
                bbox_x=detected_object.bbox_x,
                bbox_y=detected_object.bbox_y,
                bbox_width=detected_object.bbox_width,
                bbox_height=detected_object.bbox_height,
                priority=3,
                detected_at=now,
                repeat_detection=False,
                repeat_count=0,
                last_detected_at=now,
            )
            db.add(event)
            db.flush()
        else:
            event.repeat_count += 1
            event.repeat_detection = True
            event.priority = _priority_from_repeat_count(event.repeat_count)
            event.last_detected_at = now
            event.confidence = detected_object.confidence
            event.latitude = latitude
            event.longitude = longitude
            event.image_url = image_url

        roadkill_events.append(_to_roadkill_event(event, equipment))

    db.commit()
    return roadkill_events


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


def list_event_comments(db: Session, event_id: int) -> list[CommentRead]:
    event = db.get(Event, event_id)
    if event is None:
        raise not_found(
            error_code="EVENT_NOT_FOUND",
            message="해당 이벤트를 찾을 수 없습니다.",
            detail={"event_id": event_id},
        )

    comments = (
        db.query(Comment, User)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.event_id == event_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .all()
    )
    return [_to_comment_read(comment, user) for comment, user in comments]


def create_event_comment(db: Session, event_id: int, payload: CommentCreate) -> CommentRead:
    event = db.get(Event, event_id)
    if event is None:
        raise not_found(
            error_code="EVENT_NOT_FOUND",
            message="해당 이벤트를 찾을 수 없습니다.",
            detail={"event_id": event_id},
        )

    user_id = _get_system_operator_id(db)
    comment = Comment(
        event_id=event.id,
        user_id=user_id,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    user = db.get(User, user_id)
    return _to_comment_read(comment, user)


def _get_event_with_equipment(db: Session, event_id: int) -> tuple[Event, Equipment]:
    row = (
        db.query(Event, Equipment)
        .join(Equipment, Event.equipment_id == Equipment.id)
        .filter(Event.id == event_id)
        .first()
    )
    if row is None:
        raise not_found(
            error_code="EVENT_NOT_FOUND",
            message="해당 이벤트를 찾을 수 없습니다.",
            detail={"event_id": event_id},
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


def _to_comment_read(comment: Comment, user: User) -> CommentRead:
    return CommentRead(
        id=str(comment.id),
        eventId=str(comment.event_id),
        content=comment.content,
        createdAt=comment.created_at,
        writerName=_writer_name(user),
    )


def _get_system_operator_id(db: Session) -> int:
    user = db.query(User).filter(User.username == SYSTEM_OPERATOR_USERNAME).first()
    if user is None:
        user = User(username=SYSTEM_OPERATOR_USERNAME, role="OPERATOR")
        db.add(user)
        db.flush()
    return user.id


def _get_or_create_equipment(
    db: Session,
    camera_id: str,
    location_name: str | None,
    equipment_type: str,
) -> Equipment:
    equipment = db.query(Equipment).filter(Equipment.camera_id == camera_id).first()
    if equipment is not None:
        return equipment

    equipment = Equipment(
        camera_id=camera_id,
        equipment_type=equipment_type,
        location_name=location_name or "미지정 위치",
        status="ACTIVE",
    )
    db.add(equipment)
    db.flush()
    return equipment


def _find_repeat_event(
    db: Session,
    equipment_id: int,
    detected_object: DetectedObject,
    now: datetime,
) -> Event | None:
    candidates = (
        db.query(Event)
        .filter(Event.equipment_id == equipment_id)
        .filter(Event.species == detected_object.species)
        .order_by(Event.last_detected_at.desc())
        .all()
    )

    detected_center = _bbox_center(
        detected_object.bbox_x,
        detected_object.bbox_y,
        detected_object.bbox_width,
        detected_object.bbox_height,
    )

    for event in candidates:
        event_center = _bbox_center(
            event.bbox_x,
            event.bbox_y,
            event.bbox_width,
            event.bbox_height,
        )
        if event_center != detected_center:
            continue

        last_detected_at = _as_aware_utc(event.last_detected_at)
        if now - last_detected_at >= timedelta(minutes=1):
            return event

    return None


def _bbox_center(x: float, y: float, width: float, height: float) -> tuple[float, float]:
    return (round(x + width / 2, 6), round(y + height / 2, 6))


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _priority_from_repeat_count(repeat_count: int) -> int:
    if repeat_count <= 0:
        return 3
    if repeat_count == 1:
        return 2
    return 1


def _writer_name(user: User) -> str:
    if user.username == SYSTEM_OPERATOR_USERNAME:
        return "관제사"
    return user.username
