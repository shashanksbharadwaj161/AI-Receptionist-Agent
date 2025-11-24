from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.twiml.voice_response import VoiceResponse

from app.db import get_session
from app.models import Call, Facility
from app.telephony import twilio_media

router = APIRouter()


@router.post("/voice")
async def voice_webhook(
    From: str = Form(...),
    To: str = Form(...),
    CallSid: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    facility_result = await session.execute(select(Facility).where(Facility.phone_number == To))
    facility = facility_result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found for this number")

    call = Call(facility_id=facility.id, caller_phone=From, meta={"CallSid": CallSid})
    session.add(call)
    await session.commit()

    response = VoiceResponse()
    response.say("Connecting you to our AI receptionist. Please hold.")
    stream_url = twilio_media.get_stream_url(call_id=str(call.id))
    response.connect().stream(url=stream_url)
    return Response(content=str(response), media_type="application/xml")
