# 4. Agent workflow

## Request handling

1. **Understand the request.** Identify whether the staff member is asking about availability, a booking/reschedule, billing, or an explicitly requested daily financial report.
2. **Check required details.** Ask for missing or ambiguous information. Do not guess patient or doctor identifiers, time ranges, or report dates.
3. **Select the approved tool.** Use only the tool that matches the request. If no tool is needed, answer directly without inventing clinic facts.
4. **Enforce sequencing and scope.** Check calendar availability before booking or rescheduling. Keep billing lookup read-only. Call the daily report tool only for an explicit daily-summary or reconciliation request.
5. **Validate tool arguments and authorization.** The application, not the model, enforces access rights, data scope, and write permissions.
6. **Handle result or failure.** Report confirmed outcomes. If a tool errors or returns no result, state that the information is unavailable and suggest the next step.
7. **Respond clearly.** Summarize only the relevant information and avoid unnecessary patient identifiers.

## Booking sequence

```text
Staff asks to book or reschedule
              │
              ▼
Are patient, doctor, and time details clear?
      ├── No ──► Ask staff for missing details
      └── Yes
              │
              ▼
check_calendar_availability
      ├── Unavailable/error ──► Explain result; do not book
      └── Available
              │
              ▼
book_or_reschedule_appointment
              │
              ▼
Report only the confirmed tool result
```

## Finance sequence

- For a billing question, use the scoped, read-only `query_database` tool.
- For a daily summary or reconciliation, verify that the request is explicit, then use `generate_financial_report` for the specified date.
- If the relevant tool has no data or fails, say so. Do not estimate, infer, or fabricate financial values.

