# Monthly Review

## Steps

### 1. Month Retrospective

Read weekly review notes from the past month (`Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD Weekly Review.md`):
- Recurring themes
- Productivity patterns (mood, tasks completed)
- What worked well vs what didn't

Present a synthesis and ask:
- "Qu'est-ce qui t'a le plus satisfait ce mois-ci ?"
- "Qu'est-ce que tu changerais ?"

### 2. Goals Progress Review

Read `Areas/Goals.md`:
- For each goal: progress since start, time remaining, current pace
- **Projection**: compare the percentage of tasks/facts completed vs percentage of time elapsed before the deadline (from `Goals.md`). Ex: if 40% of time has passed but only 20% of tasks are done → at risk.
- Formulate: "At this pace, the goal will be met / will not be met on time"
- If a goal is at risk: propose corrective actions or a deadline revision

### 3. Cleanup and Archiving

Scan `Projects/*.md`:
- Projects with `status: active` but no activity for > 1 month → propose `backlog` or `archived`
  - **Activity definition**: a project is considered active this month if its `last_synthesis` was updated this month OR if new facts were added under `## Active Facts` this month
- Completed projects (`status: done`) → propose moving to `Archive/`

Scan tasks via `td list --all` and `td list --backlog`:
- Tasks open for > 1 month without activity → propose deletion or rescheduling
  - `td` does not provide an age filter; read `Areas/TODO.md` directly only for this metric

### 4. Vault Health

Monthly metrics:
- Total notes, facts, tasks
- Breakdown by PARA folder
- Daily notes filled vs days in the month (fill rate)
- Inbox: number of items processed this month

### 5. Monthly Review Note Creation

Create `Daily Notes/YYYY/YYYY-MM/YYYY-MM Monthly Review.md` with:
```markdown
---
type: review
tags: [review, monthly]
date: YYYY-MM-DD
month: YYYY-MM
---

## Retrospective - <Month YYYY>

### What Worked Well
<from user input>

### What Didn't Work
<from user input>

### Goals
| Goal | Deadline | Progress | Status |
|------|----------|----------|--------|

### Cleanup
- Projects archived: X
- Tasks removed: Y

### Metrics
<vault metrics>

### Next Month Focus
<from user input>
```
