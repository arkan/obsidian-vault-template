# Weekly Review (Sunday evening)

## Steps

### 1. Goals Review

Read `Areas/Goals.md` section `## Active Goals`:
- For each goal: status, time remaining before deadline, estimated progress
- Alert if a goal is at risk (deadline < 2 weeks without visible progress)

### 2. Project Audit

Read frontmatter of all `Projects/*.md`:
- Active projects without recent activity (`last_synthesis` > 2 weeks)
- Projects with `fact_count` of 0 (empty shells)
- Present: "X active projects, Y without recent activity"
- Suggest moving dormant projects to `backlog`

### 3. People/Companies Audit

Read frontmatter of `Areas/People/*.md` and `Areas/Companies/*.md`:
- Entities with potentially incorrect status
- Suggest corrections if needed

### 4. Week's Tasks

Read `Areas/TODO.md`:
- Tasks completed this week (grep for `✅ YYYY-MM-DD` where the date falls within the last 7 days from today)
- Overdue tasks
- Present summary: "X completed, Y overdue, Z added"

### 5. Full Inbox Triage

List all files in `Inbox/`:
- Sort each item (same process as evening routine)
- Goal: Inbox empty at end of review

### 6. Vault Metrics

Compute and present:
- Notes created this week (by folder)
- Facts added this week (read `## Active Facts` sections in entity files under `Projects/`, `Areas/People/`, `Areas/Companies/` and count facts whose ID date or surrounding context matches the current week)
- Tasks completed vs added
- Daily notes filled vs days of the week

### 7. Next Week Planning

Ask:
- "What are your top 3 priorities for next week?"
- Suggest tasks based on deadlines and goals

### 8. Create Weekly Review Note

Create `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD Weekly Review.md` with:
```markdown
---
type: review
tags: [review, weekly]
date: YYYY-MM-DD
week_number: WW
---

## Week WW Summary

### Goals
<goals status>

### Tasks
- Completed: X
- Overdue: Y
- Added: Z

### Projects
<project summary>

### Metrics
<vault metrics>

### Next Week Priorities
1. ...
2. ...
3. ...
```
