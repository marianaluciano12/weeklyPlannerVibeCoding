from datetime import datetime, timedelta
import re
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

def looks_like_full_datetime(value):
    if not value or not isinstance(value, str):
        return False

    value = value.strip()

    # HH:MM or HH:MM:SS is only a time window, not a fixed datetime.
    if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", value):
        return False

    # ISO date or datetime, e.g. 2026-07-03 or 2026-07-03T20:00:00+01:00
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}", value))


def default_time_for_task(title, category, preferred_time_of_day=None):
    title_lower = (title or "").lower()
    category = category or "personal"
    preferred_time_of_day = preferred_time_of_day or "balanced"

    if preferred_time_of_day == "morning":
        return 8, 0

    if preferred_time_of_day == "afternoon":
        return 15, 0

    if preferred_time_of_day == "evening":
        return 20, 0

    if any(word in title_lower for word in ["cinema", "jantar", "date", "namorado", "amigos"]):
        return 20, 0

    if category == "exercise":
        return 18, 0

    if category == "errand":
        return 18, 0

    if category == "health":
        return 9, 0

    if category == "work":
        return 9, 0

    return 18, 0


def parse_fixed_task_datetime(value, title, category, preferred_time_of_day=None):
    if not looks_like_full_datetime(value):
        return None

    fixed_datetime = isoparse(value)

    if fixed_datetime.tzinfo is None:
        fixed_datetime = fixed_datetime.replace(tzinfo=TZ)

    # If the model returns only a date like 2026-07-03, isoparse sets 00:00.
    # Replace midnight with a sensible default based on the task.
    value_text = str(value)
    if "T" not in value_text and fixed_datetime.hour == 0 and fixed_datetime.minute == 0:
        hour, minute = default_time_for_task(
            title=title,
            category=category,
            preferred_time_of_day=preferred_time_of_day
        )
        fixed_datetime = fixed_datetime.replace(hour=hour, minute=minute)

    return fixed_datetime


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

    try:
        action = parse_user_message(
            request.message,
            calendar_context=calendar_context
        )
    except Exception as error:
        return {
            "status": "error",
            "message": f"Ocorreu um erro ao interpretar o pedido: {error}",
            "action": None
        }

    if action.get("error_type"):
        return {
            "status": "error",
            "message": action.get(
                "notes",
                "Ocorreu um erro ao comunicar com o modelo de IA. Tenta novamente mais tarde."
            ),
            "action": action
        }

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
        title = action.get("title") or "Lembrete"
        duration_minutes = action.get("duration_minutes") or 30

        start_datetime_value = action.get("start_datetime")

        # If the user did not give a specific date/time, ask the scheduler
        # to find the next available slot outside work hours.
        if not start_datetime_value:
            now = datetime.now(TZ)
            horizon = now + timedelta(days=7)

            busy_periods = get_free_busy(
                now.isoformat(),
                horizon.isoformat()
            )

            slots = find_slots_for_task(
                busy_periods=busy_periods,
                duration_minutes=duration_minutes,
                sessions_count=1,
                days=7,
                base_preferences=preferences,
                task_preferences={
                    "frequency": "weekly",
                    "allowed_days": "any",
                    "preferred_time_of_day": "balanced",
                    "preferred_window_start": None,
                    "preferred_window_end": None,
                }
            )

            if not slots:
                return {
                    "status": "error",
                    "message": f"Não encontrei um horário livre para: {title}",
                    "action": action
                }

            start_datetime = isoparse(slots[0]["start"])
            end_datetime = isoparse(slots[0]["end"])

        else:
            start_datetime = isoparse(start_datetime_value)

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

            # Create this list before any branch uses it.
            task_created_events = []

            task_frequency = task.get("frequency") or "weekly"
            preferred_window_start = task.get("preferred_window_start")

            # Handle one-off events inside a multi-task weekly plan.
            # Examples:
            # - "comprar ovos hoje depois do piano"
            # - "cinema com amigos na sexta"
            # - "date com o namorado no domingo à tarde"
            #
            # For one-off tasks, the model should provide task["start_datetime"].
            # Older prompts may still put a full ISO datetime in preferred_window_start,
            # so we support both.
            task_start_datetime_value = task.get("start_datetime") or preferred_window_start
            fixed_start_datetime = parse_fixed_task_datetime(
                value=task_start_datetime_value,
                title=title,
                category=category,
                preferred_time_of_day=task.get("preferred_time_of_day")
            )

            if task_frequency == "once" and fixed_start_datetime:
                try:
                    start_datetime = fixed_start_datetime
                    end_datetime = start_datetime + timedelta(minutes=duration_minutes)

                    created_event = create_calendar_event(
                        title=title,
                        start_datetime=start_datetime.isoformat(),
                        end_datetime=end_datetime.isoformat(),
                        description=f"Scheduled by AI Calendar Assistant. Category: {category}",
                        reminder_minutes_before=reminder_minutes,
                        category=category
                    )

                    created_events.append(created_event)
                    task_created_events.append(created_event)

                    working_busy_periods.append({
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat()
                    })

                    task_summaries.append(
                        f"{title}: 1/1 agendada"
                    )

                    continue

                except Exception as error:
                    task_summaries.append(
                        f"{title}: não foi possível agendar ({error})"
                    )
                    continue

            if task_frequency == "once" and not fixed_start_datetime:
                task_summaries.append(
                    f"{title}: não foi possível agendar porque faltou uma data/hora específica"
                )
                continue
            slots = find_slots_for_task(
                busy_periods=working_busy_periods,
                duration_minutes=duration_minutes,
                sessions_count=sessions_count,
                days=task_days,
                base_preferences=preferences,
                task_preferences=task
            )

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