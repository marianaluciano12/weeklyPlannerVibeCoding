from typing import Literal, Optional

from pydantic import BaseModel


class PlanningPreferences(BaseModel):
    weekday_start: str = "17:00"
    weekday_end: str = "22:30"
    weekend_start: str = "10:00"
    weekend_end: str = "22:00"
    minimum_gap_minutes: int = 15
    default_reminder_minutes: int = 10
    preferred_time_of_day: Literal[
        "earliest",
        "morning",
        "afternoon",
        "evening",
        "balanced"
    ] = "balanced"
    avoid_after: str = "21:30"


class AssistantRequest(BaseModel):
    message: str
    preferences: Optional[PlanningPreferences] = None