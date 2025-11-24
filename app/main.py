from __future__ import annotations

from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.booking_service import check_availability, create_booking
from app.db import get_session
from app.schemas import (
    AvailabilityRequest,
    AvailabilityResponse,
    BookingRequest,
    BookingResponse,
    HealthResponse,
)
from app.schemas import SlotOption
from app.telephony.twilio_webhook import router as twilio_router
from app.telephony.twilio_media import router as twilio_media_router

app = FastAPI(title="AI Receptionist Backend")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/availability", response_model=AvailabilityResponse)
async def availability(
    payload: AvailabilityRequest,
    session: AsyncSession = Depends(get_session),
) -> AvailabilityResponse:
    slots = await check_availability(session, payload.facility_id, datetime.combine(payload.date, datetime.min.time()))
    return AvailabilityResponse(slots=slots)


@app.post("/book", response_model=BookingResponse)
async def book(
    payload: BookingRequest,
    session: AsyncSession = Depends(get_session),
) -> BookingResponse:
    slot_option = SlotOption(start=payload.start, end=payload.end)
    booking = await create_booking(
        session,
        facility_id=payload.facility_id,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        slot=slot_option,
    )
    await session.commit()
    return BookingResponse(booking_id=booking.id, start=booking.start_time, end=booking.end_time)


app.include_router(twilio_router, prefix="/twilio")
app.include_router(twilio_media_router, prefix="/twilio")
