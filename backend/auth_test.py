from calendar_service import get_calendar_service

service = get_calendar_service()

calendar_list = service.calendarList().list().execute()

print("Google Calendar connected successfully.")
print("Calendars:")

for calendar in calendar_list.get("items", []):
    print("-", calendar.get("summary"))