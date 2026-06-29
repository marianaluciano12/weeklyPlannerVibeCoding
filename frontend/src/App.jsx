import { useRef, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const calendarRef = useRef(null);

  const [message, setMessage] = useState("");
  const [assistantReply, setAssistantReply] = useState("");
  const [loading, setLoading] = useState(false);

  async function fetchEvents(fetchInfo, successCallback, failureCallback) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/events?start=${encodeURIComponent(fetchInfo.startStr)}&end=${encodeURIComponent(fetchInfo.endStr)}`
      );

      const events = await response.json();

      successCallback(events);
    } catch (error) {
      console.error(error);
      failureCallback(error);
    }
  }

  async function sendMessageToAssistant() {
    if (!message.trim()) return;

    setLoading(true);
    setAssistantReply("");

    try {
      const response = await fetch(`${API_BASE_URL}/assistant`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message
        })
      });

      const data = await response.json();

      setAssistantReply(data.message || "Done.");

      setMessage("");

      if (calendarRef.current) {
        calendarRef.current.getApi().refetchEvents();
      }
    } catch (error) {
      console.error(error);
      setAssistantReply("Something went wrong.");
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

  return (
    <div className="app">
      <h1>AI Calendar Assistant</h1>

      <div className="calendar-card">
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay"
          }}
          height="70vh"
          events={fetchEvents}
          nowIndicator={true}
        />
      </div>

      <div className="assistant-card">
        <h2>Personal Assistant</h2>

        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Try: "Remind me to buy milk in 3 days" or "I want to dedicate 20 min per day each week to play the piano"'
        />

        <button onClick={sendMessageToAssistant} disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>

        {assistantReply && (
          <p className="assistant-reply">{assistantReply}</p>
        )}
      </div>
    </div>
  );
}

export default App;