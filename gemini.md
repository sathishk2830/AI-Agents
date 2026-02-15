# gemini.md — Project Constitution

Created: 2026-02-15

Purpose: This file holds the authoritative data schemas, behavioral rules, and architectural invariants. Changes to schema or rules must be recorded here.

1) Data Schemas (REQUIRED before coding)

- Input Schema (define exact JSON shape expected by tools):

```json
{
  "example_input": {
    "id": "string",
    "payload": {}
  }
}
```

- Output Schema (define exact JSON shape produced by tools):

```json
{
  "example_output": {
    "id": "string",
    "status": "string",
    "result": {}
  }
}
```

Instructions: Replace the example schemas above with the definitive Input/Output shapes for this project. Do not start building `tools/` until these are confirmed.

2) Behavioral Rules

- Tone / Safety rules:
  - e.g., "Respond politely; do not disclose PII; obey rate limits"

- Operational rules:
  - e.g., "All API calls must use retries with exponential backoff"

3) Architectural Invariants

- Components that must not change without explicit review (e.g., auth flow, primary database schema).

4) Maintenance Log

- 2026-02-15: gemini.md created (initial template). Any changes must be recorded here with date and rationale.
