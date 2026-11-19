# Clinic Appointment and Finance Agent

**An agentic AI assistant concept for clinic appointment scheduling, billing lookups, and daily financial summaries.**

This project helps authorized clinic staff check a doctor's availability, book or reschedule appointments, retrieve limited billing details, and prepare daily financial reports. LlamaIndex coordinates the agent and tools; Ollama serves the selected local LLM.

> **Project scope:** This is an implementation prototype using fictional sample records. It does not connect to a real clinic calendar or patient billing system and must not be used with real patient information.

## Assignment deliverables

1. **Use case:** Automated clinic appointment and financial management assistant.
2. **LLM and provider:** Llama 3.3 70B Instruct served locally by Ollama.
3. **Tools:** Availability check, appointment booking/rescheduling, read-only billing lookup, and daily financial report.
4. **System prompt:** Instructions for tool use, scheduling order, privacy, and reliable responses.
5. **Implementation:** LlamaIndex `AgentWorkflow` with typed function tools.

## Repository structure

```text
Clinic_agent/
├── README.md
├── clinic_agent.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── doctors.csv
│   ├── patients.csv
│   ├── appointments.csv
│   ├── billing.csv
│   └── payments.csv
└── docs/
    ├── 01_brainstorming_and_use_case.md
    ├── 02_llm_and_provider.md
    ├── 03_tool_specifications.md
    ├── 04_agent_workflow.md
    ├── 05_system_prompt.md
    └── 06_llamaindex_implementation.md
```

## Quick overview

A staff member may ask:

> “Check whether Dr. Noor is available tomorrow at 10:00, and book Demo Patient A if the slot is free.”

The agent checks availability first. It books only after the exact doctor and time range have been checked and found available, then reports the confirmed result.

## Important design principles

- **Verify before answering:** availability, appointment changes, and financial figures must come from tools.
- **Availability before booking:** the booking tool requires a successful check for the same slot and checks conflicts again before writing.
- **Read-only billing lookup:** `query_database` can return limited billing fields and cannot modify records.
- **Explicit daily reports:** call `generate_financial_report` only for an explicit daily summary or reconciliation request.
- **Privacy:** do not expose unnecessary patient identifiers, credentials, or sensitive records.
- **Honest results:** explain unavailable information and tool failures; never claim an action succeeded without confirmation.
- **Administrative scope:** the assistant does not provide medical advice or make clinical decisions.

## Detailed documentation

- [Brainstorming and use case](docs/01_brainstorming_and_use_case.md)
- [LLM and provider selection](docs/02_llm_and_provider.md)
- [Tool specifications](docs/03_tool_specifications.md)
- [Agent workflow](docs/04_agent_workflow.md)
- [System prompt](docs/05_system_prompt.md)
- [LlamaIndex implementation](docs/06_llamaindex_implementation.md)

## LlamaIndex implementation

The Python demo uses LlamaIndex's agent workflow with typed functions for the clinic tools. It follows the notebook's `AgentWorkflow` pattern and connects to Ollama using the local LLM integration. The notebook demonstrates other provider integrations too; this project keeps Ollama to match the assignment brief.

The clinic tools operate on a local SQLite database initialized from the fictional CSV files in `data/`. The implementation does not include the reference project's finance-specific tools or document RAG because those do not match this clinic task's requested tools.

## Run locally

1. Install [Ollama](https://ollama.com/download).
2. Pull the model and install the Python dependencies:

   ```powershell
   ollama pull llama3.3
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   python clinic_agent.py
   ```

The demo creates `clinic_demo.db` from the CSV files on first run. Type `quit` to exit. The local database is ignored by Git. If you change the sample CSV files after the database has been created, remove the demo database to reload the sample data.

The listed default Ollama model is about 43 GB in its default quantization. Confirm you have enough memory and storage before downloading it. See the [Ollama model page](https://ollama.com/library/llama3.3).

## Example scenario

The included fictional records contain two demo patients, two doctors, sample invoices, and payments dated November 19, 2026. The appointment fixture starts empty, so the demo calendar initially has no scheduled slots. These values only demonstrate the tool flow; they are not real clinic data.

## Safety and limitations

- The CSV records and SQLite database are fictional and local.
- This prototype has no authentication, role-based access, production audit logging, or clinic integration.
- Never put real patient records in the sample files or the demo database.
- A real deployment requires clinic privacy/security review, staff identity and authorization, audit and retention controls, and transactional integration testing.
- The assistant supports administrative tasks only.

## Future Work

- Replace sample records with approved calendar and billing integrations, starting in a sandbox or read-only environment.
- Add staff sign-in, role-based access, and patient-record authorization checks before exposing clinic data or enabling appointment changes.
- Add audit logging, privacy and retention controls, secure configuration, and operational monitoring.
- Add explicit confirmation and recovery flows for bookings and rescheduling, including duplicate-request and concurrent-booking handling.
- Evaluate tool selection, date handling, financial calculations, and failure responses across supported model versions.
- Assess hardware and response-time needs for Llama 3.3 70B and document a smaller local-model option if needed.

## Status

**Runnable implementation prototype.** Production clinic integrations, authentication, operational safeguards, and deployment remain future work.

