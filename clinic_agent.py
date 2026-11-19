"""LlamaIndex clinic assistant demo backed only by synthetic local SQLite data."""
from __future__ import annotations

import asyncio
import json
import os
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("CLINIC_DB", ROOT / "clinic_demo.db"))
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3.3")
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def connect(db_path: Path = DB_PATH, *, read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
        db = sqlite3.connect(uri, uri=True, timeout=10)
    else:
        db = sqlite3.connect(db_path, timeout=10)
    db.row_factory = sqlite3.Row
    return db


def initialize_demo_database(db_path: Path = DB_PATH) -> None:
    """Create local tables and fictional records used by this prototype."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            ends_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'booked'
        );
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY,
            patient_name TEXT NOT NULL,
            service_date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            paid REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            paid_at TEXT NOT NULL,
            amount REAL NOT NULL
        );
        """)
        db.executemany("INSERT OR IGNORE INTO doctors(name) VALUES(?)", [("Dr. Noor",), ("Dr. Omar",)])
        db.executemany("INSERT OR IGNORE INTO patients(name) VALUES(?)", [("Demo Patient A",), ("Demo Patient B",)])
        if db.execute("SELECT COUNT(*) FROM billing").fetchone()[0] == 0:
            today = date.today().isoformat()
            db.executemany(
                "INSERT INTO billing(patient_name,service_date,description,amount,paid) VALUES(?,?,?,?,?)",
                [("Demo Patient A", today, "Consultation", 75.0, 75.0),
                 ("Demo Patient B", today, "Follow-up", 50.0, 20.0)],
            )
            now = datetime.now().isoformat(timespec="seconds")
            db.executemany("INSERT INTO payments(paid_at,amount) VALUES(?,?)", [(now, 75.0), (now, 20.0)])


def _as_local_datetime(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is not None:
        raise ValueError("Use the clinic's local time without a UTC offset.")
    return result


def _iso_minute(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


def _explicit_daily_report_request(text: str) -> bool:
    temporal = r"\b(daily|today|today's|day's)\b"
    report = r"\b(summary|report|reconciliation)\b"
    near = r"(?:\W+\w+){0,4}\W+"
    return bool(
        re.search(temporal + near + report, text, re.I)
        or re.search(report + near + temporal, text, re.I)
        or re.search(r"\bfinancial reconciliation\b", text, re.I)
    )


def build_tools(db_path: Path = DB_PATH) -> tuple[list[Any], dict[str, Any]]:
    """Build the four LlamaIndex tools and their per-chat safety state."""
    state: dict[str, Any] = {"availability_checks": set(), "report_allowed": False}

    def check_calendar_availability(doctor_name: str, starts_at: str, ends_at: str) -> str:
        """Check a doctor's exact appointment interval; do this before booking or rescheduling."""
        try:
            start, end = _as_local_datetime(starts_at), _as_local_datetime(ends_at)
            if end <= start:
                return json.dumps({"available": False, "error": "End time must be after start time."})
            start_text, end_text = _iso_minute(start), _iso_minute(end)
            with connect(db_path, read_only=True) as db:
                doctor = db.execute("SELECT 1 FROM doctors WHERE name = ?", (doctor_name,)).fetchone()
                if doctor is None:
                    return json.dumps({"available": False, "error": "Doctor not found in the demo directory."})
                occupied = db.execute(
                    """SELECT 1 FROM appointments WHERE doctor_name = ? AND status = 'booked'
                    AND starts_at < ? AND ends_at > ? LIMIT 1""",
                    (doctor_name, end_text, start_text),
                ).fetchone()
            available = occupied is None
            key = (doctor_name, start_text, end_text)
            if available:
                state["availability_checks"].add(key)
            else:
                state["availability_checks"].discard(key)
            return json.dumps({"available": available, "doctor_name": doctor_name,
                               "starts_at": start_text, "ends_at": end_text})
        except (ValueError, sqlite3.Error) as exc:
            return json.dumps({"available": False, "error": f"Availability is unavailable: {type(exc).__name__}."})

    def book_or_reschedule_appointment(
        patient_name: str,
        doctor_name: str,
        starts_at: str,
        ends_at: str,
        appointment_id: int = 0,
    ) -> str:
        """Book or reschedule only after availability was checked for this exact slot."""
        try:
            start, end = _as_local_datetime(starts_at), _as_local_datetime(ends_at)
            if end <= start:
                return json.dumps({"success": False, "error": "End time must be after start time."})
            start_text, end_text = _iso_minute(start), _iso_minute(end)
            key = (doctor_name, start_text, end_text)
            if key not in state["availability_checks"]:
                return json.dumps({"success": False, "error": "Check this exact time with check_calendar_availability first."})
            with connect(db_path) as db:
                db.execute("BEGIN IMMEDIATE")
                patient = db.execute("SELECT 1 FROM patients WHERE name = ?", (patient_name,)).fetchone()
                doctor = db.execute("SELECT 1 FROM doctors WHERE name = ?", (doctor_name,)).fetchone()
                if patient is None or doctor is None:
                    return json.dumps({"success": False, "error": "Patient or doctor not found in the demo directory."})
                overlap = db.execute(
                    """SELECT id FROM appointments WHERE doctor_name = ? AND status = 'booked'
                    AND starts_at < ? AND ends_at > ? AND (? = 0 OR id != ?) LIMIT 1""",
                    (doctor_name, end_text, start_text, appointment_id, appointment_id),
                ).fetchone()
                if overlap:
                    return json.dumps({"success": False, "error": "That time is no longer available; check again."})
                if appointment_id:
                    result = db.execute(
                        """UPDATE appointments SET patient_name=?, doctor_name=?, starts_at=?, ends_at=?, status='booked'
                        WHERE id=?""",
                        (patient_name, doctor_name, start_text, end_text, appointment_id),
                    )
                    if result.rowcount == 0:
                        return json.dumps({"success": False, "error": "Appointment not found."})
                    action = "rescheduled"
                    result_id = appointment_id
                else:
                    result = db.execute(
                        "INSERT INTO appointments(patient_name,doctor_name,starts_at,ends_at) VALUES(?,?,?,?)",
                        (patient_name, doctor_name, start_text, end_text),
                    )
                    action = "booked"
                    result_id = result.lastrowid
            state["availability_checks"].discard(key)
            return json.dumps({"success": True, "action": action, "appointment_id": result_id,
                               "doctor_name": doctor_name, "starts_at": start_text, "ends_at": end_text})
        except (ValueError, sqlite3.Error) as exc:
            return json.dumps({"success": False, "error": f"Appointment action failed: {type(exc).__name__}."})

    def query_database(patient_name: str, service_date: str = "") -> str:
        """Read billing details for one exact patient name; this tool never modifies data."""
        try:
            query = "SELECT service_date, description, amount, paid FROM billing WHERE patient_name = ?"
            values: list[Any] = [patient_name]
            if service_date:
                datetime.strptime(service_date, "%Y-%m-%d")
                query += " AND service_date = ?"
                values.append(service_date)
            query += " ORDER BY service_date DESC LIMIT 20"
            with connect(db_path, read_only=True) as db:
                rows = db.execute(query, values).fetchall()
            return json.dumps({"records": [dict(row) for row in rows]}, ensure_ascii=False)
        except (ValueError, sqlite3.Error) as exc:
            return json.dumps({"records": [], "error": f"Billing information is unavailable: {type(exc).__name__}."})

    def generate_financial_report(report_date: str) -> str:
        """Generate a daily financial summary only after an explicit daily-summary or reconciliation request."""
        if not state["report_allowed"]:
            return json.dumps({"error": "A daily summary or financial reconciliation must be explicitly requested."})
        try:
            datetime.strptime(report_date, "%Y-%m-%d")
            with connect(db_path, read_only=True) as db:
                billed = db.execute(
                    "SELECT COALESCE(SUM(amount), 0) FROM billing WHERE service_date = ?", (report_date,)
                ).fetchone()[0]
                collected = db.execute(
                    "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE substr(paid_at, 1, 10) = ?",
                    (report_date,),
                ).fetchone()[0]
                invoices = db.execute(
                    "SELECT COUNT(*) FROM billing WHERE service_date = ?", (report_date,)
                ).fetchone()[0]
            return json.dumps({"date": report_date, "billed_total": round(billed, 2),
                               "payments_collected": round(collected, 2), "invoice_count": invoices})
        except (ValueError, sqlite3.Error) as exc:
            return json.dumps({"error": f"Financial report is unavailable: {type(exc).__name__}."})

    return [check_calendar_availability, book_or_reschedule_appointment, query_database,
            generate_financial_report], state


def load_system_prompt() -> str:
    prompt_doc = (ROOT / "docs" / "05_system_prompt.md").read_text(encoding="utf-8")
    prompt = prompt_doc.split("```text", 1)[1].split("```", 1)[0].strip()
    return prompt + f"\n\nCurrent local date: {date.today().isoformat()}. Use it when interpreting relative dates."


async def chat() -> None:
    initialize_demo_database(DB_PATH)
    tools, state = build_tools(DB_PATH)
    llm = Ollama(
        model=MODEL_NAME,
        base_url=OLLAMA_URL,
        request_timeout=300.0,
        context_window=8192,
    )
    agent = AgentWorkflow.from_tools_or_functions(
        tools,
        llm=llm,
        system_prompt=load_system_prompt(),
    )
    context = Context(agent)

    print(f"Clinic assistant demo | LlamaIndex + Ollama ({MODEL_NAME})")
    print(f"Synthetic database: {DB_PATH}")
    print("Do not enter real patient information. Type 'quit' to exit.\n")
    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_message.lower() in {"quit", "exit"}:
            break
        if not user_message:
            continue
        state["availability_checks"].clear()
        state["report_allowed"] = _explicit_daily_report_request(user_message)
        try:
            response = await agent.run(user_msg=user_message, ctx=context)
            print(f"Assistant: {response}\n")
        except Exception as exc:
            print(f"Assistant: The request could not be completed ({type(exc).__name__}). Check Ollama and retry.\n")


if __name__ == "__main__":
    asyncio.run(chat())

