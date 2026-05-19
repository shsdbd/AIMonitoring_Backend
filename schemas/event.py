from datetime import datetime
from typing import Optional
from fastapi import Form
from pydantic import BaseModel, Field

class EventCreate(BaseModel):
    equipment_id: int = Field(..., ge=1)
    obstacle_type: str = Field(..., min_length=1, max_length=50)
    confidence: float = Field(..., ge=0.0, le=1.0)
    latitude: float = Field(..., ge=-90.0, le=90.0)      # 위도 검증 추가
    longitude: float = Field(..., ge=-180.0, le=180.0)   # 경도 검증 추가

    @classmethod
    def as_form(
        cls,
        equipment_id: int = Form(...),
        obstacle_type: str = Form(...),
        confidence: float = Form(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
    ) -> "EventCreate":
        return cls(
            equipment_id=equipment_id,
            obstacle_type=obstacle_type,
            confidence=confidence,
            latitude=latitude,
            longitude=longitude,
        )

class EventRead(EventCreate):
    id: int
    user_id: Optional[int] = None
    image_url: str
    status: str
    detected_at: datetime

    model_config = {"from_attributes": True}