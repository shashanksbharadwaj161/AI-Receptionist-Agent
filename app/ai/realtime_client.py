from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Callable, Dict

import websockets

from app.ai import tools
from app.ai.prompt_builder import build_system_prompt
from app.config import get_settings
from app.db import SessionLocal
from app.models import Facility, FacilityConfig

settings = get_settings()


class RealtimeClient:
    def __init__(self, facility: Facility, config: FacilityConfig):
        self.facility = facility
        self.config = config
        self.ws = None
        self.session = SessionLocal()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
        await self.session.close()

    async def connect(self) -> None:
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        self.ws = await websockets.connect("wss://api.openai.com/v1/realtime", extra_headers=headers)
        await self._send_system_prompt()
        await self._register_tools()

    async def _send_system_prompt(self) -> None:
        prompt = build_system_prompt(self.facility, self.config)
        await self.ws.send(json.dumps({"type": "system", "content": prompt}))

    async def _register_tools(self) -> None:
        # Define tool schemas for the Realtime API.
        payload = {
            "type": "register_tools",
            "tools": [
                {
                    "name": "check_availability",
                    "description": "Check available time slots for a facility on a date",
                    "parameters": {
                        "facility_id": "string",
                        "date": "string",
                    },
                },
                {
                    "name": "create_booking",
                    "description": "Create a booking for a customer",
                    "parameters": {
                        "facility_id": "string",
                        "customer_name": "string",
                        "customer_phone": "string",
                        "start": "string",
                        "end": "string",
                    },
                },
            ],
        }
        await self.ws.send(json.dumps(payload))

    async def listen(self) -> None:
        async for message in self.ws:
            data = json.loads(message)
            if data.get("type") == "tool_call":
                await self._handle_tool_call(data)
            # TODO: handle other message types such as text/audio generation

    async def _handle_tool_call(self, data: Dict[str, Any]) -> None:
        name = data["name"]
        args = data.get("arguments", {})
        tool_id = data.get("id")
        if name == "check_availability":
            result = await tools.check_availability_tool(
                self.session,
                facility_id=args.get("facility_id"),
                date=datetime.fromisoformat(args.get("date")),
            )
        elif name == "create_booking":
            result = await tools.create_booking_tool(
                self.session,
                facility_id=args.get("facility_id"),
                customer_name=args.get("customer_name"),
                customer_phone=args.get("customer_phone"),
                start=datetime.fromisoformat(args.get("start")),
                end=datetime.fromisoformat(args.get("end")),
            )
        else:
            result = {"error": "Unknown tool"}

        response = {"type": "tool_result", "tool_id": tool_id, "result": result}
        await self.ws.send(json.dumps(response))

    async def close(self) -> None:
        if self.ws:
            await self.ws.close()
