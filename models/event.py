from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_events_confidence_range",
        ),
        CheckConstraint(
            "latitude >= -90.0 AND latitude <= 90.0",
            name="ck_events_latitude_range",
        ),
        CheckConstraint(
            "longitude >= -180.0 AND longitude <= 180.0",
            name="ck_events_longitude_range",
        ),
        CheckConstraint(
            "status IN ('UNCHECKED', 'CHECKING', 'DISPATCH_REQUESTED', "
            "'DISPATCHING', 'COMPLETED', 'MISIDENTIFIED')",
            name="ck_events_status",
        ),
        CheckConstraint(
            "species IN ('gorani', 'wild_boar', 'raccoon')",
            name="ck_events_species",
        ),
        CheckConstraint(
            "bbox_x >= 0.0 AND bbox_x <= 100.0",
            name="ck_events_bbox_x_range",
        ),
        CheckConstraint(
            "bbox_y >= 0.0 AND bbox_y <= 100.0",
            name="ck_events_bbox_y_range",
        ),
        CheckConstraint(
            "bbox_width > 0.0 AND bbox_width <= 100.0",
            name="ck_events_bbox_width_range",
        ),
        CheckConstraint(
            "bbox_height > 0.0 AND bbox_height <= 100.0",
            name="ck_events_bbox_height_range",
        ),
        CheckConstraint(
            "priority IN (1, 2, 3)",
            name="ck_events_priority",
        ),
        CheckConstraint(
            "repeat_count >= 0",
            name="ck_events_repeat_count_non_negative",
        ),
        Index("ix_events_detected_at", "detected_at"),
        Index("ix_events_status", "status"),
        Index("ix_events_equipment_id", "equipment_id"),
        Index("ix_events_user_id", "user_id"),
        Index("ix_events_priority", "priority"),
        Index("ix_events_status_detected_at", "status", "detected_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("equipment.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    obstacle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="UNCHECKED",
        server_default="UNCHECKED",
    )
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    bbox_x: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_width: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_height: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    repeat_detection: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    repeat_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    last_detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
