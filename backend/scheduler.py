import os
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse
from dotenv import load_dotenv

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Europe/Lisbon")
TZ = ZoneInfo(TIMEZONE)

DEFAULT_PREFERENCES = {
    "weekday_start": "17:00",
    "weekday_end": "22:30",
    "weekend_start": "10:00",
    "weekend_end": "22:00",
    "minimum_gap_minutes": 15,
    "default_reminder_minutes": 10,
    "preferred_time_of_day": "balanced",
    "avoid_after": "21:30",
}


def merge_preferences(preferences):
    merged = DEFAULT_PREFERENCES.copy()

    if preferences:
        for key, value in preferences.items():
            if value is not None and value != "":
                merged[key] = value

    return merged


def parse_datetime(value: str) -> datetime:
    dt = isoparse(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)

    return dt.astimezone(TZ)


def parse_time(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def overlaps(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and start_b < end_a


def round_up_to_next_15_minutes(dt: datetime) -> datetime:
    minutes_to_add = (15 - dt.minute % 15) % 15
    rounded = dt + timedelta(minutes=minutes_to_add)
    return rounded.replace(second=0, microsecond=0)


def get_daily_windows(day_date, preferences):
    weekday = day_date.weekday()

    if weekday < 5:
        start = parse_time(preferences["weekday_start"])
        end = parse_time(preferences["weekday_end"])
    else:
        start = parse_time(preferences["weekend_start"])
        end = parse_time(preferences["weekend_end"])

    window_start = datetime.combine(day_date, start, TZ)
    window_end = datetime.combine(day_date, end, TZ)

    if window_start >= window_end:
        return []

    return [(window_start, window_end)]


def get_target_time(day_date, preferences):
    preferred = preferences["preferred_time_of_day"]
    weekday = day_date.weekday()

    if preferred == "morning":
        return datetime.combine(day_date, time(10, 0), TZ)

    if preferred == "afternoon":
        return datetime.combine(day_date, time(15, 0), TZ)

    if preferred == "evening":
        return datetime.combine(day_date, time(19, 0), TZ)

    if preferred == "balanced":
        if weekday < 5:
            return datetime.combine(day_date, time(18, 30), TZ)

        return datetime.combine(day_date, time(11, 0), TZ)

    return None


def score_slot(candidate_start, window_start, day_offset, preferences):
    preferred = preferences["preferred_time_of_day"]
    avoid_after = parse_time(preferences["avoid_after"])

    if preferred == "earliest":
        score = (candidate_start - window_start).total_seconds() / 60
    else:
        target = get_target_time(candidate_start.date(), preferences)

        if target:
            score = abs((candidate_start - target).total_seconds() / 60)
        else:
            score = 0

    # Prefer earlier days slightly, but not too aggressively.
    score += day_offset * 5

    # Penalize events after the user's preferred latest time.
    if candidate_start.time() > avoid_after:
        score += 500

    return score


def find_best_slot_for_day(
    day_date,
    day_offset,
    busy_ranges,
    duration,
    now,
    preferences
):
    windows = get_daily_windows(day_date, preferences)

    best_slot = None
    best_score = float("inf")

    for window_start, window_end in windows:
        candidate_start = window_start

        if candidate_start < now:
            candidate_start = round_up_to_next_15_minutes(now)

        while candidate_start + duration <= window_end:
            candidate_end = candidate_start + duration

            has_conflict = any(
                overlaps(candidate_start, candidate_end, busy_start, busy_end)
                for busy_start, busy_end in busy_ranges
            )

            if not has_conflict:
                score = score_slot(
                    candidate_start,
                    window_start,
                    day_offset,
                    preferences
                )

                if score < best_score:
                    best_score = score
                    best_slot = {
                        "start": candidate_start.isoformat(),
                        "end": candidate_end.isoformat(),
                    }

            candidate_start += timedelta(minutes=15)

    return best_slot


def find_daily_slots(busy_periods, duration_minutes: int, days: int, preferences=None):
    preferences = merge_preferences(preferences)

    duration = timedelta(minutes=duration_minutes)
    minimum_gap = timedelta(minutes=int(preferences["minimum_gap_minutes"]))

    # Expand busy periods by the minimum gap.
    # Example: if an event ends at 18:00 and gap is 15 min,
    # the next task cannot start before 18:15.
    busy_ranges = [
        (
            parse_datetime(period["start"]) - minimum_gap,
            parse_datetime(period["end"]) + minimum_gap
        )
        for period in busy_periods
    ]

    now = datetime.now(TZ)
    today = now.date()

    selected_slots = []

    for day_offset in range(days):
        current_day = today + timedelta(days=day_offset)

        slot = find_best_slot_for_day(
            day_date=current_day,
            day_offset=day_offset,
            busy_ranges=busy_ranges,
            duration=duration,
            now=now,
            preferences=preferences
        )

        if slot:
            selected_slots.append(slot)

    return selected_slots