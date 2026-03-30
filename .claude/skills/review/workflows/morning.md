# Morning Routine

## Steps

### 1. Daily Note

Ensure today's daily note exists (lazy creation). Read it if it exists.

### 2. Today's Tasks

Read `Areas/TODO.md`:
- List tasks with deadline today or overdue
- List tasks with deadline in the next 7 days
- Present as table: | Task | Priority | Project | Deadline |

### 3. Active Goals

Read `Areas/Goals.md` section `## Active Goals`:
- Reminder of active goals with their deadlines
- Alert if a deadline is approaching (< 2 weeks)

### 4. Inbox

List files in `Inbox/`:
- If items exist: "You have X items in your Inbox to sort"
- If empty: skip silently

### 5. Active Projects

Read frontmatter of `Projects/*.md` where `status: active`:
- Quick status overview
- Flag any project without recent activity (last_synthesis > 2 weeks ago)

### 6. Summary

Present a concise morning briefing:
> "Good morning! You have X tasks today, Y overdue. Main goal: [goal]. Inbox: X items."

Ask: "What's your main focus for today?"

If user answers, append to daily note under `## Notes`:
```
**Today's focus**: <answer>
```
