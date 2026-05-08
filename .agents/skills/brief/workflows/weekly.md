# Weekly Review (Sunday evening)

## Steps

### 1. Goals Review

Read `Areas/Goals.md` section `## Objectifs`:
- For each goal: status, time remaining before deadline, estimated progress
- Alert if a goal is at risk (deadline < 2 weeks with no visible progress)

### 2. Projects Audit

Read frontmatter of all `Projects/*.md`:
- Active projects without recent activity (`last_synthesis` > 2 weeks)
- Projects with `fact_count` of 0 (empty shells)
- Present: "X projets actifs, Y sans activite recente"
- Propose moving dormant projects to `backlog`

### 3. People/Companies Audit

Read frontmatter of `Areas/People/*.md` and `Areas/Companies/*.md`:
- Entities with potentially incorrect status
- Propose corrections if needed

### 4. This Week's Tasks

Use `td list --completed` and `td list`:
- Tasks completed this week — parse `td list --completed` output, filter lines with `✅ YYYY-MM-DD` where the date falls within the last 7 days
- Overdue tasks — `td list` shows tasks with due date ≤ today
- Present summary: "X completed, Y overdue, Z added"

### 5. Full Inbox Triage

List all files in `Inbox/` (excluding `A trier.md`):
- Triage each item (same process as evening routine)
- Goal: empty inbox by end of review

### 6. Vault Metrics

Compute and present:
- Notes created this week (by folder)
- Facts added this week (read `## Active Facts` sections in entity files under `Projects/`, `Areas/People/`, `Areas/Companies/` and count facts whose ID date or surrounding context matches the current week)
- Tasks completed vs added
- Daily notes filled vs days of the week

### 6b. Vault Lint

Run vault-lint checks and include results in the weekly brief:
1. Run all 7 checks (same as `/vault-lint`)
2. Append summary to weekly brief note under `## Sante du vault`
3. If critical issues found (>5 broken wikilinks, >10 stale drafts), flag them prominently
4. Do NOT auto-fix — just report for user decision

### 7. Next Week Planning

Ask:
- "Quelles sont tes 3 priorites pour la semaine prochaine ?"
- Propose tasks based on deadlines and goals

### 8. Weekly Brief Note Creation

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
<projects summary>

### Metrics
<vault metrics>

### Next Week Priorities
1. ...
2. ...
3. ...
```
