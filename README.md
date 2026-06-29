# AI Calendar Assistant

A web app that displays a Google Calendar and includes an AI assistant textbox.  
The assistant can understand natural language requests such as:

- "Remind me to buy milk in 3 days"
- "I want to dedicate 20 min per day each week to play the piano"
- "Schedule 30 minutes of reading every day this week"

The app uses:

- **Frontend:** React + Vite + FullCalendar
- **Backend:** Python + FastAPI
- **AI/LLM:** Gemini API
- **Calendar integration:** Google Calendar API

---

## Demo Features

The current MVP can:

1. Display Google Calendar events in a weekly/monthly calendar view.
2. Send natural language commands to an AI assistant.
3. Convert user messages into structured actions.
4. Create reminders in Google Calendar.
5. Find free time slots in Google Calendar.
6. Schedule recurring daily hobby/habit sessions.
7. Refresh the calendar after events are created.

---

## Project Structure

```txt
ai-calendar-assistant/
  package.json

  backend/
    .env.example
    .gitignore
    requirements.txt
    credentials.json        # Not included in GitHub
    token.json              # Not included in GitHub, generated after login
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

The following files should **not** be uploaded to GitHub:

```txt
backend/.env
backend/credentials.json
backend/token.json
backend/venv/
```

These files contain private API keys, OAuth credentials, or local environment data.

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

Replace `YOUR_REPOSITORY_URL` with the actual GitHub repository URL.

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

If there is a timezone error related to `Europe/Lisbon`, make sure `tzdata` is installed:

```bash
pip install tzdata
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

This scope allows the app to read and create Google Calendar events.

### If the app is in Testing mode

If your OAuth app is still in **Testing**, add the Google account that will test the app as a **Test user**.

For example, if your professor is testing with their own Google account, they may need to either:

1. Create their own Google Cloud OAuth credentials, or
2. Be added as a test user in your Google Cloud project.

For most school projects, the easiest option is for each tester to create their own credentials.

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

Replace:

```txt
your_gemini_api_key_here
```

with your real Gemini API key.

Example:

```env
GEMINI_API_KEY=AIza...
TIMEZONE=Europe/Lisbon
GOOGLE_CALENDAR_ID=primary
```

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

This file stores the local OAuth token.

Do not upload `token.json` to GitHub.

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

The root `package.json` should contain something like this for Windows:

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

2. Confirm that calendar events are visible.
3. In the assistant textbox, try:

```txt
remind me to buy milk in 3 days
```

The app should create a calendar event/reminder.

Then try:

```txt
I want to dedicate 20 min per day each week to play the piano
```

The app should:

1. Check busy periods in Google Calendar.
2. Find available time slots.
3. Create one piano event per day for the next 7 days.

---

## 13. API Endpoints

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

### Send message to assistant

```txt
POST /assistant
```

Request body:

```json
{
  "message": "remind me to buy milk in 3 days"
}
```

Example response:

```json
{
  "status": "success",
  "message": "Created reminder: Buy milk",
  "created_events": [],
  "action": {
    "action": "create_reminder",
    "title": "Buy milk"
  }
}
```

---

## 14. How the AI Assistant Works

The LLM does not directly access Google Calendar.

Instead, the system works like this:

```txt
User message
  ↓
Gemini interprets the message
  ↓
Backend receives structured JSON action
  ↓
Python validates the action
  ↓
Google Calendar API creates the event
```

Example:

User writes:

```txt
remind me to buy milk in 3 days
```

Gemini returns a structured action similar to:

```json
{
  "action": "create_reminder",
  "title": "Buy milk",
  "start_datetime": "2026-07-02T09:00:00+01:00",
  "duration_minutes": 10,
  "frequency": "once",
  "days": null,
  "notes": null
}
```

Then the backend creates the calendar event.

---

## 15. Troubleshooting

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

---

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

---

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

---

### Google OAuth says app is not verified

This is normal for local development.

If the app is in testing mode, make sure the Google account being used is added as a test user.

For a school project, the tester can also create their own Google Cloud credentials and use their own `credentials.json`.

---

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

---

### Gemini request fails

Check:

1. `.env` exists inside `backend/`
2. `GEMINI_API_KEY` is correct
3. The backend server was restarted after editing `.env`
4. Your Gemini API key is enabled and valid

---

## 16. Notes for Evaluation

This project demonstrates:

- API integration
- Google Calendar OAuth
- LLM-powered intent parsing
- Prompt engineering
- Python backend development
- React frontend development
- Calendar scheduling logic
- Full-stack communication between frontend and backend

The main architectural decision is:

> The LLM interprets the user's intent, but the backend validates and executes calendar actions.

This keeps the app safer and easier to debug.

---

## 17. Useful Official Documentation

- Google Calendar API Python Quickstart: https://developers.google.com/workspace/calendar/api/quickstart/python
- Google Calendar FreeBusy API: https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- Gemini API Keys: https://ai.google.dev/gemini-api/docs/api-key
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- FullCalendar React Docs: https://fullcalendar.io/docs/react
