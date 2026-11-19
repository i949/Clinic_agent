# 6. LlamaIndex implementation

This implementation adapts the supplied LlamaIndex agents notebook to the clinic use case. It uses the notebook's `AgentWorkflow` and tool-function pattern while keeping the assignment's selected model and provider: Llama 3.3 70B Instruct through local Ollama.

## 6.1 Mapping from the course notebook

| Notebook concept | Clinic implementation |
|---|---|
| LlamaIndex local LLM integration | `Ollama` initializes the local Llama 3.3 model |
| `AgentWorkflow.from_tools_or_functions` | Coordinates the assistant with its clinic tools |
| Typed Python tool functions | Defines the tool names, parameters, and descriptions |
| `Context` | Keeps the agent's conversation context during the interactive session |
| SQLite tool data | Checks availability, writes demo appointments, reads billing data, and calculates daily totals |

The supplied notebook also demonstrates Hugging Face inference and retrieval-augmented generation. This project uses Ollama to match the assignment brief and does not add a policy RAG tool because the requested clinic tools already access their source-of-truth demo records. No Hugging Face token or hosted model key is needed.

## 6.2 Architecture

```text
Staff request
     │
     ▼
LlamaIndex AgentWorkflow ─── Ollama: Llama 3.3 70B Instruct
     │
     ├── check_calendar_availability ─┐
     ├── book_or_reschedule_appointment ├── local SQLite demo database
     ├── query_database ────────────────┤        ▲
     └── generate_financial_report ─────┘        │
                                                CSV fixtures
     Tool results → agent reasoning → staff response
```

The appointment tool rejects requests unless the exact slot was checked in the current turn. It also checks for conflicts inside the SQLite write transaction. The financial report tool rejects calls unless the current user message explicitly requests a daily summary or reconciliation.

## 6.3 Requirements

Use Python 3.10 or newer. Install Ollama, then pull the model. Its default quantization is approximately 43 GB, so check available memory and storage first.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Pull the model and start the agent:

```powershell
ollama pull llama3.3
Copy-Item .env.example .env
python clinic_agent.py
```

The `.env` file is optional for default settings and is excluded by `.gitignore`. It may be used to set `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `CLINIC_DB`, or the CSV fixture paths. Do not put real patient data, passwords, or API keys in it.

## 6.4 Clinic tools

The four tools are typed Python functions exposed through LlamaIndex's `AgentWorkflow.from_tools_or_functions`.

| Tool | Behavior |
|---|---|
| `check_calendar_availability` | Checks that a doctor exists in the demo directory and that the requested interval has no scheduled appointment |
| `book_or_reschedule_appointment` | Requires a successful check for the same time range, validates the demo patient and doctor, then rechecks conflicts before writing |
| `query_database` | Performs a read-only billing lookup for an exact demo patient name and optional service date |
| `generate_financial_report` | Calculates daily billed total, payments collected, and invoice count; requires an explicit daily-report request |

LlamaIndex derives tool schemas from the functions' names, type annotations, and docstrings. The system prompt tells the agent when to choose each tool; runtime guards enforce the important scheduling and report rules.

## 6.5 Demo data and database

The files in `data/` are fictional fixtures:

- `doctors.csv` and `patients.csv` define the demo directory.
- `appointments.csv` starts empty so the demo calendar has no existing bookings.
- `billing.csv` and `payments.csv` provide small sample records for billing lookups and daily reports.

At startup, the script creates `clinic_demo.db` and imports the fixtures into SQLite. The database is local and ignored by Git. If you edit fixture files after the database has been initialized, remove `clinic_demo.db` and restart to re-import the samples.

## 6.6 Example prompts

```text
Is Dr. Noor available on 2026-11-20 from 10:00 to 10:30?
Check Dr. Omar at 2026-11-20 11:00–11:30 and book Demo Patient A if free.
Look up Demo Patient B's billing records for 2026-11-19.
Generate today's daily financial summary for 2026-11-19.
```

Use exact demo names and ISO dates in these examples. The sample patient names are not real patient identifiers.

## 6.7 Safety and limitations

- The application reads and writes only the local fictional database created from the sample files.
- The demo has no staff authentication, role authorization, real calendar connection, or real billing-system connection.
- The local 70B model has high hardware requirements and may respond slowly on unsupported hardware.
- Tool-call reliability can vary by Ollama version and model quantization; validate behavior before any deployment.
- Do not use real patient records. Production use requires a privacy/security review, access controls, audit logging, retention policies, and integration-specific safeguards.
- The agent is administrative only and must not provide medical advice.

