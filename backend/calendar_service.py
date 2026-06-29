import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"

TIMEZONE = os.getenv("TIMEZONE", "Europe/Lisbon")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")


def get_calendar_service():
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def list_calendar_events(time_min: str, time_max: str):
    service = get_calendar_service()

    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = result.get("items", [])

    formatted_events = []

    for event in events:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")

        formatted_events.append({
            "id": event.get("id"),
            "title": event.get("summary", "Untitled event"),
            "start": start,
            "end": end,
        })

    return formatted_events


def get_free_busy(time_min: str, time_max: str):
    service = get_calendar_service()

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": TIMEZONE,
        "items": [
            {"id": CALENDAR_ID}
        ]
    }

    result = service.freebusy().query(body=body).execute()

    return result["calendars"][CALENDAR_ID].get("busy", [])


def create_calendar_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    reminder_minutes_before: int = 10
):
    service = get_calendar_service()

    event_body = {
        "summary": title,
        "description": description or "",
        "start": {
            "dateTime": start_datetime,
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": TIMEZONE,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": reminder_minutes_before
                }
            ]
        }
    }

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event_body
    ).execute()

    return {
        "id": created_event.get("id"),
        "title": created_event.get("summary"),
        "start": created_event.get("start", {}).get("dateTime"),
        "end": created_event.get("end", {}).get("dateTime"),
        "htmlLink": created_event.get("htmlLink"),
    }