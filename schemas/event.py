from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    equipment_type: str = Field(..., pattern="^(CCTV|DRONE)$")
    equipment_id: str = Field(..., min_length=1, max_length=100)
    obstacle_type: str = Field(..., min_length=1, max_length=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    @classmethod
    def as_form(
        cls,
        equipment_type: str = Form(...),
        equipment_id: str = Form(...),
        obstacle_type: str = Form(...),
        confidence: float = Form(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
    ) -> "EventCreate":
        return cls(
            equipment_type=equipment_type,
            equipment_id=equipment_id,
            obstacle_type=obstacle_type,
            confidence=confidence,
            latitude=latitude,
            longitude=longitude,
        )


class EventRead(EventCreate):
    id: int
    image_url: str
    status: str
    detected_at: datetime

    model_config = {"from_attributes": True}
