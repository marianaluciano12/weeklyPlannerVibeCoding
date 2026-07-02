from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AssistantRequest
from assistant_service import process_assistant_message
from calendar_service import (
    list_calendar_events,
    delete_calendar_event,
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
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
        "deleted_event": deleted_event,
    }


@app.post("/assistant")
def assistant(request: AssistantRequest):
    preferences = None

    if request.preferences:
        if hasattr(request.preferences, "model_dump"):
            preferences = request.preferences.model_dump()
        else:
            preferences = request.preferences.dict()

    return process_assistant_message(
        message=request.message,
        preferences=preferences,
    )
