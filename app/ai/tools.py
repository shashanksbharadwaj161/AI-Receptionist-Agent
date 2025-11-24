from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.booking_service import check_availability, create_booking
from app.schemas import SlotOption


async def check_availability_tool(session: AsyncSession, facility_id: UUID, date: datetime) -> List[Dict[str, Any]]:
    slots = await check_availability(session, facility_id, date)
    return [slot.dict() for slot in slots]


async def create_booking_tool(
    session: AsyncSession,
    facility_id: UUID,
    customer_name: str,
    customer_phone: str,
    start: datetime,
    end: datetime,
) -> Dict[str, Any]:
    slot = SlotOption(start=start, end=end)
    booking = await create_booking(
        session,
        facility_id=facility_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        slot=slot,
    )
    await session.commit()
    return {
        "booking_id": str(booking.id),
        "start": booking.start_time.isoformat(),
        "end": booking.end_time.isoformat(),
    }
