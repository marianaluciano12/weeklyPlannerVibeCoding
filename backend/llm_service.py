import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Europe/Lisbon")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)

GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")


def clean_json(text: str) -> str:
    text = text.strip()

    # Some reasoning models return hidden reasoning as visible text:
    # <think> ... </think>
    # Remove it before trying to parse JSON.
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove markdown fences if the model adds them.
    text = re.sub(r"^```json", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text.strip())
    text = re.sub(r"```$", "", text.strip())

    text = text.strip()

    # If the model adds any extra text before/after the JSON,
    # extract only the outer JSON object.
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

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

IMPORTANTE:
- Devolve APENAS JSON válido.
- Não uses markdown.
- Não uses blocos ```json.
- Não uses <think>.
- Não escrevas raciocínio.
- Não expliques nada.
- Não incluas texto antes nem depois do JSON.

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
      "start_datetime": string | null,
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
- Para create_reminder, duration_minutes deve ser 30.
- Para create_reminder, frequency deve ser "once".
- Para "todos os dias da semana", usa frequency "daily", sessions_count 7 e days 7.
- Para "3 vezes por semana", usa sessions_count 3, frequency "weekly" e days 7.
- Para schedule_habit, start_datetime pode ser null porque o backend vai encontrar os melhores horários.
- O título deve ser curto e adequado para calendário.

Regras para datas e horas:
- Se o utilizador não der nenhuma data nem hora específica, usa start_datetime null. O backend vai encontrar o próximo horário livre fora do horário de trabalho.
- Se o utilizador der uma data ou dia da semana, como "amanhã", "sexta", "na segunda", "dia 15", deves preencher start_datetime com essa data.
- Se o utilizador der uma data/dia mas não der hora, escolhe uma hora provável:
  - cinema, jantar, date, amigos, eventos sociais = 20:00
  - ginásio/treino = 18:00, excepto se disser "de manhã"
  - compras/recados = 18:00
  - consultas/saúde = 09:00
  - trabalho/reuniões = 09:00
  - outros eventos pessoais = 18:00
- "sexta" significa a próxima sexta-feira futura.
- "na sexta" significa a próxima sexta-feira futura.
- "este fim de semana" significa sábado ou domingo próximos.

Regras de contexto do calendário:
- Usa os eventos próximos para resolver frases como "depois da minha aula de piano", "antes do dentista", "depois da reunião" ou "antes do trabalho".
- Se o utilizador disser "depois de [evento]", agenda depois do fim desse evento.
- Se o utilizador disser "antes de [evento]", agenda antes do início desse evento.
- Se o utilizador não disser quanto tempo depois, usa 15 minutos depois do fim do evento.
- Se o utilizador disser "logo depois" ou "imediatamente depois", usa a hora exata de fim do evento.
- Se o utilizador mencionar parcialmente um evento, encontra o evento próximo mais parecido.
- Se o utilizador referir outro evento e não encontrares evento correspondente, mas tiver dado uma data/dia, usa essa data com uma hora provável.
- Se não houver data, hora nem evento correspondente, usa start_datetime null.

Regras de planeamento com várias tarefas:
- Se o utilizador pedir mais do que uma coisa para agendar, usa action "schedule_plan".
- Para schedule_plan, coloca cada atividade dentro de tasks.
- Dentro de schedule_plan, se uma task for um evento único com data/dia específico, usa frequency "once" e preenche start_datetime nessa task.
- Para tasks com frequency "once", não uses preferred_window_start para datas completas. Usa start_datetime.
- preferred_window_start e preferred_window_end são apenas para janelas horárias recorrentes como "06:30" e "09:00".
- Se o utilizador disser "cinema na sexta", a task deve ter frequency "once" e start_datetime na próxima sexta às 20:00.
- Se o utilizador disser "date no domingo à tarde", a task deve ter frequency "once" e start_datetime no próximo domingo às 15:00 ou 16:00.
- Se o utilizador disser "comprar ovos hoje depois do evento de piano", a task deve ter frequency "once" e start_datetime depois do fim desse evento.
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
- cinema, amigos, eventos sociais = personal
- se não tiveres a certeza, usa personal

Exemplos importantes:

Mensagem: "tenho cinema com amigos na sexta"
Resposta esperada:
{{
  "action": "create_reminder",
  "title": "Cinema com amigos",
  "start_datetime": "YYYY-MM-DDT20:00:00+01:00",
  "duration_minutes": 120,
  "frequency": "once",
  "days": null,
  "category": "personal",
  "tasks": null,
  "notes": null
}}

Mensagem: "tenho de comprar ovos"
Resposta esperada:
{{
  "action": "create_reminder",
  "title": "Comprar ovos",
  "start_datetime": null,
  "duration_minutes": 30,
  "frequency": "once",
  "days": null,
  "category": "errand",
  "tasks": null,
  "notes": null
}}

Mensagem: "tenho de comprar ovos na sexta"
Resposta esperada:
{{
  "action": "create_reminder",
  "title": "Comprar ovos",
  "start_datetime": "YYYY-MM-DDT18:00:00+01:00",
  "duration_minutes": 30,
  "frequency": "once",
  "days": null,
  "category": "errand",
  "tasks": null,
  "notes": null
}}

Mensagem: "quero praticar piano todos os dias e tenho cinema com amigos na sexta"
Resposta esperada:
{{
  "action": "schedule_plan",
  "title": null,
  "start_datetime": null,
  "duration_minutes": null,
  "frequency": null,
  "days": null,
  "category": null,
  "tasks": [
    {{
      "title": "Praticar piano",
      "start_datetime": null,
      "duration_minutes": 20,
      "sessions_count": 7,
      "frequency": "daily",
      "days": 7,
      "category": "hobby",
      "preferred_time_of_day": "balanced",
      "allowed_days": "any",
      "preferred_window_start": null,
      "preferred_window_end": null,
      "notes": null
    }},
    {{
      "title": "Cinema com amigos",
      "start_datetime": "YYYY-MM-DDT20:00:00+01:00",
      "duration_minutes": 120,
      "sessions_count": 1,
      "frequency": "once",
      "days": 1,
      "category": "personal",
      "preferred_time_of_day": "evening",
      "allowed_days": "any",
      "preferred_window_start": null,
      "preferred_window_end": null,
      "notes": null
    }}
  ],
  "notes": null
}}

Mensagem: "tenho um date com o meu namorado no domingo à tarde"
Resposta esperada:
{{
  "action": "create_reminder",
  "title": "Date com o namorado",
  "start_datetime": "YYYY-MM-DDT15:00:00+01:00",
  "duration_minutes": 120,
  "frequency": "once",
  "days": null,
  "category": "relationship",
  "tasks": null,
  "notes": null
}}

Mensagem do utilizador:
{message}
"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Devolve apenas JSON válido. "
                        "Não uses markdown. "
                        "Não uses <think>. "
                        "Não escrevas raciocínio. "
                        "Não expliques nada."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
        )
    except Exception as error:
        error_text = str(error)

        if "429" in error_text or "rate_limit" in error_text.lower() or "quota" in error_text.lower():
            return {
                "action": "unknown",
                "title": None,
                "start_datetime": None,
                "duration_minutes": None,
                "frequency": None,
                "days": None,
                "category": None,
                "tasks": None,
                "error_type": "quota_exceeded",
                "notes": (
                    "Atingiste o limite gratuito do modelo de IA. "
                    "Espera um pouco e tenta novamente."
                ),
            }

        return {
            "action": "unknown",
            "title": None,
            "start_datetime": None,
            "duration_minutes": None,
            "frequency": None,
            "days": None,
            "category": None,
            "tasks": None,
            "error_type": "llm_error",
            "notes": f"Erro ao comunicar com o modelo de IA: {error}",
        }

    raw_text = response.choices[0].message.content or "{}"
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
            "error_type": "json_parse_error",
            "notes": f"Não consegui interpretar a resposta do modelo de IA: {raw_text}",
        }
