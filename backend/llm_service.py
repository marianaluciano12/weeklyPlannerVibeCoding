import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Europe/Lisbon")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def clean_json(text: str) -> str:
    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


def parse_user_message(message: str, calendar_context=None) -> dict:
    now = datetime.now(ZoneInfo(TIMEZONE)).isoformat()
    calendar_context = calendar_context or []

    calendar_context_text = "\n".join(
        [
            f"- {event['title']}: {event['start']} to {event['end']}"
            for event in calendar_context
        ]
    )

    if not calendar_context_text:
        calendar_context_text = "No upcoming events found."

    prompt = f"""
És um assistente pessoal de calendário.

A tua tarefa é converter a mensagem do utilizador numa única ação JSON estruturada.

Data e hora atuais: {now}
Fuso horário: {TIMEZONE}

Eventos próximos no calendário:
{calendar_context_text}

Ações permitidas:

1. create_reminder
Usa quando o utilizador pede um lembrete único.
Exemplo:
"lembra-me de comprar leite daqui a 3 dias"

2. schedule_habit
Usa quando o utilizador quer agendar tempo recorrente para um hobby, hábito, exercício, estudo, etc.
Exemplo:
"quero dedicar 20 min por dia esta semana a tocar piano"

3. schedule_plan
Usa quando o utilizador pede para agendar várias coisas na mesma mensagem.
Exemplo:
"quero tocar piano todos os dias e ir ao ginásio 3 vezes esta semana"

4. unknown
Usa quando não consegues compreender o pedido.

Devolve APENAS JSON válido.

JSON schema:
{{
  "action": "create_reminder" | "schedule_habit" | "schedule_plan" | "unknown",
  "title": string | null,
  "start_datetime": string | null,
  "duration_minutes": integer | null,
  "frequency": "once" | "daily" | "weekly" | null,
  "days": integer | null,
  "category": "hobby" | "errand" | "exercise" | "work" | "chore" | "health" | "study" | "relationship" | "personal" | null,
  "tasks": [
    {{
      "title": string,
      "duration_minutes": integer,
      "sessions_count": integer,
      "frequency": "daily" | "weekly",
      "days": integer,
      "category": "hobby" | "errand" | "exercise" | "work" | "chore" | "health" | "study" | "relationship" | "personal",
      "preferred_time_of_day": "earliest" | "morning" | "afternoon" | "evening" | "balanced",
      "allowed_days": "any" | "weekdays" | "weekends",
      "preferred_window_start": string | null,
      "preferred_window_end": string | null,
      "notes": string | null
    }}
  ] | null,
  "notes": string | null
}}

Regras de idioma:
- As chaves JSON devem ficar em inglês porque o backend precisa delas.
- Os valores visíveis ao utilizador, especialmente "title" e "notes", devem estar em português de Portugal.
- Usa português natural de Portugal, não português do Brasil.
- Não traduzas os valores internos de "category". Devem continuar em inglês.

Regras:
- Devolve sempre datas em formato ISO 8601.
- Usa o fuso horário {TIMEZONE}.
- Para lembretes sem hora específica, usa 09:00.
- Para create_reminder, duration_minutes deve ser 30.
- Para "todos os dias da semana", usa frequency "daily", sessions_count 7 e days 7.
- Para "3 vezes por semana", usa sessions_count 3, frequency "weekly" e days 7.
- Para schedule_habit, start_datetime pode ser null porque o backend vai encontrar os melhores horários.
- O título deve ser curto e adequado para calendário.

Regras de contexto do calendário:
- Usa os eventos próximos para resolver frases como "depois da minha aula de piano", "antes do dentista", "depois da reunião" ou "antes do trabalho".
- Se o utilizador disser "depois de [evento]", agenda depois do fim desse evento.
- Se o utilizador disser "antes de [evento]", agenda antes do início desse evento.
- Se o utilizador não disser quanto tempo depois, usa 15 minutos depois do fim do evento.
- Se o utilizador disser "logo depois" ou "imediatamente depois", usa a hora exata de fim do evento.
- Se o utilizador mencionar parcialmente um evento, encontra o evento próximo mais parecido.
- Se não encontrares evento correspondente, usa 09:00.

Regras de planeamento com várias tarefas:
- Se o utilizador pedir mais do que uma coisa para agendar, usa action "schedule_plan".
- Para schedule_plan, coloca cada atividade dentro de tasks.
- Se faltar duração:
  - ginásio/exercício = 60 minutos
  - recados = 30 minutos
  - tarefas domésticas = 30 minutos
  - hobbies = 20 minutos
  - estudo = 45 minutos
- Se o utilizador disser "de manhã", usa preferred_time_of_day "morning".
- Se o utilizador disser "antes do trabalho", usa allowed_days "weekdays", preferred_window_start "06:30", preferred_window_end "09:00".
- Se não houver preferência específica, usa preferred_time_of_day "balanced", allowed_days "any", preferred_window_start null, preferred_window_end null.

Regras de categoria:
- piano, leitura, música, desenho, jogos = hobby
- compras, comprar algo, supermercado, farmácia = errand
- ginásio, correr, caminhada, treino, yoga = exercise
- reuniões, chamadas, trabalho, código, curso, aulas = work
- limpeza, roupa, loiça, tarefas da casa = chore
- médico, dentista, medicamentos, consultas = health
- estudar, aprender, trabalhos, exames = study
- encontro, date, planos românticos, tempo de casal = relationship
- se não tiveres a certeza, usa personal

Mensagem do utilizador:
{message}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    raw_text = response.text or "{}"
    json_text = clean_json(raw_text)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return {
             "action": "unknown",
    "title": None,
    "start_datetime": None,
    "duration_minutes": None,
    "frequency": None,
    "days": None,
    "category": None,
    "tasks": None,
    "notes": "Could not parse LLM response."
        }