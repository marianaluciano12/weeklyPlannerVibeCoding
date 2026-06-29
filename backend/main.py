from datetime import datetime, timedelta
from turtle import title
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpcore import request

from models import AssistantRequest
from llm_service import parse_user_message
from calendar_service import (
     list_calendar_events,
      list_calendar_events_for_context,
      create_calendar_event,
      get_free_busy,
      delete_calendar_event
)
from scheduler import find_daily_slots, find_slots_for_task

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
        "message": "Evento eliminado com sucesso.",
        "deleted_event": deleted_event
    }

@app.post("/assistant")
def assistant(request: AssistantRequest):
    now = datetime.now(TZ)
    context_end = now + timedelta(days=14)

    calendar_context = list_calendar_events_for_context(
      now.isoformat(),
      context_end.isoformat()
    )

    action = parse_user_message(
      request.message,
      calendar_context=calendar_context
    )
    preferences = request.preferences
    action_type = action.get("action")
    category = action.get("category") or "personal"

    if request.preferences:
      if hasattr(request.preferences, "model_dump"):
        preferences = request.preferences.model_dump()
      else:
        preferences = request.preferences.dict()



    if action_type == "unknown":
        return {
            "status": "error",
            "message": "Não consegui perceber esse pedido.",
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
          description=f"Created by AI Calendar Assistant. Category: {category}",
          reminder_minutes_before=reminder_minutes,
          category=category
)

        return {
            "status": "success",
            "message": f"Lembrete criado: {title}",
            "created_events": [created_event],
            "action": action
        }
    if action_type == "schedule_plan":
        tasks = action.get("tasks") or []

        if not tasks:
            return {
                "status": "error",
                "message": "I understood this as a weekly plan, but no tasks were returned.",
                "action": action
            }

        now = datetime.now(TZ)
        days = 7
        horizon = now + timedelta(days=days)

        working_busy_periods = get_free_busy(
            now.isoformat(),
            horizon.isoformat()
        )

        created_events = []
        task_summaries = []

        reminder_minutes = 10

        if preferences:
            reminder_minutes = preferences.get("default_reminder_minutes", 10)

        def task_sort_key(task):
            score = 0

            # Tasks with restricted windows should be scheduled first.
            if task.get("preferred_window_start") and task.get("preferred_window_end"):
                score -= 100

            if task.get("allowed_days") and task.get("allowed_days") != "any":
                score -= 50

            # Longer tasks are harder to place, so schedule earlier.
            score -= int(task.get("duration_minutes") or 30)

            return score

        sorted_tasks = sorted(tasks, key=task_sort_key)

        for task in sorted_tasks:
            title = task.get("title") or "Scheduled task"
            duration_minutes = int(task.get("duration_minutes") or 30)
            sessions_count = int(task.get("sessions_count") or 1)
            task_days = int(task.get("days") or 7)
            category = task.get("category") or "personal"

            slots = find_slots_for_task(
                busy_periods=working_busy_periods,
                duration_minutes=duration_minutes,
                sessions_count=sessions_count,
                days=task_days,
                base_preferences=preferences,
                task_preferences=task
            )

            task_created_events = []

            for slot in slots:
                created_event = create_calendar_event(
                    title=title,
                    start_datetime=slot["start"],
                    end_datetime=slot["end"],
                    description=f"Scheduled by AI Calendar Assistant. Category: {category}",
                    reminder_minutes_before=reminder_minutes,
                    category=category
                )

                created_events.append(created_event)
                task_created_events.append(created_event)

                # Important: add newly scheduled events to the busy list,
                # so the next task does not get scheduled on top of this one.
                working_busy_periods.append({
                    "start": slot["start"],
                    "end": slot["end"]
                })

            task_summaries.append(
                f"{title}: {len(task_created_events)}/{sessions_count} agendadas"
            )

        return {
            "status": "success",
            "message": "Plano semanal criado. " + " · ".join(task_summaries),
            "created_events": created_events,
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
              description=f"Scheduled by AI Calendar Assistant. Category: {category}",
              reminder_minutes_before=reminder_minutes,
              category=category
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