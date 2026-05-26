from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


InternalEventStatus = Literal[
    "UNCHECKED",
    "CHECKING",
    "DISPATCH_REQUESTED",
    "DISPATCHING",
    "COMPLETED",
    "MISIDENTIFIED",
]

DisplayEventStatus = Literal[
    "미확인",
    "확인 중",
    "출동 요청",
    "출동 중",
    "처리 완료",
    "오탐 처리",
]

RiskLevel = Literal["즉시 확인", "순차 확인", "후순위 확인"]


class BoundingBox(BaseModel):
    x: float = Field(..., ge=0.0, le=100.0)
    y: float = Field(..., ge=0.0, le=100.0)
    width: float = Field(..., gt=0.0, le=100.0)
    height: float = Field(..., gt=0.0, le=100.0)


class RoadkillEvent(BaseModel):
    id: str
    riskLevel: RiskLevel
    detectedAt: datetime
    location: str
    objectType: str
    status: DisplayEventStatus
    description: str
    cameraId: str
    repeatDetection: bool
    lastDetectedAt: datetime
    imageUrl: str
    boundingBox: BoundingBox

    model_config = ConfigDict(from_attributes=True)


class EventStatusUpdate(BaseModel):
    status: InternalEventStatus
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class CommentCreate(BaseModel):
    content: str = Field(..., max_length=500)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("content must not be blank")
        return stripped


class CommentRead(BaseModel):
    id: str
    eventId: str
    content: str
    createdAt: datetime
    writerName: str

    model_config = ConfigDict(from_attributes=True)
