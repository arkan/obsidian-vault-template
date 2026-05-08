---
name: monthly
description: Monthly brief routine. USE WHEN user says /monthly, "monthly review", "bilan du mois", or wants a monthly recap.
user_invocable: true
argument: ""
---

# /monthly → `/brief monthly`

Immediately delegate to the `brief` skill with the `monthly` argument. Load the brief skill and execute the monthly.md workflow.

Do not reproduce the logic here — everything is in `.agents/skills/brief/workflows/monthly.md`.
