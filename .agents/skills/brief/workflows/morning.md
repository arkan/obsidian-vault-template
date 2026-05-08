# Morning Routine

## Steps

### 1. Daily Note

Ensure today's daily note exists (lazy creation). Read it if it exists.

### 2. Tasks

Use the `td` CLI (never read `Areas/TODO.md` directly). Present tasks in **two distinct tables**:

#### 2a. Today's Tasks

Run `td list`. This returns tasks with `📅 <= today` or no date — the time-sensitive items.

- Present the output as-is (comfy-table formatted). Extract and reformat as markdown if needed for readability.
- If the command returns 0 tasks: write "Rien d'urgent aujourd'hui" and skip the table.

#### 2b. All Open Tasks (by priority)

Run `td list --all`. This returns all active tasks, sorted by priority descending then due date descending.

- Present the output as-is or as a markdown table.
- If the result is identical to 2a (all tasks are due today or overdue), merge into a single table to avoid redundancy.

Why two tables instead of one: the morning briefing has a dual purpose — react to what's due today, AND keep the broader backlog in mind. A single sorted list buries one of those two needs. Two tables make both legible at a glance.

### 3. Active Goals

Read `Areas/Goals.md` section `## Objectifs`:
- Recap of active goals with their deadlines
- Alert if a deadline is approaching (< 2 weeks)

### 4. Inbox

List files in `Inbox/` (excluding `A trier.md`):
- If items exist: "Tu as X items dans l'Inbox a trier"
- If empty: skip silently

### 5. Active Projects

Read frontmatter of `Projects/*.md` where `status: active`:
- Quick status overview
- Flag any project without recent activity (last_synthesis > 2 weeks ago)

### 6. Summary

Present a concise morning briefing:
> "Bonjour ! Tu as X tâches aujourd'hui, Y en retard. Objectif principal : [goal]. Inbox : X items."

Ask: "Quel est ton focus principal pour aujourd'hui ?"

If user answers, append to daily note under `## Notes`:
```
**Focus du jour** : <answer>
```
