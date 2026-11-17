# Clinic Appointment and Finance Agent

An agentic AI design for helping authorized clinic staff check appointment availability, manage bookings, retrieve limited billing details, and prepare daily financial summaries.

> **Project scope:** This repository documents the agent design and assignment deliverables. It is a design prototype, not a live clinic application. It does not connect to patient records, book appointments, or execute financial operations.

## Assignment deliverables

1. **Use case:** Clinic appointment and financial management assistant.
2. **LLM and provider:** Llama 3.3 70B Instruct served locally through Ollama.
3. **Tools:** Availability check, appointment booking or rescheduling, read-only billing lookup, and daily financial report generation.
4. **System prompt:** A complete instruction set for tool selection, scheduling order, privacy, and reliable responses.

## Repository structure

```text
Clinic_agent/
├── README.md
└── docs/
    ├── 01_brainstorming_and_use_case.md
    ├── 02_llm_and_provider.md
    ├── 03_tool_specifications.md
    ├── 04_agent_workflow.md
    └── 05_system_prompt.md
```

## Quick overview

A staff member may ask:

> “Check whether Dr. Noor is free tomorrow at 10:00, then book Salma for a 30-minute visit.”

The assistant first checks the requested slot. If the slot is unavailable, it reports that and does not book. If it is available, it proceeds with the booking tool and reports only the confirmed result.

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

## Status

**Design and documentation prototype.** Connecting clinic systems, authentication, authorization, audit logging, privacy review, implementation, and operational testing are separate future phases.

