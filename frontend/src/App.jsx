import { useCallback, useRef, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

const SUGGESTIONS = [
  "Remind me to buy milk in 3 days",
  "Schedule 20 minutes of piano every day this week",
  "Schedule 30 minutes of reading every day this week",
];

function App() {
  const [preferences, setPreferences] = useState({
  weekday_start: "17:00",
  weekday_end: "22:30",
  weekend_start: "10:00",
  weekend_end: "22:00",
  minimum_gap_minutes: 15,
  default_reminder_minutes: 10,
  preferred_time_of_day: "balanced",
  avoid_after: "21:30",
});

function updatePreference(key, value) {
  setPreferences((currentPreferences) => ({
    ...currentPreferences,
    [key]: value,
  }));
}
  const calendarRef = useRef(null);

  const [message, setMessage] = useState("");
  const [assistantReply, setAssistantReply] = useState("");
  const [statusType, setStatusType] = useState("");
  const [loading, setLoading] = useState(false);

const fetchEvents = useCallback(async (fetchInfo, successCallback, failureCallback) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/events?start=${encodeURIComponent(
        fetchInfo.startStr
      )}&end=${encodeURIComponent(fetchInfo.endStr)}`
    );

    if (!response.ok) {
      throw new Error("Could not load calendar events.");
    }

    const events = await response.json();
    successCallback(events);
  } catch (error) {
    console.error(error);
    failureCallback(error);
  }
}, []);

  async function sendMessageToAssistant(customMessage) {
    const textToSend = customMessage || message;

    if (!textToSend.trim()) return;

    setLoading(true);
    setAssistantReply("");
    setStatusType("");

    try {
      const response = await fetch(`${API_BASE_URL}/assistant`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: textToSend,
          preferences
        }),
      });

      const data = await response.json();

      if (!response.ok || data.status === "error") {
        throw new Error(data.message || "The assistant could not complete the request.");
      }

      setAssistantReply(data.message || "Done.");
      setStatusType("success");
      setMessage("");

      if (calendarRef.current) {
        calendarRef.current.getApi().refetchEvents();
      }
    } catch (error) {
      console.error(error);
      setAssistantReply(error.message || "Something went wrong.");
      setStatusType("error");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessageToAssistant();
    }
  }

const renderEventContent = useCallback((eventInfo) => {
  return (
    <div className="custom-event-content" title={eventInfo.event.title}>
      <span className="custom-event-title">{eventInfo.event.title}</span>
    </div>
  );
}, []);


const deleteCalendarEvent = useCallback(async (eventClickInfo) => {
  const eventTitle = eventClickInfo.event.title;
  const eventId = eventClickInfo.event.id;

  const shouldDelete = window.confirm(
    `Delete "${eventTitle}" from your Google Calendar?`
  );

  if (!shouldDelete) return;

  try {
    const response = await fetch(
      `${API_BASE_URL}/events/${encodeURIComponent(eventId)}`,
      {
        method: "DELETE",
      }
    );

    const data = await response.json();

    if (!response.ok || data.status === "error") {
      throw new Error(data.message || "Could not delete event.");
    }

    eventClickInfo.event.remove();

    setAssistantReply(`Deleted: ${eventTitle}`);
    setStatusType("success");

    if (calendarRef.current) {
      calendarRef.current.getApi().refetchEvents();
    }
  } catch (error) {
    console.error(error);
    setAssistantReply(error.message || "Something went wrong while deleting the event.");
    setStatusType("error");
  }
}, []);




  return (
    <div className="app-shell">
      <div className="background-glow background-glow-primary" />
      <div className="background-glow background-glow-secondary" />

      <div className="app-container">
        <header className="app-header">
          <div className="brand">
            <div className="brand-mark">✦</div>
            
            <div>
              <h1>Calendar Planner</h1>
              <p>Your AI assistant for reminders, routines and focus time.</p>
            </div>
          </div>

          <div className="header-summary">
            <span className="summary-label">Today</span>
            <strong>Plan smarter, remember more.</strong>
          </div>
        </header>

        <main className="dashboard">
          <section className="calendar-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Google Calendar</p>
                <h2>Your schedule</h2>
              </div>

              <div className="calendar-hint">
                <span className="hint-dot" />
                Live calendar events
              </div>
            </div>

            <div className="calendar-wrapper">
              <FullCalendar
  ref={calendarRef}
  plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
  initialView="timeGridWeek"
  headerToolbar={{
    left: "prev,next today",
    center: "title",
    right: "dayGridMonth,timeGridWeek,timeGridDay",
  }}
  eventContent={renderEventContent}
displayEventTime={false}
slotEventOverlap={false}
eventMinHeight={28}
slotDuration="00:30:00"
snapDuration="00:15:00"
eventClick={deleteCalendarEvent}  
height="82vh"
  events={fetchEvents}
  nowIndicator={true}
  allDaySlot={false}
  slotMinTime="07:00:00"
  slotMaxTime="23:00:00"
  expandRows={true}
  eventMinHeight={34}
  eventShortHeight={34}
  slotEventOverlap={false}
  displayEventEnd={true}
  eventDisplay="block"
  eventTimeFormat={{
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }}
/>
            </div>
          </section>
<section className="preferences-card">
  <div className="preferences-header">
    <div>
      <p className="eyebrow">Planning preferences</p>
      <h2>How should the assistant schedule your time?</h2>
    </div>
  </div>

  <div className="preferences-grid">
    <label className="preference-field">
      <span>Weekday start</span>
      <input
        type="time"
        value={preferences.weekday_start}
        onChange={(event) =>
          updatePreference("weekday_start", event.target.value)
        }
      />
    </label>

    <label className="preference-field">
      <span>Weekday end</span>
      <input
        type="time"
        value={preferences.weekday_end}
        onChange={(event) =>
          updatePreference("weekday_end", event.target.value)
        }
      />
    </label>

    <label className="preference-field">
      <span>Weekend start</span>
      <input
        type="time"
        value={preferences.weekend_start}
        onChange={(event) =>
          updatePreference("weekend_start", event.target.value)
        }
      />
    </label>

    <label className="preference-field">
      <span>Weekend end</span>
      <input
        type="time"
        value={preferences.weekend_end}
        onChange={(event) =>
          updatePreference("weekend_end", event.target.value)
        }
      />
    </label>

    <label className="preference-field">
      <span>Minimum gap</span>
      <select
        value={preferences.minimum_gap_minutes}
        onChange={(event) =>
          updatePreference("minimum_gap_minutes", Number(event.target.value))
        }
      >
        <option value={0}>No gap</option>
        <option value={10}>10 minutes</option>
        <option value={15}>15 minutes</option>
        <option value={30}>30 minutes</option>
      </select>
    </label>

    <label className="preference-field">
      <span>Default reminder</span>
      <select
        value={preferences.default_reminder_minutes}
        onChange={(event) =>
          updatePreference("default_reminder_minutes", Number(event.target.value))
        }
      >
        <option value={0}>At event time</option>
        <option value={5}>5 minutes before</option>
        <option value={10}>10 minutes before</option>
        <option value={30}>30 minutes before</option>
        <option value={60}>1 hour before</option>
      </select>
    </label>

    <label className="preference-field">
      <span>Planning style</span>
      <select
        value={preferences.preferred_time_of_day}
        onChange={(event) =>
          updatePreference("preferred_time_of_day", event.target.value)
        }
      >
        <option value="balanced">Balanced</option>
        <option value="earliest">Earliest available</option>
        <option value="morning">Prefer morning</option>
        <option value="afternoon">Prefer afternoon</option>
        <option value="evening">Prefer evening</option>
      </select>
    </label>

    <label className="preference-field">
      <span>Avoid after</span>
      <input
        type="time"
        value={preferences.avoid_after}
        onChange={(event) =>
          updatePreference("avoid_after", event.target.value)
        }
      />
    </label>
  </div>
</section>
          <section className="assistant-card">
            <div className="assistant-icon">✨</div>

            <div className="assistant-content">
              <div className="assistant-title-row">
                <div>
                  <p className="eyebrow">Personal assistant</p>
                  <h2>What do you want to plan?</h2>
                </div>

                {loading && <span className="thinking-pill">Thinking…</span>}
              </div>

              <div className={`command-bar ${loading ? "is-loading" : ""}`}>
                <textarea
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder='Try: "remind me to buy milk in 3 days"'
                  disabled={loading}
                />

                <button
                  type="button"
                  className="send-button"
                  onClick={() => sendMessageToAssistant()}
                  disabled={loading || !message.trim()}
                  aria-label="Send message to assistant"
                >
                  {loading ? "…" : "➜"}
                </button>
              </div>

              <div className="suggestion-row">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    className="suggestion-chip"
                    onClick={() => {
                      setMessage(suggestion);
                      sendMessageToAssistant(suggestion);
                    }}
                    disabled={loading}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              {assistantReply && (
                <div className={`assistant-reply ${statusType}`}>
                  <strong>{statusType === "error" ? "Could not complete request" : "Done"}</strong>
                  <p>{assistantReply}</p>
                </div>
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
