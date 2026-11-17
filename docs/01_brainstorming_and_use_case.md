# 1. Brainstorming and use case

## Proposed agent

**Clinic Appointment and Finance Assistant** is an administrative assistant for authorized clinic staff. It uses an LLM to understand staff requests, select approved tools, and summarize verified results.

## Problem

Front-desk and finance staff often switch among calendar, booking, billing, and reporting systems. This agent design brings common lookup and scheduling steps into one conversational workflow while preserving clear checks around writes and sensitive data.

## Intended users

- Reception and appointment scheduling staff
- Clinic billing or finance staff
- Authorized clinic administrators

The agent is not intended for patients to self-diagnose, for clinicians to make treatment decisions, or for autonomous financial operations.

## Core use cases

1. Check whether a named doctor has an appointment slot available.
2. Book a new appointment or reschedule an existing appointment after availability is checked.
3. Retrieve the minimum billing details needed to answer an authorized staff question.
4. Generate a daily financial summary or reconciliation when explicitly requested.

## Example request

> “Is Dr. Noor available tomorrow from 10:00 to 10:30? If so, book Salma Hassan.”

The assistant checks the calendar first. It makes the booking only when the exact slot is reported available, then communicates the tool’s confirmed result.

## Boundaries

- The assistant does not provide medical advice or triage patients.
- It does not invent patient IDs, availability, appointment details, or financial figures.
- It does not retrieve arbitrary database data or run arbitrary SQL.
- It does not create a daily finance report unless staff explicitly ask for a daily summary or reconciliation.
- A production deployment would require identity and role checks, audit trails, minimum-necessary data access, retention controls, and clinic privacy/security review.

