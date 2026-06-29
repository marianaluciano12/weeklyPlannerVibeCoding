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


def parse_user_message(message: str) -> dict:
    now = datetime.now(ZoneInfo(TIMEZONE)).isoformat()

    prompt = f"""
You are a personal calendar assistant.

Your job is to convert the user's message into ONE structured JSON action.

Current datetime: {now}
Timezone: {TIMEZONE}

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
  "action": "create_reminder" | "schedule_habit" | "unknown",
  "title": string | null,
  "start_datetime": string | null,
  "duration_minutes": integer | null,
  "frequency": "once" | "daily" | null,
  "days": integer | null,
  "notes": string | null
}}

Rules:
- Always return ISO 8601 datetime strings.
- Use the timezone {TIMEZONE}.
- For reminders with no exact time, use 09:00.
- For create_reminder, duration_minutes should be 10.
- For "per day each week", use frequency "daily" and days 7.
- For schedule_habit, start_datetime can be null because the backend will find the best slots.
- Make the title short and calendar-friendly.

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
            "notes": "Could not parse LLM response."
        }