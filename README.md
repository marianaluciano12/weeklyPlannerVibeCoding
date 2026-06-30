# AI Calendar Assistant

Um assistente pessoal de calendário simples que lê o teu Google Calendar, entende linguagem natural e cria eventos/lembretes por ti.

A aplicação usa:

- **Backend:** FastAPI + Google Calendar API + Groq LLM
- **Frontend:** React + Vite + FullCalendar
- **Calendário:** Google Calendar OAuth

---

## Funcionalidades

- Ver eventos do Google Calendar numa vista semanal.
- Adicionar lembretes através de linguagem natural.
- Agendar hábitos recorrentes como piano, ginásio, estudo ou tarefas domésticas.
- Agendar várias tarefas a partir de uma só mensagem.
- Evitar horários já ocupados no calendário.
- Usar as tuas preferências de horário de trabalho para evitar marcar eventos durante o trabalho.
- Criar lembretes antes dos eventos.
- Suportar prompts em português e títulos de eventos em português.
- Abrir detalhes de eventos ao clicar no calendário.
- Eliminar eventos do calendário através da aplicação.
- Entender datas e contexto, como:
  - hoje
  - amanhã
  - sexta
  - domingo à tarde
  - esta semana
  - depois do meu evento de piano

---

## Requisitos

Instala primeiro:

- Python 3.10+
- Node.js 18+
- npm
- Projeto no Google Cloud com a Google Calendar API ativa
- Chave API da Groq

---

## Variáveis de ambiente

Cria um ficheiro `.env` dentro da pasta `backend`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3-32b

TIMEZONE=Europe/Lisbon
GOOGLE_CALENDAR_ID=primary
```

Também precisas de ter as credenciais OAuth do Google Calendar configuradas no backend, de acordo com o teu ficheiro `calendar_service.py`.

---

## Configurar autenticação do Google Calendar

Para a aplicação conseguir aceder ao teu Google Calendar, precisas de adicionar o ficheiro de credenciais OAuth do Google ao projeto.

### 1. Criar credenciais no Google Cloud

No Google Cloud Console:

1. Abre o teu projeto.
2. Ativa a **Google Calendar API**.
3. Vai a **APIs & Services** → **Credentials**.
4. Cria credenciais do tipo **OAuth client ID**.
5. Escolhe **"Desktop app"**.
6. Faz download do ficheiro JSON das credenciais.

### 2. Renomear o ficheiro

Depois de fazeres download, renomeia o ficheiro para:

```txt
credentials.json
```

### 3. Colocar o ficheiro no backend

Coloca o ficheiro dentro da pasta `backend`:

```txt
backend/
  credentials.json
  main.py
  llm_service.py
  calendar_service.py
  scheduler.py
  models.py
  requirements.txt
  .env
```

O caminho esperado deve ser:

```txt
backend/credentials.json
```

### 4. Primeira autenticação

Na primeira vez que correres a aplicação, o backend pode abrir uma janela do browser para iniciares sessão com a tua conta Google e autorizares o acesso ao calendário.

Depois da autenticação, o projeto pode criar um ficheiro de sessão/token, dependendo da implementação do teu `calendar_service.py`.

Não partilhes estes ficheiros:

```txt
credentials.json
token.json
.env
```

### 5. Importante

O ficheiro `credentials.json` deve ficar apenas no teu computador. Não o publiques no GitHub.

Adiciona estes ficheiros ao `.gitignore`:

```txt
backend/credentials.json
backend/token.json
backend/.env
```

---

## Instalar dependências do backend

A partir da raiz do projeto:

```bash
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

Se o backend mostrar o erro `No module named openai`, executa:

```bash
cd backend
.\venv\Scripts\python.exe -m pip install openai
cd ..
```

---

## Instalar dependências do frontend

A partir da raiz do projeto:

```bash
cd frontend
npm install
cd ..
```

---

## Executar a aplicação

A partir da raiz do projeto:

```bash
npm run dev
```

Isto inicia:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

Abre o frontend no browser:

```txt
http://localhost:5173
```

---

## Exemplos de prompts

### Lembretes simples

```txt
Tenho de comprar ovos
```

```txt
Lembra-me de comprar leite amanhã
```

```txt
Tenho dentista amanhã às 10:00
```

```txt
Tenho cinema com amigos na sexta das 21:00 às 23:00
```

```txt
Tenho um date com o meu namorado no domingo à tarde
```

---

### Hábitos e planos recorrentes

```txt
Quero praticar piano 20 min por dia nesta semana
```

```txt
Quero ir ao ginásio 3 vezes esta semana, prefiro de manhã
```

```txt
Quero estudar 45 minutos todos os dias esta semana
```

```txt
Quero fazer uma caminhada de 30 minutos no fim de semana
```

---

### Exemplos com contexto

```txt
Preciso de comprar ovos hoje depois do meu evento de piano
```

```txt
Lembra-me de ir à farmácia depois da reunião
```

```txt
Quero praticar piano antes do trabalho amanhã
```

---

### Exemplo complexo

```txt
Quero ir ao ginasio 3 vezes esta semana (prefiro de manhã), quero praticar piano 20 min todos os dias e preciso de comprar ovos hoje depois do meu evento de piano. Tenho cinema com amigos na sexta das 21:00 as 23:00 e um date com o meu namorado no domingo à tarde
```

Comportamento esperado:

- Agenda ginásio 3 vezes esta semana, de preferência de manhã.
- Agenda piano durante 20 minutos todos os dias até domingo.
- Agenda comprar ovos depois do evento de piano de hoje.
- Adiciona cinema na sexta-feira das 21:00 às 23:00.
- Adiciona o date no domingo à tarde.
- Evita eventos já existentes no calendário.

---

## Regras importantes de comportamento

- “Esta semana” significa **de hoje até domingo**, não os próximos 7 dias.
- Eventos para hoje não devem ser agendados antes da hora atual, a não ser que indiques explicitamente essa hora.
- Se não deres uma hora para um lembrete simples, o backend encontra o próximo horário livre.
- Se for mencionado um dia específico, como sexta ou domingo, o evento deve ficar nesse dia.
- Tarefas recorrentes continuam flexíveis e são colocadas à volta do teu calendário.

---

## Resolução de problemas

### O backend não inicia

Confirma que estás a usar o ambiente virtual do backend:

```bash
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

### `No module named openai`

Instala o pacote OpenAI dentro do ambiente virtual do backend:

```bash
cd backend
.\venv\Scripts\python.exe -m pip install openai
```

### Erros da Groq ou da IA

Confirma que o teu `.env` contém:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3-32b
```

Depois reinicia a aplicação.

### Eventos duplicados no calendário

Elimina os eventos de teste duplicados no Google Calendar antes de voltares a executar o mesmo prompt.

---

## Estrutura do projeto

```txt
backend/
  main.py
  llm_service.py
  calendar_service.py
  scheduler.py
  models.py
  requirements.txt
  .env

frontend/
  src/
  package.json

package.json
```
