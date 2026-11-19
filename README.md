# Clinic Appointment and Finance Agent

A LlamaIndex agent demo for helping clinic staff check appointment availability, manage bookings, retrieve limited billing details, and prepare daily financial summaries.

> **Project scope:** The runnable demo uses a local SQLite database containing fictional records only. It does not connect to a real clinic, patient record system, calendar, or accounting service. Do not enter real patient information.

## Assignment deliverables

1. **Use case:** Clinic appointment and financial management assistant.
2. **LLM and provider:** Llama 3.3 70B Instruct served locally through Ollama.
3. **Tools:** Availability check, appointment booking or rescheduling, read-only billing lookup, and daily financial report generation.
4. **System prompt:** A complete instruction set for tool selection, scheduling order, privacy, and reliable responses.
5. **Implementation:** A LlamaIndex `AgentWorkflow` using function tools and a local Ollama model.

## Repository structure

```text
Clinic_agent/
├── README.md
├── clinic_agent.py
├── requirements.txt
├── .gitignore
└── docs/
    ├── 01_brainstorming_and_use_case.md
    ├── 02_llm_and_provider.md
    ├── 03_tool_specifications.md
    ├── 04_agent_workflow.md
    └── 05_system_prompt.md
```

## How the agent works

```text
Staff request → LlamaIndex AgentWorkflow → clinic tools → verified result → staff response
```

The tools are ordinary typed Python functions that LlamaIndex exposes to the agent. The code also enforces two important rules: booking needs an availability check for the same slot, and the daily report tool is disabled unless the request explicitly asks for a daily summary or reconciliation.

## Run locally

1. Install [Ollama](https://ollama.com/download).
2. Pull the selected model and install the Python packages:

   ```bash
   ollama pull llama3.3
   python -m venv .venv
   # Activate the virtual environment, then:
   pip install -r requirements.txt
   python clinic_agent.py
   ```

The demo creates `clinic_demo.db` with fictional records the first time it runs. Set `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, or `CLINIC_DB` to override defaults. Type `quit` to exit.

The default Ollama `llama3.3` model is about 43 GB in its listed quantization, so confirm your machine has enough memory and disk space before downloading it. See the [Ollama model page](https://ollama.com/library/llama3.3).

## Example request

A staff member may ask:

> “Check whether Dr. Noor is free tomorrow at 10:00, then book Salma for a 30-minute visit.”

The assistant checks the requested slot first. The booking tool will reject a booking unless that exact doctor and time range were checked and available. It then rechecks for conflicts before writing to the local demo database.

## Important design principles

- **Verify before answering:** availability, bookings, and financial figures must come from tools.
- **Availability before booking:** scheduling always starts with a calendar check.
- **Read-only billing:** the billing lookup cannot modify records.
- **Explicit report requests:** generate a financial report only when staff explicitly ask for a daily summary or reconciliation.
- **Privacy:** return only the information needed; never reveal credentials or unnecessary patient identifiers.
- **Honest results:** report empty results and tool failures clearly; never claim an action succeeded without confirmation.
- **Human responsibility:** this assistant supports administrative work and does not provide medical advice or make clinical decisions.

## Detailed documentation

- [Brainstorming and use case](docs/01_brainstorming_and_use_case.md)
- [LLM and provider selection](docs/02_llm_and_provider.md)
- [Tool specifications](docs/03_tool_specifications.md)
- [Agent workflow](docs/04_agent_workflow.md)
- [Complete system prompt](docs/05_system_prompt.md)

## Safety and limits

- The booking and billing tools operate only on the fictional local demo database.
- This prototype has no authentication, staff authorization, production audit trail, or clinic system integration.
- Never use real patient data with this demo. A real deployment requires privacy/security review, identity and role controls, audit logging, retention controls, and transactional integration design.
- The assistant supports administrative work only; it does not provide medical advice or make clinical decisions.

