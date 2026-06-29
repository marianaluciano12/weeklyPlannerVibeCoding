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

const [selectedEvent, setSelectedEvent] = useState(null);

const [showPreferences, setShowPreferences] = useState(false);

function getPlanningStyleLabel(value) {
  const labels = {
    balanced: "Balanced",
    earliest: "Earliest available",
    morning: "Prefer morning",
    afternoon: "Prefer afternoon",
    evening: "Prefer evening",
  };

  return labels[value] || "Balanced";
}

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
  const category = eventInfo.event.extendedProps.category || "personal";
  const originalTitle =
    eventInfo.event.extendedProps.originalTitle || eventInfo.event.title;

  return (
    <div
      className={`custom-event-content event-category-${category}`}
      title={originalTitle}
    >
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

function formatEventDate(dateValue) {
  if (!dateValue) return "No date";

  return new Intl.DateTimeFormat("en-GB", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(dateValue);
}

function openEventPopup(eventClickInfo) {
  eventClickInfo.jsEvent.preventDefault();

  setSelectedEvent({
    id: eventClickInfo.event.id,
    title:
      eventClickInfo.event.extendedProps.originalTitle ||
      eventClickInfo.event.title,
    displayTitle: eventClickInfo.event.title,
    start: eventClickInfo.event.start,
    end: eventClickInfo.event.end,
    category: eventClickInfo.event.extendedProps.category || "personal",
    emoji: eventClickInfo.event.extendedProps.emoji || "✨",
  });
}

function editSelectedEvent() {
  if (!selectedEvent) return;

  setAssistantReply(
    `Edit feature coming soon for: ${selectedEvent.title}`
  );
  setStatusType("success");
  closeEventPopup();
}

function closeEventPopup() {
  setSelectedEvent(null);
}

async function deleteSelectedEvent() {
  if (!selectedEvent) return;

  const shouldDelete = window.confirm(
    `Delete "${selectedEvent.title}" from your Google Calendar?`
  );

  if (!shouldDelete) return;

  try {
    const response = await fetch(
      `${API_BASE_URL}/events/${encodeURIComponent(selectedEvent.id)}`,
      {
        method: "DELETE",
      }
    );

    const data = await response.json();

    if (!response.ok || data.status === "error") {
      throw new Error(data.message || "Could not delete event.");
    }

    setAssistantReply(`Deleted: ${selectedEvent.title}`);
    setStatusType("success");

    closeEventPopup();

    if (calendarRef.current) {
      calendarRef.current.getApi().refetchEvents();
    }
  } catch (error) {
    console.error(error);
    setAssistantReply(
      error.message || "Something went wrong while deleting the event."
    );
    setStatusType("error");
  }
}


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
    right: "timeGridDay,timeGridWeek,dayGridMonth",
  }}
  buttonText={{
    today: "Today",
    day: "Day",
    week: "Week",
    month: "Month",
  }}
  height="82vh"
  events={fetchEvents}
  eventClick={openEventPopup}
  nowIndicator={true}
  allDaySlot={false}
  slotMinTime="07:00:00"
  slotMaxTime="23:00:00"
  expandRows={true}
  eventContent={renderEventContent}
  displayEventTime={false}
  slotEventOverlap={false}
  eventMinHeight={34}
  slotDuration="00:30:00"
  snapDuration="00:15:00"
/>
            </div>
          </section>
<section className={`preferences-card ${showPreferences ? "is-open" : ""}`}>
  <div className="preferences-compact">
    <div className="preferences-identity">
      <div className="preferences-badge">✦</div>

      <div className="preferences-copy">
        <p className="eyebrow">Planning preferences</p>
        <h2>How should the assistant schedule your time?</h2>
        <p className="preferences-description">
          Fine-tune how your assistant picks time slots so suggestions match
          your routine.
        </p>

        <div className="preferences-summary">
          <span className="summary-chip">
            <strong>Weekdays</strong>
            {preferences.weekday_start}–{preferences.weekday_end}
          </span>

          <span className="summary-chip">
            <strong>Weekends</strong>
            {preferences.weekend_start}–{preferences.weekend_end}
          </span>

          <span className="summary-chip">
            <strong>Style</strong>
            {getPlanningStyleLabel(preferences.preferred_time_of_day)}
          </span>

          <span className="summary-chip">
            <strong>Gap</strong>
            {preferences.minimum_gap_minutes} min
          </span>

          <span className="summary-chip">
            <strong>Reminder</strong>
            {preferences.default_reminder_minutes} min
          </span>
        </div>
      </div>
    </div>

    <button
      type="button"
      className="preferences-toggle-button"
      onClick={() => setShowPreferences((current) => !current)}
    >
      <span className="preferences-toggle-icon">
        {showPreferences ? "–" : "⚙"}
      </span>
      <span>{showPreferences ? "Hide settings" : "Customize"}</span>
    </button>
  </div>

  {showPreferences && (
    <div className="preferences-expanded">
      <div className="preferences-section-card">
        <div className="preferences-section-header">
          <div>
            <p className="preferences-section-label">Availability</p>
            <h3>When are you usually free?</h3>
          </div>
          <p>
            These time windows help the assistant find realistic slots for your
            hobbies and personal tasks.
          </p>
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
        </div>
      </div>

      <div className="preferences-section-card">
        <div className="preferences-section-header">
          <div>
            <p className="preferences-section-label">Scheduling behaviour</p>
            <h3>How should planning feel?</h3>
          </div>
          <p>
            Control gaps, reminders and the preferred time of day for AI-created
            plans.
          </p>
        </div>

        <div className="preferences-grid">
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
                updatePreference(
                  "default_reminder_minutes",
                  Number(event.target.value)
                )
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
      </div>
    </div>
  )}
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
      
      {selectedEvent && (
  <div className="event-modal-backdrop" onClick={closeEventPopup}>
    <div
      className="event-modal"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="event-modal-header">
        <div className="event-modal-icon">{selectedEvent.emoji}</div>

        <div>
          <p className="eyebrow">Calendar event</p>
          <h2>{selectedEvent.title}</h2>
        </div>

        <button
          type="button"
          className="event-modal-close"
          onClick={closeEventPopup}
          aria-label="Close event popup"
        >
          ×
        </button>
      </div>

      <div className="event-details-panel always-visible">
        <div className="event-detail-row">
          <span>Title</span>
          <strong>{selectedEvent.title}</strong>
        </div>

        <div className="event-detail-row">
          <span>Start</span>
          <strong>{formatEventDate(selectedEvent.start)}</strong>
        </div>

        <div className="event-detail-row">
          <span>End</span>
          <strong>{formatEventDate(selectedEvent.end)}</strong>
        </div>

        <div className="event-detail-row">
          <span>Category</span>
          <strong>
            {selectedEvent.emoji} {selectedEvent.category}
          </strong>
        </div>
      </div>

      <div className="event-modal-actions bottom-actions">
        <button
          type="button"
          className="event-action-button secondary"
          onClick={editSelectedEvent}
        >
          Edit event
        </button>

        <button
          type="button"
          className="event-action-button danger"
          onClick={deleteSelectedEvent}
        >
          Delete event
        </button>
      </div>
    </div>
  </div>
)}
    </div>
  );
}

export default App;
