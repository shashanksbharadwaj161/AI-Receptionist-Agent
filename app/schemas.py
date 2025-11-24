from datetime import datetime, date
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class SlotOption(BaseModel):
    start: datetime
    end: datetime


class AvailabilityRequest(BaseModel):
    facility_id: UUID
    date: date


class AvailabilityResponse(BaseModel):
    slots: List[SlotOption]


class BookingRequest(BaseModel):
    facility_id: UUID
    customer_name: str = Field(..., min_length=1)
    customer_phone: str = Field(..., min_length=5)
    start: datetime
    end: datetime


class BookingResponse(BaseModel):
    booking_id: UUID
    start: datetime
    end: datetime


class HealthResponse(BaseModel):
    status: str


class MockCallRequest(BaseModel):
    facility_id: UUID
    date: date
    customer_name: str = Field(..., min_length=1)
    customer_phone: str = Field(..., min_length=5)


class MockCallResponse(BaseModel):
    script: List[str]
    booked_slot: SlotOption | None = None
    booking_id: UUID | None = None
    note: str | None = None
