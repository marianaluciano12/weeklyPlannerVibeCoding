from datetime import datetime, timedelta
from turtle import title
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AssistantRequest
from llm_service import parse_user_message
from calendar_service import (
    list_calendar_events,
    create_calendar_event,
    get_free_busy,
    delete_calendar_event
)
from scheduler import find_daily_slots

TIMEZONE = "Europe/Lisbon"
TZ = ZoneInfo(TIMEZONE)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Calendar Assistant backend is running."
    }


@app.get("/events")
def get_events(start: str, end: str):
    return list_calendar_events(start, end)


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    deleted_event = delete_calendar_event(event_id)

    return {
        "status": "success",
        "message": "Event deleted successfully.",
        "deleted_event": deleted_event
    }

@app.post("/assistant")
def assistant(request: AssistantRequest):
    action = parse_user_message(request.message)
    preferences = request.preferences
    action_type = action.get("action")

    if request.preferences:
      if hasattr(request.preferences, "model_dump"):
        preferences = request.preferences.model_dump()
      else:
        preferences = request.preferences.dict()



    if action_type == "unknown":
        return {
            "status": "error",
            "message": "I could not understand that request.",
            "action": action
        }

    if action_type == "create_reminder":
        title = action.get("title") or "Reminder"
        duration_minutes = action.get("duration_minutes") or 10

        start_datetime = isoparse(action["start_datetime"])

        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=TZ)

        end_datetime = start_datetime + timedelta(minutes=duration_minutes)

        reminder_minutes = 10

        if preferences:
          reminder_minutes = preferences.get("default_reminder_minutes", 10)

        created_event = create_calendar_event(
          title=title,
          start_datetime=start_datetime.isoformat(),
          end_datetime=end_datetime.isoformat(),
          description="Created by AI Calendar Assistant",
          reminder_minutes_before=reminder_minutes
)

        return {
            "status": "success",
            "message": f"Created reminder: {title}",
            "created_events": [created_event],
            "action": action
        }

    if action_type == "schedule_habit":
        title = action.get("title") or "Habit"
        duration_minutes = action.get("duration_minutes") or 20
        days = action.get("days") or 7

        now = datetime.now(TZ)
        horizon = now + timedelta(days=days)

        busy_periods = get_free_busy(
            now.isoformat(),
            horizon.isoformat()
        )

        slots = find_daily_slots(
          busy_periods=busy_periods,
          duration_minutes=duration_minutes,
          days=days,
          preferences=preferences
        )

        created_events = []

        for slot in slots:
            reminder_minutes = 10

            if preferences:
              reminder_minutes = preferences.get("default_reminder_minutes", 10)

            created_event = create_calendar_event(
              title=title,
              start_datetime=slot["start"],
              end_datetime=slot["end"],
              description="Scheduled by AI Calendar Assistant",
              reminder_minutes_before=reminder_minutes
            )   

            created_events.append(created_event)

        return {
            "status": "success",
            "message": f"Scheduled {len(created_events)} session(s) for {title}.",
            "created_events": created_events,
            "action": action
        }

    return {
        "status": "error",
        "message": "Unsupported action.",
        "action": action
    }