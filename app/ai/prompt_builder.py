from __future__ import annotations

from app.models import Facility, FacilityConfig


def build_system_prompt(facility: Facility, config: FacilityConfig) -> str:
    open_hours_summary = ", ".join(
        f"{day}: {', '.join(ranges)}" for day, ranges in (config.open_hours or {}).items()
    )
    prompt = f"""
You are an AI phone receptionist for a badminton center in India.
Facility name: {facility.name}.
Timezone: {facility.timezone}.
Operating hours: {open_hours_summary}.
Slot length: {config.slot_minutes} minutes.

Your job is to answer calls, help callers book badminton courts, and answer simple questions.
Always confirm caller name, phone number, date, and time before booking.
Use the provided tools to check availability and create bookings. If you cannot handle a request, let the caller know a human will call back.
"""
    return prompt.strip()
