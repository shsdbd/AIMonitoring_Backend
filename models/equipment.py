from sqlalchemy import CheckConstraint, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = (
        CheckConstraint(
            "equipment_type IN ('CCTV', 'DRONE')",
            name="ck_equipment_equipment_type",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')",
            name="ck_equipment_status",
        ),
        Index("ix_equipment_equipment_type", "equipment_type"),
        Index("ix_equipment_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    equipment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    location_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE",
    )
