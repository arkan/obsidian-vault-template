# Monthly Review

## Steps

### 1. Month Retrospective

Read weekly review notes from the past month (`Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD Weekly Review.md`):
- Recurring themes
- Productivity patterns (mood, tasks completed)
- What worked well vs what didn't

Present a synthesis and ask:
- "What are you most satisfied with this month?"
- "What would you change?"

### 2. Goal Progress Report

Read `Areas/Goals.md`:
- For each goal: progress since start, time remaining, current pace
- **Projection**: compare the percentage of tasks/facts completed vs the percentage of time elapsed before the deadline (from `Goals.md`). E.g.: if 40% of time has passed but only 20% of tasks are done → at risk.
- State: "At this pace, the goal will / will not be reached on time"
- If a goal is at risk: suggest corrective actions or a deadline revision

### 3. Cleanup and Archiving

Scan `Projects/*.md`:
- Projects with `status: active` but no activity for > 1 month → suggest `backlog` or `archived`
  - **Activity definition**: a project is considered active in the month if its `last_synthesis` was updated this month OR if new facts were added to `## Active Facts` this month
- Completed projects (`status: done`) → suggest moving to `Archive/`

Scan `Areas/TODO.md`:
- Tasks open for > 1 month without activity → suggest deletion or rescheduling

### 4. Vault Health

Monthly metrics:
- Total notes, facts, tasks
- Distribution by PARA folder
- Daily notes filled vs days in the month (fill rate)
- Inbox: number of items processed during the month

### 5. Create Monthly Review Note

Create `Daily Notes/YYYY/YYYY-MM/YYYY-MM Monthly Review.md` with:
```markdown
---
type: review
tags: [review, monthly]
date: YYYY-MM-DD
month: YYYY-MM
---

## Retrospective - <Month YYYY>

### What worked well
<from user input>

### What didn't work
<from user input>

### Goals
| Goal | Deadline | Progress | Status |
|------|----------|----------|--------|

### Cleanup
- Projects archived: X
- Tasks deleted: Y

### Metrics
<vault metrics>

### Next Month Focus
<from user input>
```
