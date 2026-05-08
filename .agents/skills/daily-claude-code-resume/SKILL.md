---
name: daily-codex-resume
description: >
  Generate a daily summary of all Codex activity by parsing session JSONL logs
  and writing an Obsidian-compatible markdown note into the vault. Use this skill whenever
  the user asks to summarize Codex activity, generate a daily Codex report, or when
  triggered by a scheduled cron. Also triggers for: "resume codex", "activite du jour",
  "what did Codex do today", "journal codex", "daily recap".
---

# Daily Codex Resume

Parse all Codex session logs from the last 24 hours and produce a single Obsidian note summarizing the work done across all projects.

## Data Source

Session logs live under `~/.claude/projects/`. Each project directory contains:
- `sessions-index.json` — metadata index with `sessionId`, `firstPrompt`, `messageCount`, `created`, `modified`, `gitBranch`, `projectPath`
- `<session-id>.jsonl` — full conversation logs (one JSON object per line)

### How to find today's sessions

1. List all project directories under `~/.claude/projects/`
2. For each project, read `sessions-index.json` and filter entries where `modified` falls within the last 24 hours
3. For qualifying sessions, read the corresponding `.jsonl` file to extract conversation content

### JSONL message format

Each line is a JSON object. The key fields are:
- `type`: `"user"` or `"assistant"` (ignore `"queue-operation"`)
- `message.role`: `"user"` or `"assistant"`
- `message.content`: array of content blocks or a string
  - Text blocks: `{"type": "text", "text": "..."}`
  - Tool use blocks: `{"type": "tool_use", "name": "ToolName", "input": {...}}`
  - Thinking blocks: `{"type": "thinking", "thinking": "..."}` — skip these, they are internal reasoning
- `cwd`: working directory at that point
- `gitBranch`: current git branch
- `sessionId`: session identifier
- `timestamp`: ISO 8601 timestamp

### What to extract from each session

- **Project context**: derive from `projectPath` in the index or `cwd` in messages
- **Branch**: from `gitBranch`
- **User prompts**: the `text` content from `type: "user"` messages — these describe intent
- **Assistant actions**: the `text` content and `tool_use` blocks from `type: "assistant"` messages
  - `tool_use` with `name: "Write"` or `name: "Edit"` → files modified
  - `tool_use` with `name: "Bash"` → commands run (look at `input.command`)
    - **GitHub URLs**: extract any `https://github.com/...` URLs from Bash outputs — these are PR and issue URLs created or referenced during the session (look for `gh pr create`, `gh issue create`, or URLs printed by git push)
  - `tool_use` with `name: "Read"` or `name: "Grep"` or `name: "Glob"` → files explored
- **GitHub URLs in text**: also scan assistant text messages for GitHub issue/PR URLs (`https://github.com/.../pull/N` or `https://github.com/.../issues/N`)
- **First prompt**: `firstPrompt` from the index gives a quick summary of intent

### Relevance filter

Not all sessions deserve mention. Use your judgment:
- Sessions with only 1-2 messages or trivial actions (a single `/commit`, a quick file read with no follow-up) can be omitted
- Group related sessions on the same project/branch together
- Focus on sessions where meaningful work happened: code written, bugs fixed, features implemented, plans created, research done

## Wikilink Detection

Before writing the output, scan the vault to build a list of known entities and their aliases.

### Directories to scan
- `Areas/People/*.md` — person entities
- `Areas/Companies/*.md` — company entities
- `Projects/*.md` — project entities

### How to build the entity map

For each `.md` file in those directories:
1. The filename (without `.md`) is the primary name
2. Read the first 20 lines and extract `aliases:` from YAML frontmatter
3. Filter out generic tags (like `people`, `work`, `family`, `company`, `project`, `tech`, `service`) — keep only name-like aliases

This gives you a map like:
```
"Bob Dupont" → ["Bob Dupont", "Bob"]
"Tech-Corp" → ["TC", "Tech Corp"]
```

### Applying wikilinks

When writing the summary text, replace mentions of known entity names or aliases with `[[Entity-Name]]` wikilinks. Match case-insensitively but use the canonical filename in the link. For aliases, use the pipe syntax: `[[Bob Dupont|Bob]]`.

**Critical rules:**
- Only link an entity when the text genuinely refers to that entity. A project directory name like `my-saas-app` is NOT the same as a vault entity `[[SaaS-Dashboard]]` — do not conflate them. Each project is its own distinct entity.
- Use short Obsidian links (`[[MOC Projects]]`), never path-based links (`[[Areas/MOC Projects|MOC Projects]]`). Obsidian resolves filenames globally.
- Do this naturally inline — not as a separate list. The `## Connections` section at the end collects all unique wikilinks used.

### Auto-creation of missing project pages

If a project mentioned in the summary does not have a corresponding page in `Projects/`, create one automatically. Use the entity-project template format:

```markdown
---
type: project
aliases: []
tags:
  - project
status: active
area:
created: YYYY-MM-DD
last_synthesis: YYYY-MM-DD
fact_count: 0
---
# Project-Name

## Active Facts

## Superseded Facts

_None yet._
```

- File name: `Projects/Project-Name.md` (PascalCase with hyphens)
- Populate `aliases` with common short names (e.g., for `SaaS-Dashboard` add `["saas-dashboard", "saas"]`)
- Set `created` to today's date
- Then use `[[Project-Name]]` as a wikilink in the summary

## Output

### Location

Write to: `Areas/Codex/YYYY-MM-DD-codex.md`

Use today's date. If the directory `Areas/Codex/` does not exist, create it.

If the file already exists for today, read its current content first. Merge new sessions into the existing file: append new project sections, update statistics, and preserve any manual edits. Do not overwrite blindly.

### Template

```markdown
---
title: "Codex Summary - YYYY-MM-DD"
date: YYYY-MM-DD
source: codex
type: daily/codex
tags:
  - codex
  - summary
status: done
---

## Summary

Overview of Codex activity for the day (2-4 sentences). Mention the main projects, the overall work theme, and notable accomplishments. Use [[wikilinks]] for known entities.

## Activity by Project

### Project Name 1

**Branch(es)**: `branch-name`
**Sessions**: N session(s), ~M messages

Description of work done on this project. What was the goal, what was accomplished, what tools/files were involved. Use [[wikilinks]] naturally.

Key changes:
- Concise description of an important change
- Concise description of another change

GitHub links:
- [#189 — CRUD rejection patterns](https://github.com/org/repo/pull/42)
- [Issue #194 — Feedback widget](https://github.com/org/repo/issues/194)

### Project Name 2

(same structure)

## Statistics

- **Active projects**: N
- **Total sessions**: N
- **Messages exchanged**: ~N

## Connections

[[Entity1]] | [[Entity2]] | [[Entity3]]
```

### Content language

All note content, section headers, and descriptions must be in **English**. Technical terms (file paths, branch names, tool names) stay in English.

## Execution Notes

This skill is designed to run as a scheduled task (via `/schedule`). It should:
1. Scan all project directories — do not skip any
2. Parse JSONL files for sessions modified in the last 24 hours
3. Build the entity map from the vault
4. Generate the summary with wikilinks
5. Write the file

The JSONL files can be large. For efficiency:
- Use the `sessions-index.json` to pre-filter sessions by date before reading any JSONL
- For very large JSONL files (>10000 lines), focus on the user messages and tool_use blocks, skip thinking blocks entirely
- Derive project names from the directory name: strip the leading `-` and convert `-` path separators back to `/` (e.g., `-Users-john-Code-Acme-web-app` → `Acme/web-app`)
