from __future__ import annotations

from datetime import datetime, time, timedelta
import pytz
from typing import Iterable, Tuple


def parse_time_range(range_str: str) -> Tuple[time, time]:
    start_str, end_str = range_str.split("-")
    start = datetime.strptime(start_str, "%H:%M").time()
    end = datetime.strptime(end_str, "%H:%M").time()
    return start, end


def generate_slots_for_day(
    date_value: datetime, ranges: Iterable[str], slot_minutes: int, tz_name: str
) -> list[tuple[datetime, datetime]]:
    tz = pytz.timezone(tz_name)
    slots: list[tuple[datetime, datetime]] = []
    for range_str in ranges:
        start_time, end_time = parse_time_range(range_str)
        window_start = tz.localize(datetime.combine(date_value.date(), start_time))
        window_end = tz.localize(datetime.combine(date_value.date(), end_time))

        current = window_start
        delta = timedelta(minutes=slot_minutes)
        while current + delta <= window_end:
            slots.append((current, current + delta))
            current += delta
    return slots


def slot_overlaps(slot: tuple[datetime, datetime], intervals: Iterable[tuple[datetime, datetime]]) -> bool:
    for busy_start, busy_end in intervals:
        if slot[0] < busy_end and busy_start < slot[1]:
            return True
    return False
