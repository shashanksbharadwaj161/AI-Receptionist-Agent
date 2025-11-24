from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


STREAM_PATH = "/twilio/media"


def get_stream_url(call_id: str) -> str:
    # Twilio requires public URL. In production use https URL.
    return STREAM_PATH + f"?call_id={call_id}"


@router.websocket("/media")
async def media_stream(ws: WebSocket):
    await ws.accept()
    call_id = ws.query_params.get("call_id")
    try:
        while True:
            message = await ws.receive_text()
            payload = json.loads(message)
            # TODO: Handle Twilio audio chunks and forward to OpenAI Realtime session.
            # Expected format includes media.payload (base64-encoded audio) and other metadata.
            # 1. Decode/convert audio payload to format expected by OpenAI Realtime audio stream.
            # 2. Send audio frames over the Realtime WebSocket client.
            # 3. Receive AI-generated audio and push back to Twilio via <Stream> websocket (ws.send_bytes).
            # 4. Manage session lifecycle and teardown when call ends.
    except WebSocketDisconnect:
        # TODO: Cleanup Realtime session and any resources.
        pass
