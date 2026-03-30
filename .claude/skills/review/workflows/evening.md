# Evening Routine

## Steps

### 1. Daily Note

Ensure today's daily note exists at `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md` (lazy creation).

### 2. Mood & Sleep

Ask the user:
- "How are you feeling tonight? (mood 1-10)"
- "How did you sleep last night? (good/average/poor + hours)"

Update the daily note frontmatter with `mood` and `sleep` values.

### 3. Claude Code Summary

Generate the daily Claude activity summary if it doesn't exist yet:
1. Check if `Areas/Claude/YYYY-MM-DD-claude.md` exists (with today's date)
2. If **not**, invoke the skill `daily-claude-code-resume` to generate it
3. If it **already exists**, skip generation

Then read `Areas/Claude/YYYY-MM-DD-claude.md` and extract the key highlights:
- Important technical decisions
- Resolved bugs
- Features shipped or significantly advanced
- Notable discoveries or learnings
- PRs created or merged

Append these highlights to the daily note under `## Notes` as:
```
**Claude activity**:
- highlight 1
- highlight 2
- ...
```

The goal is a synthetic but exhaustive view of everything that happened via Claude today. Cover all projects worked on — do not cherry-pick.

### 4. Day Summary

Read `Areas/TODO.md`:
- List tasks completed today (marked `✅ YYYY-MM-DD` with today's date)
- List tasks still open with today's deadline (overdue)

Present: "Today you completed X tasks. Y are still overdue."

### 5. Inbox Triage

List files in `Inbox/`:
- If items exist, for each item:
  - Read the file content
  - Ask: "What should we do with this? (project/task/note/archive/delete)"
  - Based on answer: move to appropriate location or convert to task in TODO.md
- If empty: "Inbox empty, nothing to sort."

### 6. Fact Proposals

Review the current conversation context. If any factual information about known entities (projects, people, companies) was discussed today:
- List proposed facts with target entity
- Ask: "I suggest adding these facts. OK?"
- If approved, append facts to the entity files using the `#status/active` inline tag format:
  ```
  - `ENTITY-NNN` Fact description #status/active
  ```
- Update `fact_count` and `last_synthesis` in entity frontmatter

### 7. Day Log

Append a brief summary to the daily note under `## Log`:
```
- Tasks completed: X
- Inbox sorted: Y items
- Facts added: Z
```

### 8. Wrap Up

> "Good evening! Tomorrow, priority: [highest priority open task or goal]"
