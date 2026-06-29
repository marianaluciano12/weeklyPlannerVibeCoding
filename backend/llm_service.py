import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Europe/Lisbon")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def clean_json(text: str) -> str:
    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


def parse_user_message(message: str, calendar_context=None) -> dict:
    now = datetime.now(ZoneInfo(TIMEZONE)).isoformat()
    calendar_context = calendar_context or []

    calendar_context_text = "\n".join(
        [
            f"- {event['title']}: {event['start']} to {event['end']}"
            for event in calendar_context
        ]
    )

    if not calendar_context_text:
        calendar_context_text = "No upcoming events found."

    prompt = f"""
You are a personal calendar assistant.

Your job is to convert the user's message into ONE structured JSON action.

Current datetime: {now}
Timezone: {TIMEZONE}

Upcoming calendar events:
{calendar_context_text}

Allowed actions:

1. create_reminder
Use this when the user asks to be reminded of something once.
Example:
"remind me to buy milk in 3 days"

2. schedule_habit
Use this when the user wants to schedule repeated time for a hobby, habit, exercise, study, etc.
Example:
"I want to dedicate 20 min per day each week to play the piano"

3. unknown
Use this when you cannot understand the user's request.

Return ONLY valid JSON.

JSON schema:
{{
  "action": "create_reminder" | "schedule_habit" | "schedule_plan" | "unknown",
  "title": string | null,
  "start_datetime": string | null,
  "duration_minutes": integer | null,
  "frequency": "once" | "daily" | "weekly" | null,
  "days": integer | null,
  "category": "hobby" | "errand" | "exercise" | "work" | "chore" | "health" | "study" | "relationship" | "personal" | null,
  "tasks": [
    {{
      "title": string,
      "duration_minutes": integer,
      "sessions_count": integer,
      "frequency": "daily" | "weekly",
      "days": integer,
      "category": "hobby" | "errand" | "exercise" | "work" | "chore" | "health" | "study" | "relationship" | "personal",
      "preferred_time_of_day": "earliest" | "morning" | "afternoon" | "evening" | "balanced",
      "allowed_days": "any" | "weekdays" | "weekends",
      "preferred_window_start": string | null,
      "preferred_window_end": string | null,
      "notes": string | null
    }}
  ] | null,
  "notes": string | null
}}

Rules:
- Always return ISO 8601 datetime strings.
- Use the timezone {TIMEZONE}.
- For reminders with no exact time, use 09:00.
- For create_reminder, duration_minutes should be 30.
- For "per day each week", use frequency "daily" and days 7.
- For schedule_habit, start_datetime can be null because the backend will find the best slots.
- Make the title short and calendar-friendly.

Calendar context rules:
- Use the upcoming calendar events to resolve phrases like "after my piano appointment", "before my dentist appointment", "after work", or "after my meeting".
- If the user says "after [event]", schedule the reminder after that event ends.
- If the user says "before [event]", schedule the reminder before that event starts.
- If the user does not specify how long after, use 15 minutes after the referenced event ends.
- If the user says "right after" or "immediately after", use the exact event end time.
- If the user mentions an event name partially, match it to the closest upcoming calendar event title.
- If no matching event is found, use 09:00 as the fallback time.

Category rules:
- piano, reading, music, drawing, gaming = hobby
- groceries, shopping, buying something, pharmacy = errand
- gym, running, walking, workout, yoga = exercise
- meetings, calls, work tasks, code, course = work
- cleaning, laundry, dishes, house tasks = chore
- doctor, dentist, medicine, health appointments = health
- studying, learning, assignments, exams = study
- date night, romantic plans, relationship time = relationship
- social events, parties, gatherings = social
- if unsure, use personal

Multi-task planning rules:
- If the user asks for more than one thing to be scheduled, use action "schedule_plan".
- For schedule_plan, put every activity inside the tasks array.
- For "every day of the week", use sessions_count 7, frequency "daily", days 7.
- For "3 times per week", use sessions_count 3, frequency "weekly", days 7.
- If duration is missing:
  - gym/exercise = 60 minutes
  - errands = 30 minutes
  - chores = 30 minutes
  - hobbies = 30 minutes
  - study = 45 minutes
- If the user says "morning", use preferred_time_of_day "morning".
- If the user says "before work", use allowed_days "weekdays", preferred_window_start "8:00", preferred_window_end "09:00".
- If there is no specific preference, use preferred_time_of_day "balanced", allowed_days "any", preferred_window_start null, preferred_window_end null.

User message:
{message}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    raw_text = response.text or "{}"
    json_text = clean_json(raw_text)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return {
             "action": "unknown",
    "title": None,
    "start_datetime": None,
    "duration_minutes": None,
    "frequency": None,
    "days": None,
    "category": None,
    "tasks": None,
    "notes": "Could not parse LLM response."
        }