# 3. Tool specifications

The model may request tools, but application code remains responsible for validating arguments, enforcing staff authorization, and handling tool errors. Tool outputs should contain only the minimum information needed for the staff request.

## `check_calendar_availability`

Checks whether a doctor has a free slot for the requested interval.

**Input**

```json
{
  "doctor_name": "string",
  "starts_at": "ISO 8601 date-time",
  "ends_at": "ISO 8601 date-time"
}
```

**Output**

```json
{
  "available": "boolean",
  "doctor_name": "string",
  "starts_at": "ISO 8601 date-time",
  "ends_at": "ISO 8601 date-time",
  "error": "optional string"
}
```

The tool must reject invalid or reversed time ranges. It must not expose other patients' appointment details when a slot is occupied.

## `book_or_reschedule_appointment`

Creates a booking or updates an existing appointment. The agent must first call `check_calendar_availability` for the exact doctor and interval. The application should recheck conflicts as part of the write to prevent race conditions.

**Input**

```json
{
  "patient_name": "exact name in the demo directory",
  "doctor_name": "exact name in the demo directory",
  "starts_at": "ISO 8601 date-time",
  "ends_at": "ISO 8601 date-time",
  "appointment_id": "optional integer; required when rescheduling"
}
```

**Output**

```json
{
  "success": "boolean",
  "action": "booked | rescheduled",
  "appointment_id": "integer",
  "starts_at": "ISO 8601 date-time",
  "error": "optional string"
}
```

Only authorized staff may invoke this write operation. A failed write must not be described as a completed booking.

## `query_database`

Performs an approved, read-only billing lookup. It is a scoped application query, not an arbitrary SQL interface.

**Input**

```json
{
  "patient_name": "exact name in the demo billing records",
  "service_date": "optional YYYY-MM-DD"
}
```

**Output**

```json
{
  "records": [
    {
      "service_date": "YYYY-MM-DD",
      "description": "string",
      "amount": "number",
      "paid": "number"
    }
  ],
  "error": "optional string"
}
```

The tool must not modify records. Return only the fields needed to answer the request and avoid repeating patient identifiers unnecessarily.

## `generate_financial_report`

Returns a daily summary for a requested date. The agent may call this only after an explicit request for a daily summary or reconciliation.

**Input**

```json
{
  "report_date": "YYYY-MM-DD"
}
```

**Output**

```json
{
  "date": "YYYY-MM-DD",
  "billed_total": "number",
  "payments_collected": "number",
  "invoice_count": "integer",
  "error": "optional string"
}
```

The report should aggregate authorized clinic data and return totals with the report date. The assistant must not infer totals when the tool fails or returns no result.

