---
name: weekly
description: Weekly brief routine. USE WHEN user says /weekly, "weekly review", "bilan de la semaine", or wants a weekly recap.
user_invocable: true
argument: ""
---

# /weekly → `/brief weekly`

Immediately delegate to the `brief` skill with the `weekly` argument. Load the brief skill and execute the weekly.md workflow.

Do not reproduce the logic here — everything is in `.agents/skills/brief/workflows/weekly.md`.
