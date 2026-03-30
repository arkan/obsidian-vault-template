---
type: goals
tags:
  - dashboard
  - goals
---

# Goals

## Active Goals

### 1. Ship the SaaS Dashboard MVP to production

- **Project**: [[SaaS-Dashboard]]
- **Deadline**: June 2026
- **Definition of Done**: 10 paying clients, automated onboarding, PDF export
- **Status**: In progress

### 2. Launch the mobile app beta

- **Project**: [[Mobile-App]]
- **Deadline**: May 2026
- **Definition of Done**: 50 beta testers, TestFlight store, 0 critical crashes
- **Status**: In progress

## Project Tracking

```dataview
TABLE WITHOUT ID file.link as "Project", status, fact_count as "Facts", last_synthesis as "Synthesis"
FROM "Projects"
WHERE status = "active"
SORT file.name
```

## Archived Goals

*(None at this time)*
