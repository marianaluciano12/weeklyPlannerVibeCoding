from datetime import datetime, timedelta
import re
import unicodedata
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse

from llm_service import parse_user_message
from calendar_service import (
    list_calendar_events_for_context,
    create_calendar_event,
    get_free_busy,
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


def normalize_text(value):
    value = (value or "").lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return value


def has_current_week_phrase(text):
    normalized = normalize_text(text)

    next_week_phrases = [
        "proxima semana",
        "semana que vem",
        "next week",
    ]

    if any(phrase in normalized for phrase in next_week_phrases):
        return False

    current_week_phrases = [
        "esta semana",
        "nesta semana",
        "durante esta semana",
        "ate domingo",
        "this week",
    ]

    return any(phrase in normalized for phrase in current_week_phrases)


def days_until_sunday(base_datetime):
    # Monday = 0, Sunday = 6.
    # Inclusive count: Tuesday -> Tue, Wed, Thu, Fri, Sat, Sun = 6 days.
    return max(1, 7 - base_datetime.weekday())


def get_planning_days_for_request(default_days, original_message, base_datetime):
    default_days = int(default_days or 7)

    if has_current_week_phrase(original_message):
        return min(default_days, days_until_sunday(base_datetime))

    return default_days


def has_explicit_time(text):
    normalized = normalize_text(text)

    explicit_patterns = [
        r"\b\d{1,2}:\d{2}\b",
        r"\b\d{1,2}h\d{0,2}\b",
        r"\b(?:as|das|pelas|por volta das|a partir das)\s+\d{1,2}\b",
        r"\bmeio dia\b",
        r"\bmeia noite\b",
    ]

    return any(re.search(pattern, normalized) for pattern in explicit_patterns)


def round_up_to_next_15_from_main(value):
    minute = ((value.minute + 14) // 15) * 15

    if minute == 60:
        return value.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    return value.replace(minute=minute, second=0, microsecond=0)


def get_next_available_slot_for_today(duration_minutes, preferences, now):
    horizon = now.replace(hour=23, minute=59, second=0, microsecond=0)

    busy_periods = get_free_busy(
        now.isoformat(),
        horizon.isoformat()
    )

    slots = find_slots_for_task(
        busy_periods=busy_periods,
        duration_minutes=duration_minutes,
        sessions_count=1,
        days=1,
        base_preferences=preferences,
        task_preferences={
            "frequency": "weekly",
            "allowed_days": "any",
            "preferred_time_of_day": "earliest",
            "preferred_window_start": None,
            "preferred_window_end": None,
        }
    )

    if slots:
        return isoparse(slots[0]["start"]), isoparse(slots[0]["end"])

    fallback_start = round_up_to_next_15_from_main(now)
    fallback_end = fallback_start + timedelta(minutes=duration_minutes)

    return fallback_start, fallback_end


def adjust_today_datetime_if_needed(start_datetime, duration_minutes, original_context, preferences, now):
    if start_datetime.date() != now.date():
        return start_datetime, start_datetime + timedelta(minutes=duration_minutes)

    if start_datetime >= now:
        return start_datetime, start_datetime + timedelta(minutes=duration_minutes)

    # If the user explicitly gave a time, respect it even if it is earlier today.
    if has_explicit_time(original_context):
        return start_datetime, start_datetime + timedelta(minutes=duration_minutes)

    # Otherwise, never create an event earlier than the current time today.
    return get_next_available_slot_for_today(
        duration_minutes=duration_minutes,
        preferences=preferences,
        now=now
    )


def get_context_for_task(task, original_message):
    message_normalized = normalize_text(original_message)
    title_normalized = normalize_text(task.get("title") or "")

    keywords = [
        word for word in re.findall(r"[a-z0-9]+", title_normalized)
        if len(word) >= 4 and word not in {
            "com",
            "para",
            "tenho",
            "quero",
            "preciso",
            "minutos",
            "todos",
            "dias",
            "esta",
            "semana",
        }
    ]

    category = task.get("category") or ""

    if category == "relationship":
        keywords.extend(["date", "namorado", "namorada", "casal"])
    elif category == "personal":
        keywords.extend(["cinema", "amigos", "jantar"])
    elif category == "errand":
        keywords.extend(["comprar", "ovos", "compras"])
    elif category == "exercise":
        keywords.extend(["ginasio", "treino"])
    elif category == "hobby":
        keywords.extend(["piano", "praticar"])

    positions = [
        message_normalized.find(keyword)
        for keyword in keywords
        if keyword and message_normalized.find(keyword) != -1
    ]

    if not positions:
        return message_normalized

    position = min(positions)

    # Find the local phrase for this task only.
    # This prevents "cinema na sexta das 21:00 às 23:00" from leaking into
    # "piano", "ginásio" or "comprar ovos" in the same long request.
    rough_start = max(0, position - 120)
    rough_end = min(len(message_normalized), position + 220)

    previous_separators = [
        ". ",
        "; ",
        ", tenho ",
        ", preciso ",
        ", quero ",
        " e tenho ",
        " e preciso ",
        " e quero ",
        " e um ",
        " e uma ",
        " tenho ",
        " preciso ",
        " quero ",
    ]

    next_separators = [
        ". ",
        "; ",
        ", tenho ",
        ", preciso ",
        ", quero ",
        " e tenho ",
        " e preciso ",
        " e quero ",
        " e um ",
        " e uma ",
    ]

    start = rough_start

    for separator in previous_separators:
        separator_position = message_normalized.rfind(separator, rough_start, position)

        if separator_position != -1:
            start = max(start, separator_position + len(separator))

    end = rough_end

    for separator in next_separators:
        separator_position = message_normalized.find(separator, position + 1, rough_end)

        if separator_position != -1:
            end = min(end, separator_position)

    return message_normalized[start:end]


def extract_time_range_from_text(text_value):
    normalized = normalize_text(text_value)

    # Matches:
    # "das 21:00 as 23:00"
    # "21:00 às 23:00"
    # "21h as 23h"
    # "21-23"
    pattern = (
        r"(?:das|de|entre)?\s*"
        r"(\d{1,2})(?::(\d{2})|h(\d{2})?)?"
        r"\s*(?:as|a|ate|-)\s*"
        r"(\d{1,2})(?::(\d{2})|h(\d{2})?)?"
    )

    match = re.search(pattern, normalized)

    if not match:
        return None

    start_hour = int(match.group(1))
    start_minute = int(match.group(2) or match.group(3) or 0)
    end_hour = int(match.group(4))
    end_minute = int(match.group(5) or match.group(6) or 0)

    return start_hour, start_minute, end_hour, end_minute



def extract_single_time_from_text(text_value):
    normalized = normalize_text(text_value)

    patterns = [
        r"\b(\d{1,2}):(\d{2})\b",
        r"\b(\d{1,2})h(\d{2})?\b",
        r"\b(?:as|pelas|por volta das|a partir das)\s+(\d{1,2})(?:[:h](\d{2}))?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue

        hour = int(match.group(1))
        minute = int(match.group(2) or 0)

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute

    return None


def resolve_target_date_from_context(context_normalized, base_datetime, target_weekday):
    if "hoje" in context_normalized:
        return base_datetime.date()

    if "amanha" in context_normalized:
        return (base_datetime + timedelta(days=1)).date()

    days_ahead = target_weekday - base_datetime.weekday()
    if days_ahead < 0:
        days_ahead += 7

    return (base_datetime + timedelta(days=days_ahead)).date()

def next_weekday_datetime(base_datetime, target_weekday, hour, minute):
    days_ahead = target_weekday - base_datetime.weekday()

    if days_ahead < 0:
        days_ahead += 7

    candidate_date = (base_datetime + timedelta(days=days_ahead)).date()
    candidate_datetime = datetime.combine(candidate_date, datetime.min.time(), TZ)
    candidate_datetime = candidate_datetime.replace(hour=hour, minute=minute)

    if candidate_datetime <= base_datetime:
        candidate_datetime = candidate_datetime + timedelta(days=7)

    return candidate_datetime


def infer_fixed_datetime_from_task_context(task, original_message, base_datetime):
    context = get_context_for_task(task, original_message)
    context_normalized = normalize_text(context)

    weekdays = {
        "segunda": 0,
        "terca": 1,
        "quarta": 2,
        "quinta": 3,
        "sexta": 4,
        "sabado": 5,
        "domingo": 6,
    }

    target_weekday = None

    for weekday_name, weekday_number in weekdays.items():
        if weekday_name in context_normalized:
            target_weekday = weekday_number
            break

    if target_weekday is None:
        if "amanha" in context_normalized:
            target_weekday = (base_datetime + timedelta(days=1)).weekday()
        elif "hoje" in context_normalized:
            target_weekday = base_datetime.weekday()
        else:
            return None, None, context

    target_date = resolve_target_date_from_context(
        context_normalized=context_normalized,
        base_datetime=base_datetime,
        target_weekday=target_weekday,
    )

    time_range = extract_time_range_from_text(context_normalized)

    if time_range:
        start_hour, start_minute, end_hour, end_minute = time_range

        start_datetime = datetime.combine(
            target_date,
            datetime.min.time(),
            TZ,
        ).replace(
            hour=start_hour,
            minute=start_minute,
        )

        end_datetime = datetime.combine(
            target_date,
            datetime.min.time(),
            TZ,
        ).replace(
            hour=end_hour,
            minute=end_minute,
        )

        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)

        inferred_duration_minutes = int(
            (end_datetime - start_datetime).total_seconds() / 60
        )

        return start_datetime, inferred_duration_minutes, context

    explicit_time = extract_single_time_from_text(context_normalized)

    if explicit_time:
        hour, minute = explicit_time

        start_datetime = datetime.combine(
            target_date,
            datetime.min.time(),
            TZ,
        ).replace(
            hour=hour,
            minute=minute,
        )

        return start_datetime, None, context

    preferred_time_of_day = task.get("preferred_time_of_day")
    title = task.get("title") or ""
    category = task.get("category") or "personal"

    if "manha" in context_normalized:
        preferred_time_of_day = "morning"
    elif "tarde" in context_normalized:
        preferred_time_of_day = "afternoon"
    elif "noite" in context_normalized:
        preferred_time_of_day = "evening"

    hour, minute = default_time_for_task(
        title=title,
        category=category,
        preferred_time_of_day=preferred_time_of_day,
    )

    start_datetime = datetime.combine(
        target_date,
        datetime.min.time(),
        TZ,
    ).replace(
        hour=hour,
        minute=minute,
    )

    return start_datetime, None, context


def process_assistant_message(
    message: str,
    preferences: dict | None = None,
) -> dict:
    now = datetime.now(TZ)
    context_end = now + timedelta(days=14)

    calendar_context = list_calendar_events_for_context(
      now.isoformat(),
      context_end.isoformat()
    )

    try:
        action = parse_user_message(
            message,
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

    if preferences and hasattr(preferences, "model_dump"):
        preferences = preferences.model_dump()
    elif preferences and hasattr(preferences, "dict"):
        preferences = preferences.dict()

    action_type = action.get("action")
    category = action.get("category") or "personal"

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
                days=get_planning_days_for_request(7, message, now),
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

            inferred_start_datetime, inferred_duration_minutes, task_context = infer_fixed_datetime_from_task_context(
                task={
                    "title": title,
                    "category": category,
                    "preferred_time_of_day": action.get("preferred_time_of_day")
                },
                original_message=message,
                base_datetime=datetime.now(TZ)
            )

            if inferred_start_datetime:
                start_datetime = inferred_start_datetime

                if inferred_duration_minutes:
                    duration_minutes = inferred_duration_minutes

            start_datetime, end_datetime = adjust_today_datetime_if_needed(
                start_datetime=start_datetime,
                duration_minutes=duration_minutes,
                original_context=message,
                preferences=preferences,
                now=datetime.now(TZ)
            )

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

        scheduled_time = start_datetime.strftime("%d/%m/%Y às %H:%M")
        event_link = None

        if isinstance(created_event, dict):
            event_link = created_event.get("htmlLink")

        response_message = (
            f"Lembrete criado: {title}\n"
            f"📅 {scheduled_time}"
        )

        if event_link:
            response_message += f"\n🔗 {event_link}"

        return {
            "status": "success",
            "message": response_message,
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
        days = get_planning_days_for_request(7, message, now)
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
            task_days = get_planning_days_for_request(
                task.get("days") or days,
                message,
                now
            )
            category = task.get("category") or "personal"

            # Create this list before any branch uses it.
            task_created_events = []

            task_frequency = task.get("frequency") or "weekly"

            if task_frequency == "daily" and has_current_week_phrase(message):
                sessions_count = min(sessions_count, task_days)

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

            inferred_start_datetime, inferred_duration_minutes, task_context = infer_fixed_datetime_from_task_context(
                task=task,
                original_message=message,
                base_datetime=now
            )

            # Important:
            # Only fixed/one-off events should be overridden by weekday/date phrases.
            # Recurring tasks like piano every day or gym 3x/week must stay flexible
            # and go through the scheduler.
            is_recurring_task = (
                task_frequency in ["daily", "weekly"]
                and sessions_count > 1
            )

            if inferred_start_datetime and not is_recurring_task:
                fixed_start_datetime = inferred_start_datetime

                if inferred_duration_minutes:
                    duration_minutes = inferred_duration_minutes

                task_frequency = "once"

            if task_frequency == "once" and fixed_start_datetime:
                try:
                    start_datetime = fixed_start_datetime

                    start_datetime, end_datetime = adjust_today_datetime_if_needed(
                        start_datetime=start_datetime,
                        duration_minutes=duration_minutes,
                        original_context=task_context,
                        preferences=preferences,
                        now=datetime.now(TZ)
                    )

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

        now = datetime.now(TZ)
        days = get_planning_days_for_request(
            action.get("days") or 7,
            message,
            now
        )
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
