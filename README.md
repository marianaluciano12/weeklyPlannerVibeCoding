# AI Calendar Assistant / Calendar Planner

A full-stack web app that displays your Google Calendar and includes an AI assistant textbox for natural-language planning.

The assistant can understand requests such as:

- "Remind me to buy milk in 3 days"
- "Remind me to buy eggs tomorrow after my piano appointment"
- "I want to dedicate 20 min per day each week to play the piano"
- "I want to play the piano for 20 min every day of the week. I also want to go to the gym 3 times per week. I prefer in the mornings before work."

The app uses:

- **Frontend:** React + Vite + FullCalendar
- **Backend:** Python + FastAPI
- **AI/LLM:** Gemini API
- **Calendar integration:** Google Calendar API

---

## Current Features

The current version can:

1. Display Google Calendar events in a calendar interface.
2. Use week view as the preferred main calendar view.
3. Send natural language commands to an AI assistant.
4. Convert user messages into structured calendar actions.
5. Create reminders in Google Calendar.
6. Schedule habits and routines into available calendar slots.
7. Schedule multiple weekly activities from one message.
8. Use real calendar context to understand phrases like:
   - "after my piano appointment"
   - "before my dentist appointment"
   - "after my meeting"
9. Use planning preferences from the frontend:
   - weekday availability
   - weekend availability
   - minimum gap between events
   - default reminder time
   - preferred planning style
   - avoid scheduling after a selected time
10. Categorize events automatically.
11. Add emojis and colors to events based on category.
12. Show a custom event popup when clicking an event.
13. Show event details directly inside the popup.
14. Include an **Edit event** button placeholder.
15. Delete events from Google Calendar from the popup.
16. Show a visual summary after creating a weekly plan.
17. Refresh the calendar after creating or deleting events.

---

## Project Structure

```txt
ai-calendar-assistant/
  package.json

  backend/
    .env                  # Not included in GitHub
    .gitignore
    requirements.txt
    credentials.json       # Not included in GitHub
    token.json             # Not included in GitHub, generated locally
    main.py
    models.py
    calendar_service.py
    llm_service.py
    scheduler.py
    auth_test.py

  frontend/
    package.json
    src/
      App.jsx
      App.css
      main.jsx
```

---

## Important Security Notes

Do **not** upload these files to GitHub:

```txt
backend/.env
backend/credentials.json
backend/token.json
backend/venv/
```

These files contain API keys, OAuth credentials, or local environment data.

Each person testing the project should create their own:

1. Google Calendar API OAuth credentials
2. Gemini API key
3. `.env` file

---

## Prerequisites

Before running the project, install:

- Python 3.10 or newer
- Node.js 18 or newer
- npm
- Git
- A Google account
- A Gemini API key from Google AI Studio

---

## 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd ai-calendar-assistant
```

Replace `YOUR_REPOSITORY_URL` with the real GitHub repository URL.

---

## 2. Backend Setup

Go to the backend folder:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include:

```txt
fastapi
uvicorn[standard]
python-dotenv
pydantic
google-api-python-client
google-auth-oauthlib
google-auth-httplib2
google-genai
python-dateutil
tzdata
```

If there is a timezone error related to `Europe/Lisbon`, install:

```bash
pip install tzdata
```

---

## 3. Create a Gemini API Key

1. Go to Google AI Studio: https://aistudio.google.com/
2. Create or select a project.
3. Create an API key.
4. Copy the API key.
5. Save it in the backend `.env` file.

---

## 4. Enable Google Calendar API

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new Google Cloud project, or select an existing project.
3. Search for **Google Calendar API**.
4. Click **Enable**.

---

## 5. Configure Google OAuth Consent Screen

In Google Cloud Console:

1. Go to **Google Auth Platform** or **OAuth consent screen**.
2. Choose **External** if asked.
3. Fill in the required app information:
   - App name: `AI Calendar Assistant`
   - User support email: your email
   - Developer contact email: your email
4. Add the required scopes if requested.

The app uses this Google Calendar scope:

```txt
https://www.googleapis.com/auth/calendar
```

This scope allows the app to read, create and delete Google Calendar events.

### If the app is in Testing mode

If your OAuth app is still in **Testing**, add the Google account that will test the app as a **Test user**.

For a school project, the easiest option is usually for each tester to create their own Google Cloud credentials.

---

## 6. Create Google OAuth Credentials

In Google Cloud Console:

1. Go to **Google Auth Platform** > **Clients**.
2. Click **Create client**.
3. Select **Desktop app**.
4. Name it something like:

```txt
AI Calendar Assistant Local Test
```

5. Download the JSON credentials file.
6. Rename it to:

```txt
credentials.json
```

7. Place it inside the backend folder:

```txt
backend/credentials.json
```

The app expects this file to exist at that exact location.

---

## 7. Create the `.env` File

Inside the `backend/` folder, create a file named:

```txt
.env
```

Add this:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TIMEZONE=Europe/Lisbon
GOOGLE_CALENDAR_ID=primary
```

Replace `your_gemini_api_key_here` with your real Gemini API key.

---

## 8. Test Google Calendar Authentication

From the `backend/` folder, with the virtual environment activated, run:

```bash
python auth_test.py
```

A browser window should open asking you to log in with your Google account.

After successful login, the app creates:

```txt
backend/token.json
```

This file stores the local OAuth token. Do not upload `token.json` to GitHub.

If authentication works, you should see a list of calendars in the terminal.

---

## 9. Run the Backend Only

From the `backend/` folder:

```bash
uvicorn main:app --reload
```

Then open:

```txt
http://127.0.0.1:8000
```

Expected response:

```json
{
  "message": "AI Calendar Assistant backend is running."
}
```

---

## 10. Frontend Setup

Open a new terminal and go to the frontend folder:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Run the frontend:

```bash
npm run dev
```

Open the URL shown in the terminal. Usually it is:

```txt
http://localhost:5173
```

---

## 11. Run Backend and Frontend Together

This project can also run both backend and frontend using one command from the root folder.

Go to the project root:

```bash
cd ai-calendar-assistant
```

Install root dependencies:

```bash
npm install
```

Then run:

```bash
npm run dev
```

The root `package.json` can use this Windows setup:

```json
{
  "scripts": {
    "dev": "concurrently -k -n backend,frontend \"npm run backend\" \"npm run frontend\"",
    "backend": "cd backend && .\\venv\\Scripts\\python.exe -m uvicorn main:app --reload",
    "frontend": "cd frontend && npm run dev"
  },
  "devDependencies": {
    "concurrently": "^9.0.0"
  }
}
```

For macOS/Linux, use this version:

```json
{
  "scripts": {
    "dev": "concurrently -k -n backend,frontend \"npm run backend\" \"npm run frontend\"",
    "backend": "cd backend && ./venv/bin/python -m uvicorn main:app --reload",
    "frontend": "cd frontend && npm run dev"
  },
  "devDependencies": {
    "concurrently": "^9.0.0"
  }
}
```

---

## 12. How to Test the App

After both backend and frontend are running:

1. Open the frontend in the browser:

```txt
http://localhost:5173
```

2. Confirm that Google Calendar events are visible.
3. Use the assistant textbox to create reminders, habits or weekly plans.
4. Click an event to open the custom event popup.
5. Use the popup to view details, use the placeholder edit button, or delete the event.

---

## 13. Main Features Explained

### Calendar Display

The frontend uses FullCalendar to display Google Calendar events.

The preferred view is week view because it gives a better overview of the weekly schedule.

### AI Assistant

The assistant receives a natural language message and sends it to the backend.

The backend uses Gemini to convert the message into structured JSON, such as:

```json
{
  "action": "create_reminder",
  "title": "Buy milk",
  "start_datetime": "2026-07-02T09:00:00+01:00",
  "duration_minutes": 30,
  "frequency": "once",
  "days": null,
  "category": "errand",
  "tasks": null,
  "notes": null
}
```

### Calendar-Aware Reminders

The backend passes upcoming calendar events to Gemini as context.

This allows the assistant to understand requests like:

```txt
remind me to buy eggs tomorrow after my piano appointment
```

If the piano event is tomorrow from 16:00 to 17:00, the assistant should schedule the reminder after that event, for example around 17:15.

### Smart Scheduling Preferences

The frontend includes planning preferences, such as:

- weekday start time
- weekday end time
- weekend start time
- weekend end time
- minimum gap between events
- default reminder time
- preferred planning style
- avoid scheduling after a certain time

These preferences are sent to the backend with each assistant request.

### Multi-Task Weekly Planning

The assistant can schedule multiple activities from one message.

Example:

```txt
I want to play the piano for 20 min every day of the week. I also want to go to the gym 3 times per week. I prefer in the mornings before work.
```

The backend schedules each task while avoiding:

- existing Google Calendar events
- newly created events from the same plan
- user preference conflicts
- minimum gap conflicts

### Plan Summary

After creating a weekly plan, the frontend shows a grouped visual summary.

Example:

```txt
Created plan

🏋️ Gym
Mon, 07:30
Wed, 07:15
Fri, 08:00

🎹 Piano
Mon, 18:30
Tue, 19:00
Wed, 18:45
...
```

### Event Categories and Colors

The assistant categorizes events automatically.

Supported categories:

```txt
hobby
errand
exercise
work
chore
health
study
relationship
personal
```

Examples:

```txt
🎹 Hobby
🛒 Errand
🏋️ Exercise
💼 Work
🧺 Chore
🩺 Health
📚 Study
❤️ Relationship
✨ Personal
```

The backend stores the category in Google Calendar private extended properties and returns color data to the frontend.

### Event Popup

Clicking an event opens a custom popup.

The popup shows:

- title
- start time
- end time
- category
- edit button placeholder
- delete button

The edit button is currently a placeholder for a future feature.

### Event Deletion

The delete button calls:

```txt
DELETE /events/{event_id}
```

The backend deletes the event from Google Calendar and the frontend refreshes the calendar.

---

## 14. API Endpoints

### Health check

```txt
GET /
```

Returns:

```json
{
  "message": "AI Calendar Assistant backend is running."
}
```

### Get calendar events

```txt
GET /events?start={start_datetime}&end={end_datetime}
```

Example:

```txt
GET /events?start=2026-06-29T00:00:00%2B01:00&end=2026-07-06T00:00:00%2B01:00
```

Returns events formatted for FullCalendar, including category colors and extended properties.

### Send message to assistant

```txt
POST /assistant
```

Request body:

```json
{
  "message": "I want to play piano every day this week",
  "preferences": {
    "weekday_start": "17:00",
    "weekday_end": "22:30",
    "weekend_start": "10:00",
    "weekend_end": "22:00",
    "minimum_gap_minutes": 15,
    "default_reminder_minutes": 10,
    "preferred_time_of_day": "balanced",
    "avoid_after": "21:30"
  }
}
```

### Delete calendar event

```txt
DELETE /events/{event_id}
```

Example:

```txt
DELETE /events/abc123googlecalendarid
```

Deletes the selected event from Google Calendar.

---

## 15. Examples to Try

### Basic reminder

```txt
remind me to buy milk in 3 days
```

Expected result:

- creates one reminder/event
- category should be errand
- event should appear with an errand color and emoji

### Reminder with a specific day

```txt
remind me to call my mom tomorrow at 18:00
```

Expected result:

- creates one reminder tomorrow at 18:00
- category should probably be personal or relationship

### Calendar-aware reminder

```txt
remind me to buy eggs tomorrow after my piano appointment
```

Expected result:

- backend reads upcoming Google Calendar events
- Gemini matches "piano appointment"
- reminder is scheduled after the piano event ends

### Habit scheduling

```txt
I want to dedicate 20 min per day each week to play the piano
```

Expected result:

- creates 7 piano sessions
- uses calendar availability
- avoids busy periods
- category should be hobby

### Exercise scheduling

```txt
schedule gym 3 times this week
```

Expected result:

- creates 3 gym sessions
- category should be exercise
- schedules around existing calendar events

### Exercise with preference

```txt
I want to go to the gym 3 times per week. I prefer in the mornings before work.
```

Expected result:

- creates 3 gym sessions
- tries to schedule them on weekday mornings
- category should be exercise

### Multi-task weekly plan

```txt
I want to play the piano for 20 min every day of the week. I also want to go to the gym 3 times per week. I prefer in the mornings before work.
```

Expected result:

- creates piano sessions every day
- creates 3 gym sessions
- avoids overlap between piano, gym and existing calendar events
- shows a grouped plan summary after creation

### Chore reminder

```txt
remind me to clean the kitchen tomorrow
```

Expected result:

- creates one reminder
- category should be chore
- event should appear with chore styling

### Health reminder

```txt
remind me to book a dentist appointment next Monday
```

Expected result:

- creates one reminder
- category should be health

### Relationship planning

```txt
schedule a date night this Friday evening
```

Expected result:

- creates an event on Friday evening if possible
- category should be relationship

### Event popup

Click any event in the calendar.

Expected result:

- custom popup opens
- shows event details immediately
- shows Edit event button
- shows Delete event button

### Event deletion

1. Click any event.
2. Click **Delete event**.
3. Confirm deletion.
4. Event should disappear from the calendar.
5. Event should also be deleted from Google Calendar.

---

## 16. How the AI Assistant Works

The LLM does not directly access Google Calendar.

Instead, the system works like this:

```txt
User message
  ↓
Backend reads upcoming calendar events for context
  ↓
Gemini interprets the message
  ↓
Gemini returns structured JSON
  ↓
Python validates the action
  ↓
Backend executes the calendar action through Google Calendar API
  ↓
Frontend refreshes the calendar
```

For weekly multi-task planning:

```txt
User asks for multiple activities
  ↓
Gemini returns schedule_plan with a tasks array
  ↓
Backend sorts tasks by scheduling difficulty
  ↓
Backend finds slots for each task
  ↓
Each newly created slot is added to the temporary busy list
  ↓
Next tasks avoid both real calendar events and newly created events
  ↓
Frontend shows a grouped plan summary
```

For event deletion:

```txt
User clicks an event
  ↓
Frontend opens event popup
  ↓
User clicks Delete event
  ↓
Frontend calls DELETE /events/{event_id}
  ↓
Backend deletes the event through Google Calendar API
  ↓
Calendar refreshes
```

---

## 17. Troubleshooting

### Error: `No time zone found with key Europe/Lisbon`

Install `tzdata`:

```bash
pip install tzdata
```

Also make sure this line exists in `requirements.txt`:

```txt
tzdata
```

Do not write this inside `requirements.txt`:

```txt
pip install tzdata
```

That is a terminal command, not a package name.

### Error: `Invalid requirement: 'pip install tzdata'`

Open `backend/requirements.txt` and replace:

```txt
pip install tzdata
```

with:

```txt
tzdata
```

Then run:

```bash
pip install -r requirements.txt
```

### Error: `The system cannot find the path specified`

This usually means the root `package.json` is pointing to the wrong virtual environment path.

Check if this file exists:

```txt
backend/venv/Scripts/python.exe
```

On Windows, your backend script should be:

```json
"backend": "cd backend && .\\venv\\Scripts\\python.exe -m uvicorn main:app --reload"
```

On macOS/Linux, it should be:

```json
"backend": "cd backend && ./venv/bin/python -m uvicorn main:app --reload"
```

### Error: `ValueError: Invalid format specifier`

This usually happens in `llm_service.py` when JSON braces are used inside an f-string.

Inside an f-string, JSON examples must use double braces:

```python
{{
  "action": "create_reminder"
}}
```

not:

```python
{
  "action": "create_reminder"
}
```

### Google OAuth says app is not verified

This is normal for local development.

If the app is in testing mode, make sure the Google account being used is added as a test user.

For a school project, the tester can also create their own Google Cloud credentials and use their own `credentials.json`.

### Calendar does not show events

Check:

1. Backend is running on:

```txt
http://127.0.0.1:8000
```

2. Frontend is running on:

```txt
http://localhost:5173
```

3. `backend/.env` contains:

```env
GOOGLE_CALENDAR_ID=primary
```

4. `main.py` allows the frontend origin:

```python
allow_origins=[
    "http://localhost:5173"
]
```

5. You are looking at the correct calendar week.

If the backend returns events but the calendar looks empty, switch to week view or check the browser console.

### Gemini request fails

Check:

1. `.env` exists inside `backend/`
2. `GEMINI_API_KEY` is correct
3. The backend server was restarted after editing `.env`
4. Your Gemini API key is enabled and valid

### Event deletion does not work

Check:

1. The backend includes this endpoint:

```python
@app.delete("/events/{event_id}")
```

2. `calendar_service.py` includes a function that calls:

```python
service.events().delete(...)
```

3. The frontend `FullCalendar` component includes:

```jsx
eventClick={openEventPopup}
```

4. The Google Calendar scope is:

```txt
https://www.googleapis.com/auth/calendar
```

If you previously authenticated with a more limited scope, delete `backend/token.json` and run `python auth_test.py` again.

---

## 18. Notes for Evaluation

This project demonstrates:

- Full-stack development
- React frontend development
- Python FastAPI backend development
- Google Calendar OAuth
- Google Calendar API integration
- Gemini API integration
- Prompt engineering
- LLM-powered intent parsing
- Calendar-aware AI reasoning
- Smart scheduling logic
- User planning preferences
- Multi-task weekly planning
- Calendar CRUD operations: read, create and delete
- Frontend state management
- Custom UI interactions and modal design
- Practical AI assistant workflow

The main architectural decision is:

> The LLM interprets the user's intent, but the backend validates and executes calendar actions.

This keeps the app safer, easier to debug, and more realistic as a personal calendar assistant.

---

## 19. Future Improvements

Possible next features:

1. Fully implement event editing.
2. Add confirmation before creating events.
3. Add drag-and-drop rescheduling.
4. Add recurring Google Calendar events.
5. Save user preferences persistently.
6. Add authentication for multiple users.
7. Add a weekly reset/planning dashboard.
8. Add "find free time" without creating events.
9. Add "clear my evening" or "reschedule my week" commands.
10. Add more advanced scoring for sleep, gym, meals and energy levels.

---

## 20. Useful Documentation

- Google Calendar API Python Quickstart: https://developers.google.com/workspace/calendar/api/quickstart/python
- Google Calendar FreeBusy API: https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- Google Calendar Events API: https://developers.google.com/workspace/calendar/api/v3/reference/events
- Gemini API Keys: https://ai.google.dev/gemini-api/docs/api-key
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- FullCalendar React Docs: https://fullcalendar.io/docs/react
