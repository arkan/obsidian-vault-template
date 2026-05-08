# Evening Routine

## Steps

### 1. Daily Note

Ensure today's daily note exists at `Daily Notes/YYYY/YYYY-MM/YYYY-MM-DD.md` (lazy creation).

### 2. Mood & Sleep

Ask the user:
- "Comment tu te sens ce soir ? (mood 1-10)"
- "Comment as-tu dormi la nuit derniere ? (sleep: bien/moyen/mal + heures)"

Update the daily note frontmatter with `mood` and `sleep` values.

### 3. Claude Code Summary

Generate the daily Claude activity summary if it doesn't exist yet:
1. Check if `Areas/Claude/YYYY-MM-DD-claude.md` exists (with today's date)
2. If **not**, invoke the skill `daily-claude-code-resume` to generate it
3. If it **already exists**, skip generation

Then read `Areas/Claude/YYYY-MM-DD-claude.md` and extract the key highlights:
- Important technical decisions
- Bugs resolved
- Features delivered or significantly advanced
- Notable discoveries or learnings
- PRs created or merged

Append these highlights to the daily note under `## Notes` as:
```
**Activite Claude** ([[YYYY-MM-DD-claude|details]]) :
- highlight 1
- highlight 2
- ...
```

Replace `YYYY-MM-DD` with today's date. The wikilink points to the full Claude activity file so the user can click through for details.

The goal is a synthetic but exhaustive view of everything that happened via Claude today. Cover all projects worked on — do not cherry-pick.

### 4. Import X Bookmarks

Run an incremental import of X bookmarks to capture what was bookmarked today:
1. Invoke the `/x-import` skill (default: last 30 bookmarks)
2. This will deduplicate against existing notes and only create new ones
3. Report the count: "X nouveaux bookmarks importes" or "Aucun nouveau bookmark"

### 5. Day Summary

Use `td list --completed` and `td list`:
- List tasks completed today — parse `td list --completed` output for `✅ YYYY-MM-DD` with today's date
- List tasks still open with today's deadline — `td list` shows overdue tasks

Present: "Aujourd'hui tu as complete X taches. Y restent en retard."

### 6. Inbox Triage

List files in `Inbox/` (excluding `A trier.md`):
- If items exist, for each item:
  - Read the file content
  - Ask: "Que fait-on de ca ? (projet/tâche/note/archive/supprimer)"
  - Based on answer: move to appropriate location or convert to task via `td add`
- If empty: "Inbox vide, rien a trier."

### 7. Fact Proposals

Review the current conversation context. If any factual information about known entities (projects, people, companies) was discussed today:
- List proposed facts with target entity
- Ask: "Je propose d'ajouter ces faits. OK ?"
- If approved, append facts to the entity files using the `#status/active` inline tag format:
  ```
  - `ENTITY-NNN` Fact description #status/active
  ```
- Update `fact_count` and `last_synthesis` in entity frontmatter

### 8. Daily Log

Append a brief summary to the daily note under `## Log`:
```
- Tasks completed: X (via `td list --completed` filtered by today)
- Inbox triaged: Y items
- Facts added: Z
```

### 8b. Vault Map

Regenerate the vault map to keep it current:
1. Run the `/vault-map` skill (or execute its steps inline)
2. This updates `.claude/vault-map.md` with current entity counts, collection sizes, and recent activity
3. No user interaction needed — just regenerate silently

### 9. Wrap Up

> "Bonne soirée ! Demain, priorité : [highest priority open task or goal]"
