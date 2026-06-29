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


CATEGORY_STYLES = {
    "hobby": {
        "emoji": "🎹",
        "backgroundColor": "#efe4ff",
        "borderColor": "#7c3aed",
        "textColor": "#3b0764",
    },
    "errand": {
        "emoji": "🛒",
        "backgroundColor": "#dcfce7",
        "borderColor": "#16a34a",
        "textColor": "#14532d",
    },
    "exercise": {
        "emoji": "🏋️",
        "backgroundColor": "#ffedd5",
        "borderColor": "#f97316",
        "textColor": "#7c2d12",
    },
    "work": {
        "emoji": "💼",
        "backgroundColor": "#dbeafe",
        "borderColor": "#2563eb",
        "textColor": "#1e3a8a",
    },
    "chore": {
        "emoji": "🧺",
        "backgroundColor": "#fef9c3",
        "borderColor": "#ca8a04",
        "textColor": "#713f12",
    },
    "health": {
        "emoji": "🩺",
        "backgroundColor": "#ffe4e6",
        "borderColor": "#e11d48",
        "textColor": "#881337",
    },
    "study": {
        "emoji": "📚",
        "backgroundColor": "#e0e7ff",
        "borderColor": "#4f46e5",
        "textColor": "#312e81",
    },
    "relationship": {
        "emoji": "❤️",
        "backgroundColor": "#fce7f3",
        "borderColor": "#db2777",
        "textColor": "#831843",
    },
    "personal": {
        "emoji": "✨",
        "backgroundColor": "#f1f5f9",
        "borderColor": "#64748b",
        "textColor": "#334155",
    },
    "social": {
        "emoji": "🎉",
        "backgroundColor": "#fffbeb",
        "borderColor": "#f59e0b",
        "textColor": "#78350f",
    }
}

def normalize_category(category: str | None) -> str:
    if not category:
        return "personal"

    category = category.lower().strip()

    if category in CATEGORY_STYLES:
        return category

    return "personal"


def infer_category_from_title(title: str) -> str:
    title_lower = title.lower()

    if any(word in title_lower for word in ["piano", "música", "musica", "leitura", "ler", "jogar", "desenhar"]):
        return "hobby"

    if any(word in title_lower for word in ["comprar", "leite", "ovos", "supermercado", "compras", "farmácia", "farmacia"]):
        return "errand"

    if any(word in title_lower for word in ["ginásio", "ginasio", "treino", "correr", "corrida", "caminhada", "yoga"]):
        return "exercise"

    if any(word in title_lower for word in ["reunião", "reuniao", "chamada", "trabalho", "código", "codigo", "curso", "aula"]):
        return "work"

    if any(word in title_lower for word in ["limpar", "limpeza", "roupa", "lavandaria", "loiça", "loica", "casa"]):
        return "chore"

    if any(word in title_lower for word in ["médico", "medico", "dentista", "consulta", "saúde", "saude", "medicamento"]):
        return "health"

    if any(word in title_lower for word in ["estudar", "estudo", "exame", "trabalho de casa", "aprender"]):
        return "study"

    if any(word in title_lower for word in ["encontro", "date", "romântico", "romantico", "casal", "relação", "relacao"]):
        return "relationship"

    return "personal"


def format_event_title(title: str, category: str) -> str:
    style = CATEGORY_STYLES[category]
    emoji = style["emoji"]

    if title.startswith(emoji):
        return title

    return f"{emoji} {title}"


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

        title = event.get("summary", "Untitled event")

        stored_category = (
            event.get("extendedProperties", {})
            .get("private", {})
            .get("category")
        )

        category = normalize_category(stored_category)

        if category == "personal":
            category = infer_category_from_title(title)

        style = CATEGORY_STYLES[category]

        formatted_events.append({
            "id": event.get("id"),
            "title": format_event_title(title, category),
            "start": start,
            "end": end,
            "backgroundColor": style["backgroundColor"],
            "borderColor": style["borderColor"],
            "textColor": style["textColor"],
            "extendedProps": {
                "category": category,
                "emoji": style["emoji"],
                "originalTitle": title,
            }
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
    reminder_minutes_before: int = 10,
    category: Optional[str] = None
):
    service = get_calendar_service()
    category = normalize_category(category)
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
        "extendedProperties": {
            "private": {
                "createdBy": "AI Calendar Assistant",
                "category": category,
            }
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

    style = CATEGORY_STYLES[category]

    return {
        "id": created_event.get("id"),
        "title": format_event_title(created_event.get("summary"), category),
        "start": created_event.get("start", {}).get("dateTime"),
        "end": created_event.get("end", {}).get("dateTime"),
        "category": category,
        "emoji": style["emoji"],
        "backgroundColor": style["backgroundColor"],
        "borderColor": style["borderColor"],
        "textColor": style["textColor"],
        "htmlLink": created_event.get("htmlLink"),
    }



def delete_calendar_event(event_id: str):
    service = get_calendar_service()

    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=event_id
    ).execute()

    return {
        "id": event_id,
        "deleted": True
    }

def list_calendar_events_for_context(time_min: str, time_max: str):
    service = get_calendar_service()

    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = result.get("items", [])

    context_events = []

    for event in events:
        title = event.get("summary", "Untitled event")
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")

        context_events.append({
            "title": title,
            "start": start,
            "end": end,
        })

    return context_events