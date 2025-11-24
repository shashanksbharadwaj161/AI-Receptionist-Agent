from __future__ import annotations

from datetime import datetime
from typing import List

import pytz
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.booking_service import check_availability, create_booking, get_facility_with_config
from app.db import get_session
from app.schemas import MockCallRequest, MockCallResponse, SlotOption

router = APIRouter()


@router.post("/mock-call", response_model=MockCallResponse)
async def mock_call_flow(
    payload: MockCallRequest, session: AsyncSession = Depends(get_session)
) -> MockCallResponse:
    """Dry-run the booking flow without Twilio or audio.

    This endpoint simulates how the AI receptionist would book a court by:
    1) loading the facility + config,
    2) generating availability for the requested date,
    3) creating a booking for the first open slot,
    4) returning a conversational script so you can see what the caller/AI would say.
    """

    try:
        facility_data = await get_facility_with_config(session, payload.facility_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Facility or config not found")

    facility = facility_data.facility
    target_date = datetime.combine(payload.date, datetime.min.time())
    slots = await check_availability(session, payload.facility_id, target_date)
    if not slots:
        return MockCallResponse(
            script=[
                f"AI: Thanks for calling {facility.name}.",
                "Caller: I'd like to book a court.",
                "AI: I'm sorry, there are no open slots on that date. Would you like another day?",
            ],
            note="No availability for the selected date",
        )

    slot = slots[0]
    booking = await create_booking(
        session,
        facility_id=payload.facility_id,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        slot=SlotOption(start=slot.start, end=slot.end),
    )
    await session.commit()

    tz = pytz.timezone(facility.timezone)
    start_local = slot.start.astimezone(tz)
    end_local = slot.end.astimezone(tz)

    script: List[str] = [
        f"AI: Thanks for calling {facility.name}. How can I help you today?",
        "Caller: I'd like to book a court.",
        f"AI: I can book you on {payload.date.isoformat()} from {start_local.strftime('%H:%M')} to {end_local.strftime('%H:%M')} ({facility.timezone}). Shall I confirm it under {payload.customer_name}?",
        f"Caller: Yes, please book it with my number {payload.customer_phone}.",
        "AI: All set! Your booking is confirmed. We'll text the details to your phone.",
    ]

    return MockCallResponse(
        script=script,
        booked_slot=SlotOption(start=slot.start, end=slot.end),
        booking_id=booking.id,
    )
