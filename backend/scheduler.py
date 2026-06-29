from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse

TIMEZONE = "Europe/Lisbon"
TZ = ZoneInfo(TIMEZONE)


def parse_datetime(value: str) -> datetime:
    dt = isoparse(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)

    return dt.astimezone(TZ)


def overlaps(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and start_b < end_a


def round_up_to_next_15_minutes(dt: datetime) -> datetime:
    minutes_to_add = (15 - dt.minute % 15) % 15

    rounded = dt + timedelta(minutes=minutes_to_add)

    return rounded.replace(second=0, microsecond=0)


def get_daily_windows(day_date):
    weekday = day_date.weekday()

    # Monday-Friday
    if weekday < 5:
        return [
            (
                datetime.combine(day_date, time(17, 0), TZ),
                datetime.combine(day_date, time(23, 30), TZ)
            )
        ]

    # Saturday-Sunday
    return [
        (
            datetime.combine(day_date, time(10, 0), TZ),
            datetime.combine(day_date, time(23, 30), TZ)
        )
    ]


def find_daily_slots(busy_periods, duration_minutes: int, days: int):
    duration = timedelta(minutes=duration_minutes)

    busy_ranges = [
        (
            parse_datetime(period["start"]),
            parse_datetime(period["end"])
        )
        for period in busy_periods
    ]

    now = datetime.now(TZ)
    today = now.date()

    selected_slots = []

    for day_offset in range(days):
        current_day = today + timedelta(days=day_offset)
        windows = get_daily_windows(current_day)

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
                    selected_slots.append({
                        "start": candidate_start.isoformat(),
                        "end": candidate_end.isoformat()
                    })
                    break

                candidate_start += timedelta(minutes=15)

            if len(selected_slots) >= day_offset + 1:
                break

    return selected_slots