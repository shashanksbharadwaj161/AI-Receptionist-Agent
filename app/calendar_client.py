from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

# TODO: Integrate google-auth and google-api-python-client with OAuth2 tokens.
# For now, this module provides stubbed implementations that should be replaced
# with real calendar interactions.


def get_busy_intervals(calendar_id: str, day_start: datetime, day_end: datetime) -> List[Tuple[datetime, datetime]]:
    """Return busy intervals for the day.

    Replace this stub with Google Calendar free/busy query using stored credentials.
    """
    # Example stub returning no busy intervals.
    return []


def create_event(
    calendar_id: str,
    summary: str,
    start: datetime,
    end: datetime,
    description: str | None = None,
) -> str:
    """Create an event and return the Google event ID.

    TODO: implement Google Calendar event creation with OAuth2 credentials.
    """
    # Stubbed event id
    return "stubbed-google-event-id"
