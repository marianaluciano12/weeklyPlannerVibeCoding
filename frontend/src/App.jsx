import { useCallback, useRef, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import ptLocale from "@fullcalendar/core/locales/pt";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

const SUGESTOES = [
  "Lembra-me de comprar leite daqui a 3 dias",
  "Quero tocar piano 20 minutos todos os dias esta semana",
  "Quero ir ao ginásio 3 vezes por semana, de manhã antes do trabalho",
];

function App() {
  const calendarRef = useRef(null);

  const [message, setMessage] = useState("");
  const [assistantReply, setAssistantReply] = useState("");
  const [statusType, setStatusType] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [createdPlanEvents, setCreatedPlanEvents] = useState([]);

  const [preferences, setPreferences] = useState({
    day_start: "07:00",
    work_start: "09:00",
    work_end: "17:00",
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

  function getPlanningStyleLabel(value) {
    const labels = {
      balanced: "Equilibrado",
      earliest: "Primeiro horário livre",
      morning: "Preferir manhã",
      afternoon: "Preferir tarde",
      evening: "Preferir noite",
    };

    return labels[value] || "Equilibrado";
  }

  function getCategoryLabel(category) {
    const labels = {
      hobby: "Hobby",
      errand: "Recado",
      exercise: "Exercício",
      work: "Trabalho",
      chore: "Tarefa doméstica",
      health: "Saúde",
      study: "Estudo",
      relationship: "Relação",
      personal: "Pessoal",
    };

    return labels[category] || "Pessoal";
  }

  function formatEventDate(dateValue) {
    if (!dateValue) return "Sem data";

    return new Intl.DateTimeFormat("pt-PT", {
      weekday: "short",
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(dateValue);
  }

  function formatPlanEventDate(dateValue) {
    if (!dateValue) return "Sem data";

    return new Intl.DateTimeFormat("pt-PT", {
      weekday: "short",
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(dateValue));
  }

  function groupCreatedEvents(events) {
    return events.reduce((groups, event) => {
      const key = event.title || "Evento agendado";

      if (!groups[key]) {
        groups[key] = {
          title: event.title || "Evento agendado",
          category: event.category || "personal",
          emoji: event.emoji || "✨",
          events: [],
        };
      }

      groups[key].events.push(event);

      return groups;
    }, {});
  }

  const fetchEvents = useCallback(
    async (fetchInfo, successCallback, failureCallback) => {
      try {
        const url = `${API_BASE_URL}/events?start=${encodeURIComponent(
          fetchInfo.startStr
        )}&end=${encodeURIComponent(fetchInfo.endStr)}`;

        const response = await fetch(url);

        if (!response.ok) {
          const errorText = await response.text();
          console.error("Erro no endpoint de eventos:", errorText);
          throw new Error("Não foi possível carregar os eventos do calendário.");
        }

        const events = await response.json();
        successCallback(events);
      } catch (error) {
        console.error("Erro ao carregar eventos:", error);
        failureCallback(error);
      }
    },
    []
  );

  const renderEventContent = useCallback((eventInfo) => {
    const title =
      eventInfo.event.extendedProps?.originalTitle ||
      eventInfo.event.title ||
      "Evento sem título";

    const category = eventInfo.event.extendedProps?.category || "personal";

    return (
      <div
        className={`custom-event-content event-category-${category}`}
        title={title}
      >
        <span className="custom-event-title">{eventInfo.event.title}</span>
      </div>
    );
  }, []);

  async function sendMessageToAssistant(customMessage) {
    const textToSend = customMessage || message;

    if (!textToSend.trim()) return;

    setLoading(true);
    setAssistantReply("");
    setStatusType("");
    setCreatedPlanEvents([]);

    try {
      const response = await fetch(`${API_BASE_URL}/assistant`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: textToSend,
          preferences,
        }),
      });

      const data = await response.json();

      if (!response.ok || data.status === "error") {
        throw new Error(data.message || "O assistente não conseguiu concluir o pedido.");
      }

      setAssistantReply(data.message || "Feito.");
      setStatusType("success");
      setCreatedPlanEvents(data.created_events || []);
      setMessage("");

      if (calendarRef.current) {
        calendarRef.current.getApi().refetchEvents();
      }
    } catch (error) {
      console.error(error);
      setCreatedPlanEvents([]);
      setAssistantReply(error.message || "Ocorreu um erro.");
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

  function openEventPopup(eventClickInfo) {
    eventClickInfo.jsEvent.preventDefault();

    setSelectedEvent({
      id: eventClickInfo.event.id,
      title:
        eventClickInfo.event.extendedProps?.originalTitle ||
        eventClickInfo.event.title ||
        "Evento sem título",
      displayTitle: eventClickInfo.event.title,
      start: eventClickInfo.event.start,
      end: eventClickInfo.event.end,
      category: eventClickInfo.event.extendedProps?.category || "personal",
      emoji: eventClickInfo.event.extendedProps?.emoji || "✨",
    });
  }

  function closeEventPopup() {
    setSelectedEvent(null);
  }

  function editSelectedEvent() {
    if (!selectedEvent) return;

    setAssistantReply(`Funcionalidade de edição em breve para: ${selectedEvent.title}`);
    setStatusType("success");
    closeEventPopup();
  }

  async function deleteSelectedEvent() {
    if (!selectedEvent) return;

    const shouldDelete = window.confirm(
      `Queres eliminar "${selectedEvent.title}" do teu Google Calendar?`
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
        throw new Error(data.message || "Não foi possível eliminar o evento.");
      }

      setAssistantReply(`Evento eliminado: ${selectedEvent.title}`);
      setStatusType("success");
      setCreatedPlanEvents([]);

      closeEventPopup();

      if (calendarRef.current) {
        calendarRef.current.getApi().refetchEvents();
      }
    } catch (error) {
      console.error(error);
      setAssistantReply(error.message || "Ocorreu um erro ao eliminar o evento.");
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
              <h1>Planeador de Calendário</h1>
              <p>O teu assistente de IA para lembretes, rotinas.</p>
            </div>
          </div>

        </header>

        <main className="dashboard">

          <section className="calendar-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Google Calendar</p>
                <h2>A tua agenda</h2>
              </div>

              <div className="calendar-hint">
                <span className="hint-dot" />
                Eventos em tempo real
              </div>
            </div>

            <div className="calendar-wrapper">
              <FullCalendar
                ref={calendarRef}
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                locale={ptLocale}
                firstDay={1}
                initialView="timeGridWeek"
                headerToolbar={{
                  left: "prev,next today",
                  center: "title",
                  right: "timeGridDay,timeGridWeek,dayGridMonth",
                }}
                buttonText={{
                  today: "Hoje",
                  day: "Dia",
                  week: "Semana",
                  month: "Mês",
                }}
                allDayText="Dia todo"
                height="82vh"
                events={fetchEvents}
                eventClick={openEventPopup}
                eventContent={renderEventContent}
                nowIndicator={true}
                allDaySlot={false}
                slotMinTime="07:00:00"
                slotMaxTime="23:00:00"
                expandRows={true}
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
                

                <div className="preferences-copy">
                  <p className="eyebrow">Preferências de planeamento</p>
                  <h2>Como devo organizar o teu tempo?</h2>
                  <p className="preferences-description">
                    Ajusta a forma como o assistente escolhe horários para que as sugestões
                    se adaptem à tua rotina.
                  </p>

                  <div className="preferences-summary">
                    <span className="summary-chip">
                      <strong>Trabalho</strong>
                      {preferences.work_start}–{preferences.work_end}
                    </span>

                    <span className="summary-chip">
                      <strong>Tempo livre</strong>
                      antes/depois do trabalho
                    </span>

                    <span className="summary-chip">
                      <strong>Fim de semana</strong>
                      {preferences.weekend_start}–{preferences.weekend_end}
                    </span>

                    <span className="summary-chip">
                      <strong>Estilo</strong>
                      {getPlanningStyleLabel(preferences.preferred_time_of_day)}
                    </span>

                    <span className="summary-chip">
                      <strong>Intervalo</strong>
                      {preferences.minimum_gap_minutes} min
                    </span>

                    <span className="summary-chip">
                      <strong>Lembrete</strong>
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
                <span>{showPreferences ? "Ocultar definições" : "Personalizar"}</span>
              </button>
            </div>

            {showPreferences && (
              <div className="preferences-expanded">
                <div className="preferences-section-card">
                  <div className="preferences-section-header">
                    <div>
                      <p className="preferences-section-label">Horário de trabalho</p>
                      <h3>Qual é o teu horário de trabalho?</h3>
                    </div>

                    <p>
                      Nos dias úteis, o assistente considera como tempo livre tudo
                      o que fica antes e depois do teu horário de trabalho.
                    </p>
                  </div>

                  <div className="preferences-grid">
                    <label className="preference-field">
                      <span>Primeiro horário do dia</span>
                      <input
                        type="time"
                        value={preferences.day_start}
                        onChange={(event) =>
                          updatePreference("day_start", event.target.value)
                        }
                      />
                    </label>

                    <label className="preference-field">
                      <span>Início do trabalho</span>
                      <input
                        type="time"
                        value={preferences.work_start}
                        onChange={(event) =>
                          updatePreference("work_start", event.target.value)
                        }
                      />
                    </label>

                    <label className="preference-field">
                      <span>Fim do trabalho</span>
                      <input
                        type="time"
                        value={preferences.work_end}
                        onChange={(event) =>
                          updatePreference("work_end", event.target.value)
                        }
                      />
                    </label>

                    <label className="preference-field">
                      <span>Início fim de semana</span>
                      <input
                        type="time"
                        value={preferences.weekend_start}
                        onChange={(event) =>
                          updatePreference("weekend_start", event.target.value)
                        }
                      />
                    </label>

                    <label className="preference-field">
                      <span>Fim fim de semana</span>
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
                      <p className="preferences-section-label">Comportamento</p>
                      <h3>Como deve ser feito o planeamento?</h3>
                    </div>

                    <p>
                      Controla intervalos, lembretes e a altura do dia preferida
                      para planos criados por IA.
                    </p>
                  </div>

                  <div className="preferences-grid">
                    <label className="preference-field">
                      <span>Intervalo mínimo</span>
                      <select
                        value={preferences.minimum_gap_minutes}
                        onChange={(event) =>
                          updatePreference("minimum_gap_minutes", Number(event.target.value))
                        }
                      >
                        <option value={0}>Sem intervalo</option>
                        <option value={10}>10 minutos</option>
                        <option value={15}>15 minutos</option>
                        <option value={30}>30 minutos</option>
                      </select>
                    </label>

                    <label className="preference-field">
                      <span>Lembrete padrão</span>
                      <select
                        value={preferences.default_reminder_minutes}
                        onChange={(event) =>
                          updatePreference(
                            "default_reminder_minutes",
                            Number(event.target.value)
                          )
                        }
                      >
                        <option value={0}>Na hora do evento</option>
                        <option value={5}>5 minutos antes</option>
                        <option value={10}>10 minutos antes</option>
                        <option value={30}>30 minutos antes</option>
                        <option value={60}>1 hora antes</option>
                      </select>
                    </label>

                    <label className="preference-field">
                      <span>Estilo de planeamento</span>
                      <select
                        value={preferences.preferred_time_of_day}
                        onChange={(event) =>
                          updatePreference("preferred_time_of_day", event.target.value)
                        }
                      >
                        <option value="balanced">Equilibrado</option>
                        <option value="earliest">Primeiro horário livre</option>
                        <option value="morning">Preferir manhã</option>
                        <option value="afternoon">Preferir tarde</option>
                        <option value="evening">Preferir noite</option>
                      </select>
                    </label>

                    <label className="preference-field">
                      <span>Evitar depois das</span>
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
            

            <div className="assistant-content">
              <div className="assistant-title-row">
                <div>
                  <p className="eyebrow">Assistente pessoal</p>
                  <h2>O que queres planear?</h2>
                </div>

                {loading && <span className="thinking-pill">A pensar…</span>}
              </div>

              <div className={`command-bar ${loading ? "is-loading" : ""}`}>
                <textarea
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder='Experimenta: "lembra-me de comprar leite daqui a 3 dias"'
                  disabled={loading}
                />

                <button
                  type="button"
                  className="send-button"
                  onClick={() => sendMessageToAssistant()}
                  disabled={loading || !message.trim()}
                  aria-label="Enviar mensagem para o assistente"
                >
                  {loading ? "…" : "➜"}
                </button>
              </div>

              <div className="suggestion-row">
                {SUGESTOES.map((suggestion) => (
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
                  <strong>
                    {statusType === "error" ? "Não foi possível concluir" : "Feito"}
                  </strong>
                  <p>{assistantReply}</p>
                </div>
              )}

              {createdPlanEvents.length > 0 && (
                <div className="plan-summary-card">
                  <div className="plan-summary-header">
                    <div>
                      <p className="eyebrow">Plano criado</p>
                      <h3>{createdPlanEvents.length} evento(s) adicionados ao calendário</h3>
                    </div>
                  </div>

                  <div className="plan-summary-groups">
                    {Object.values(groupCreatedEvents(createdPlanEvents)).map((group) => (
                      <div className="plan-summary-group" key={group.title}>
                        <div className="plan-summary-group-header">
                          <div className="plan-summary-icon">{group.emoji}</div>

                          <div>
                            <h4>{group.title}</h4>
                            <p>
                              {getCategoryLabel(group.category)} · {group.events.length} sessão
                              {group.events.length === 1 ? "" : "ões"}
                            </p>
                          </div>
                        </div>

                        <div className="plan-summary-list">
                          {group.events.map((event) => (
                            <div className="plan-summary-item" key={event.id}>
                              <span>{formatPlanEventDate(event.start)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
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
                <p className="eyebrow">Evento do calendário</p>
                <h2>{selectedEvent.title}</h2>
              </div>

              <button
                type="button"
                className="event-modal-close"
                onClick={closeEventPopup}
                aria-label="Fechar popup do evento"
              >
                ×
              </button>
            </div>

            <div className="event-details-panel always-visible">
              <div className="event-detail-row">
                <span>Título</span>
                <strong>{selectedEvent.title}</strong>
              </div>

              <div className="event-detail-row">
                <span>Início</span>
                <strong>{formatEventDate(selectedEvent.start)}</strong>
              </div>

              <div className="event-detail-row">
                <span>Fim</span>
                <strong>{formatEventDate(selectedEvent.end)}</strong>
              </div>

              <div className="event-detail-row">
                <span>Categoria</span>
                <strong>
                  {selectedEvent.emoji} {getCategoryLabel(selectedEvent.category)}
                </strong>
              </div>
            </div>

            <div className="event-modal-actions bottom-actions">
              <button
                type="button"
                className="event-action-button secondary"
                onClick={editSelectedEvent}
              >
                Editar evento
              </button>

              <button
                type="button"
                className="event-action-button danger"
                onClick={deleteSelectedEvent}
              >
                Eliminar evento
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
