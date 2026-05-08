# Obsidian Vault Template — AI-Native Second Brain

An opinionated [Obsidian](https://obsidian.md) vault template designed to work seamlessly with [Claude Code](https://claude.ai/code). This is not just a folder structure — it's a complete personal knowledge management system with **15 Claude Code skills** that turn your vault into an AI-powered second brain.

## Philosophy

This vault follows three core principles:

1. **PARA Organization** — Projects, Areas, Resources, Archive. Everything has a place.
2. **Entity-Based Knowledge** — People, companies, and projects are first-class citizens with structured facts and synthesis tracking.
3. **AI-Native Workflows** — Claude Code skills handle capture, review, research, and maintenance so you can focus on thinking.

## What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| Claude Code Skills | 15 | Inbox capture, task management, reviews, research, coaching, and more |
| Obsidian Templates | 9 | Daily notes, meetings, entities, articles, MOCs |
| Maps of Content | 4 | Projects, People, Companies, Resources |
| Sample Content | ~15 files | Fictional projects, people, meetings to see the system in action |

## Prerequisites

- [Obsidian](https://obsidian.md) (latest version)
- [Claude Code](https://claude.ai/code) (CLI or desktop app)
- Required Obsidian community plugins:
  - **Dataview** — powers all dashboards and MOC queries
  - **Templater** — template engine for note creation
  - **Tasks** — task management with priorities and dates
  - **Calendar** — calendar view for daily notes
  - **Obsidian Git** *(optional)* — auto-sync vault to git

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/obsidian-vault-template.git my-vault

# 2. Open in Obsidian
# File → Open Vault → Select the cloned folder

# 3. Install required plugins
# Settings → Community Plugins → Browse → Install: Dataview, Templater, Tasks, Calendar

# 4. Configure Templater
# Settings → Templater → Template folder location: "Templates"

# 5. Configure Daily Notes
# Settings → Daily Notes → Date format: YYYY/YYYY-MM/YYYY-MM-DD
# New file location: Daily Notes
# Template file: Templates/daily-note.md

# 6. Start using Claude Code skills
# Open a terminal in the vault directory and run:
claude
# Then use /inbox, /todo, /review morning, etc.
```

## Vault Structure

```
├── Home.md                      # Hub — links to all MOCs and dashboards
├── CLAUDE.md                    # Claude Code instructions for this vault
├── AGENTS.md                    # Codex agent instructions for this vault
├── .claude/skills/              # Claude Code skills
├── .claude/vault-map.md         # Auto-generated static index for agents
├── .agents/                     # Codex agent configuration and skills (mirror of .claude/)
├── Templates/                   # Obsidian templates (Templater)
├── Inbox/                       # Quick capture — sort during weekly review
├── Projects/                    # Active projects with goals & deadlines
├── Areas/
│   ├── People/                  # Person entities
│   ├── Companies/               # Company entities
│   ├── Claude/                  # Daily Claude Code activity summaries
│   │   └── operations-log.md    # Append-only operations log
│   ├── MOCs/                    # Maps of Content
│   │   ├── MOC Projects.md      # Map of Content — projects
│   │   ├── MOC People.md        # Map of Content — people
│   │   ├── MOC Companies.md     # Map of Content — companies
│   │   └── MOC Resources.md     # Map of Content — resources
│   ├── Goals.md                 # Personal & professional objectives
│   ├── TODO.md                  # Global task list (obsidian-tasks format)
│   └── TOOLS.md                 # Local infrastructure configuration
├── Clients/                     # Client relationship files
├── Meetings/                    # Meeting notes
├── Resources/                   # Reference material, articles, docs
│   ├── Articles/                # Blog articles (idea → published lifecycle)
│   ├── Research/                # Deep research reports
│   ├── GitHub-Stars/            # Synced GitHub starred repos
│   ├── X-Bookmarks/             # Synced X/Twitter bookmarks
│   └── ImportedURLs/            # Imported external URLs
├── Archive/                     # Completed/inactive items
└── Daily Notes/YYYY/YYYY-MM/    # Daily journal entries
```

## Conventions

### Frontmatter

Every note has YAML frontmatter with a `type` field:

```yaml
---
type: project    # project | person | company | note | meeting | daily | article | moc | review | claude
status: active   # active | backlog | waiting | review | done | archived | inactive
tags: []
created: 2026-01-15
---
```

### Entity Facts

Projects, people, and companies track knowledge as **facts** under `## Active Facts`:

```markdown
## Active Facts

- `entity-name-001` Description of the fact #status/active
- `entity-name-002` Another fact #status/active

## Superseded Facts

- `entity-name-000` ~~Old fact replaced by entity-name-001~~ #status/superseded
```

Facts have auto-incrementing IDs and can be superseded when information changes.

### Tasks

Tasks in `TODO.md` use [obsidian-tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) format:

```markdown
- [ ] Description #project/xxx ⏫ 📅 2026-04-01
```

Priorities: `⏫` high, `🔼` medium, `🔽` low. Completion: `✅ YYYY-MM-DD`.

### Linking

Use `[[wikilinks]]` everywhere for Obsidian graph connectivity:
- `[[Project Name]]` — link to projects
- `[[Person Name]]` — link to people
- `[[Company Name]]` — link to companies

### File Naming

| Type | Format | Example |
|------|--------|---------|
| Projects | PascalCase-With-Dashes | `SaaS-Dashboard.md` |
| People | Full Name | `Alice Martin.md` |
| Companies | PascalCase-With-Dashes | `Tech-Corp.md` |
| Daily Notes | ISO date | `2026-03-30.md` |
| Meetings | Date + Subject | `2026-03-28 Kickoff SaaS Dashboard.md` |
| MOCs | MOC + Name | `MOC Projects.md` |

## Claude Code Skills

These skills are invoked from the Claude Code CLI by typing the trigger command.

### Core Vault Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| **inbox** | `/inbox <text>` | Quick capture to `Inbox/` with auto-tagging and wikilink enrichment |
| **todo** | `/todo <action> <args>` | Manage tasks — add, list, done. Supports `!high/!medium/!low` priorities and `@Project` |
| **note** | `/note <text>` | Append to today's daily note under `## Notes` with timestamp |
| **fact** | `/fact [[Entity]] text` | Add facts to entities with auto-incremented IDs |
| **query** | `/query <question>` | Query vault data — projects, tasks, clients, daily notes |

### Review Workflows

| Skill | Trigger | Description |
|-------|---------|-------------|
| **review** | `/review morning` | Morning briefing: today's tasks, deadlines, goals, inbox status |
| | `/review evening` | Evening routine: daily note, mood/sleep, inbox triage, fact proposals |
| | `/review weekly` | Weekly: goal audit, project review, task metrics, inbox sort |
| | `/review monthly` | Monthly: retrospective, goal progress, vault health, archiving |

### Content & Research

| Skill | Trigger | Description |
|-------|---------|-------------|
| **article** | `/article` | Write blog articles through a structured lifecycle (idea → published) |
| **deep-research** | `/deep-research <topic>` | Enterprise-grade research with multi-source synthesis and citations |
| **exa** | `/exa <query>` | Web search via Exa API *(requires `EXA_API_KEY`)* |

### People & Clients

| Skill | Trigger | Description |
|-------|---------|-------------|
| **client** | `/client <action>` | Manage client relationships — follow-ups, email drafts, new clients |
| **coach** | `/coach` | Life coaching — goals, decisions, accountability, career |
| **grill-me** | `/grill-me` | Stress-test a plan/design through relentless questioning |

### Integrations

| Skill | Trigger | Description |
|-------|---------|-------------|
| **daily-claude-code-resume** | `/daily-claude-code-resume` | Generate daily Claude Code activity summary from session logs |
| **granola** | `/granola <action>` | Sync meeting notes from Granola app *(requires Granola desktop app)* |
| **cleaning** | `/cleaning <action>` | Track cleaning service hours and payments — example of a personal custom skill |

### Vault Maintenance & Tools

| Skill | Trigger | Description |
|-------|---------|-------------|
| **vault-lint** | `/vault-lint [--quick\|--fix]` | Audit vault (7 checks: drafts, wikilinks, dormant entities, tags, duplicates, empty cross-links, frontmatter) |
| **vault-map** | `/vault-map` | Regenerate static vault index at `.claude/vault-map.md` |
| **sync** | `/sync [pull\|push]` | Git pull --rebase, commit, push with conflict resolution |
| **brainstorm** | `/brainstorm <idea>` | Stress-test a raw idea: Frame → Research → Grill → Verdict (Go/No-Go/Pivot) |
| **import** | `/import <url> [#tags] [--raw]` | Import external resources with French summaries (uses summarize CLI) |
| **github-import** | `/github-import [--all\|--count N]` | Sync GitHub starred repos into Resources/GitHub-Stars/ |
| **resume** | `/resume <file\|url>` | Synthesize long documents via parallel chunked summarization |
| **tg** | `/tg [bot] <message>` | Send messages via Telegram bots |

## Workflows

### Daily Routine

```
Morning:   /review morning     → See today's tasks, deadlines, inbox
           Work on tasks       → /todo done, /fact, /note as you go
           Quick capture       → /inbox for random thoughts
Evening:   /review evening     → Log mood/sleep, triage inbox, review day
```

### Weekly Routine

```
Sunday:    /review weekly      → Audit goals, review all projects,
                                 sort inbox, plan next week
```

### Monthly Routine

```
End of month: /review monthly  → Retrospective, goal progress check,
                                  archive completed work, vault cleanup
```

### Capture Flow

```
Thought → /inbox "my thought #tag"
          ↓
        Inbox/2026-03-30-143022.md created
          ↓
        Sorted during /review evening or /review weekly
          ↓
        Becomes a task, fact, project note, or gets archived
```

## Infrastructure

### Vault Map

`.claude/vault-map.md` is the machine-readable index for agents. It is auto-generated by the `/vault-map` skill and should be regenerated after significant vault changes (new entities, new MOCs, folder restructuring). Agents use this file to discover vault contents without scanning the full directory tree.

### Operations Log

`Areas/Claude/operations-log.md` is an append-only log. Every skill that mutates vault content (creates, updates, or deletes notes) should append a line recording the operation, the date, and the affected file. This maintains a complete audit trail of all automated vault changes.

### Agents Directory

`.agents/` is the new standard directory for Codex agent configuration and skills. It mirrors `.claude/` in structure and is the canonical location for Codex-specific instructions:

- `.agents/skills/` — Codex skill files (mirror of `.claude/skills/`)
- `.agents/vault-map.md` — Codex-specific vault index (mirror of `.claude/vault-map.md`)

The `AGENTS.md` file at the vault root provides Codex-specific instructions, equivalent to `CLAUDE.md` for Claude Code. Both agents share the same vault conventions, entity model, and workflows.

## Templates

| Template | Use Case | Key Fields |
|----------|----------|------------|
| `daily-note.md` | Daily journal | mood, sleep, Tasks/Notes/Log sections |
| `entity-project.md` | New project | status, area, Active Facts/Superseded Facts |
| `entity-person.md` | New person | status, Active Facts/Superseded Facts |
| `entity-company.md` | New company | status, Active Facts/Superseded Facts |
| `meeting.md` | Meeting notes | participants, project, Decisions/Actions/Notes |
| `note.md` | Generic note | tags |
| `article.md` | Blog article | title, slug, lang, status lifecycle |
| `weekly-review.md` | Weekly review | structured checklist |
| `moc.md` | Map of Content | Dataview query placeholder |

## Customization

### Make It Yours

1. **Delete sample content** — Remove everything in `Projects/`, `Areas/People/`, `Areas/Companies/`, `Clients/`, `Meetings/`, `Inbox/`, `Archive/`, `Daily Notes/`, and `Resources/Articles/`
2. **Update Goals.md** — Replace fictional goals with your own
3. **Update TODO.md** — Clear sample tasks
4. **Keep the structure** — The skills depend on the folder structure and conventions

### Create Your Own Skills

Skills live in `.claude/skills/<name>/SKILL.md`. See the `cleaning` skill for a simple example of a custom personal skill. The format is:

```
.claude/skills/my-skill/SKILL.md
```

Each skill file contains instructions for Claude Code on how to handle the trigger command.

### Adapt the Language

The vault content is in **English** by default. To use another language:
1. Update `CLAUDE.md` — change the content language instruction
2. Update template section headers (`## Tasks` → `## Tâches`, etc.)
3. Update skill files — translate instructions to your language
4. MOC and Home.md section headers

## License

MIT — See [LICENSE](LICENSE) for details.

---

Built with [Obsidian](https://obsidian.md) and [Claude Code](https://claude.ai/code).
