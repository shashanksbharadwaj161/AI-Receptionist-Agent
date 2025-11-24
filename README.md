# AI Receptionist Backend Skeleton

Backend scaffold for an AI-powered phone receptionist for badminton centers in India. Built with FastAPI, async SQLAlchemy, Twilio voice webhooks, OpenAI Realtime, and Google Calendar integration stubs.

## Getting Started

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the environment example and fill in credentials:

```bash
cp .env.example .env
```

3. Run the development server:

```bash
uvicorn app.main:app --reload
```

## Project Structure

- `app/config.py`: Pydantic settings loader for environment variables.
- `app/db.py`: Async SQLAlchemy engine and session factory.
- `app/models.py`: ORM models for facilities, bookings, calls, and related tables.
- `app/booking_service.py`: Availability and booking core logic.
- `app/calendar_client.py`: Google Calendar client stub.
- `app/ai/`: Prompt builder, tool handlers, and OpenAI Realtime client scaffold.
- `app/telephony/`: Twilio voice webhook and media stream skeleton.
- `app/main.py`: FastAPI application entrypoint with key routes.

## Notes

- Alembic migrations are not included; define migrations based on `app/models.py`.
- Google Calendar and OpenAI Realtime integrations are stubbed; fill in credential handling and streaming.
