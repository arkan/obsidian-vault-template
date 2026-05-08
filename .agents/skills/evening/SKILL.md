---
name: evening
description: Evening brief routine. USE WHEN user says /evening, "end of day", "bonne nuit", "evening review", or wants an end-of-day recap.
user_invocable: true
argument: ""
---

# /evening → `/brief evening`

Immediately delegate to the `brief` skill with the `evening` argument. Load the brief skill and execute the evening.md workflow.

Do not reproduce the logic here — everything is in `.agents/skills/brief/workflows/evening.md`.
