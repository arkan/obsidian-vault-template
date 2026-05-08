---
name: morning
description: Morning brief routine. USE WHEN user says /morning, "start my day", "bonjour", "good morning", or wants a morning briefing.
user_invocable: true
argument: ""
---

# /morning → `/brief morning`

Immediately delegate to the `brief` skill with the `morning` argument. Load the brief skill and execute the morning.md workflow.

Do not reproduce the logic here — everything is in `.agents/skills/brief/workflows/morning.md`.
