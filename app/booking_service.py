from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import calendar_client
from app.models import Booking, Customer, Facility, FacilityConfig
from app.schemas import SlotOption
from app.utils.time_utils import generate_slots_for_day, slot_overlaps


@dataclass
class FacilityWithConfig:
    facility: Facility
    config: FacilityConfig


async def get_facility_with_config(session: AsyncSession, facility_id: UUID) -> FacilityWithConfig:
    facility_result = await session.execute(
        select(Facility).where(Facility.id == facility_id)
    )
    facility = facility_result.scalar_one_or_none()
    if not facility:
        raise ValueError("Facility not found")

    config_result = await session.execute(
        select(FacilityConfig).where(FacilityConfig.facility_id == facility_id)
    )
    config = config_result.scalar_one_or_none()
    if not config:
        raise ValueError("Facility config missing")

    return FacilityWithConfig(facility=facility, config=config)


async def check_availability(
    session: AsyncSession, facility_id: UUID, target_date: datetime
) -> List[SlotOption]:
    facility_data = await get_facility_with_config(session, facility_id)
    facility = facility_data.facility
    config = facility_data.config

    weekday = target_date.strftime("%a").lower()[:3]
    daily_ranges = (config.open_hours.get(weekday) or []) if config.open_hours else []
    slots = generate_slots_for_day(target_date, daily_ranges, config.slot_minutes, facility.timezone)

    tz = pytz.timezone(facility.timezone)
    day_start_local = tz.localize(datetime.combine(target_date.date(), datetime.min.time()))
    day_end_local = tz.localize(datetime.combine(target_date.date(), datetime.max.time()))
    busy_intervals_local = calendar_client.get_busy_intervals(
        facility.phone_number, day_start_local, day_end_local
    )
    busy_intervals_utc = [(i[0].astimezone(pytz.UTC), i[1].astimezone(pytz.UTC)) for i in busy_intervals_local]

    available_slots: list[SlotOption] = []
    for slot in slots:
        slot_utc = (slot[0].astimezone(pytz.UTC), slot[1].astimezone(pytz.UTC))
        if slot_overlaps(slot_utc, busy_intervals_utc):
            continue
        available_slots.append(SlotOption(start=slot_utc[0], end=slot_utc[1]))
    return available_slots


async def upsert_customer(
    session: AsyncSession, facility_id: UUID, name: str, phone: str
) -> Customer:
    existing_result = await session.execute(
        select(Customer).where(Customer.facility_id == facility_id, Customer.phone == phone)
    )
    customer = existing_result.scalar_one_or_none()
    if customer:
        if name and customer.name != name:
            customer.name = name
            session.add(customer)
            await session.flush()
        return customer

    customer = Customer(facility_id=facility_id, name=name, phone=phone)
    session.add(customer)
    await session.flush()
    return customer


async def create_booking(
    session: AsyncSession,
    facility_id: UUID,
    customer_name: str,
    customer_phone: str,
    slot: SlotOption,
) -> Booking:
    facility_data = await get_facility_with_config(session, facility_id)
    facility = facility_data.facility

    customer = await upsert_customer(session, facility_id, customer_name, customer_phone)

    # TODO: Support per-court calendars based on facility_config.google_calendar_mode
    calendar_id = facility.phone_number
    event_id = calendar_client.create_event(
        calendar_id=calendar_id,
        summary=f"Badminton booking - {customer.name or customer.phone}",
        start=slot.start,
        end=slot.end,
        description="Created via AI receptionist",
    )

    booking = Booking(
        facility_id=facility_id,
        customer_id=customer.id,
        start_time=slot.start.astimezone(pytz.UTC),
        end_time=slot.end.astimezone(pytz.UTC),
        status="confirmed",
        google_event_id=event_id,
        source="phone_ai",
    )
    session.add(booking)
    await session.flush()
    return booking
