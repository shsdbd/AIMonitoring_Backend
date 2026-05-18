from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "equipment_type IN ('CCTV', 'DRONE')",
            name="ck_events_equipment_type",
        ),
        CheckConstraint(
            "status IN ('UNCHECKED', 'CHECKING', 'COMPLETED', 'MISIDENTIFIED')",
            name="ck_events_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_type: Mapped[str] = mapped_column(String, nullable=False)
    equipment_id: Mapped[str] = mapped_column(String, nullable=False)
    obstacle_type: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="UNCHECKED")
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
