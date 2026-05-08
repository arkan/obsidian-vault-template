---
name: sante
description: Document, track and search everything related to the user's health — symptoms, measurements (weight, sleep, blood pressure), illnesses, medications, consultations, lab results. USE WHEN user mentions any health-related topic conversationally (e.g. "my back hurts", "78kg this morning", "I slept 5h", "cardio appointment", "blood test results", "when did I have that migraine"), even without explicit slash command. Also triggered via `/sante`. Do NOT trigger for purely professional fatigue, metaphors ("project health"), pure sports, or daily food intake without symptoms.
user_invocable: true
argument: "(optional) free-form health information"
---

# Health Skill

Entry point for all health data in the vault. Health.md is the dashboard, but 99% of the time the skill triggers in conversation and routes the info to the right file.

## Philosophy

The user talks about health in natural language. The skill's role is not to impose a syntax — it's to **cleanly route** a phrase to the right persistent form, asking 1-2 clarification questions when ambiguous, then showing what will be saved before writing.

**Three distinct lifecycles**, do not mix them:

| Category | Why distinct | Where it lives |
|---|---|---|
| **Measurement** (number over time) | Looks for trends | `Daily Notes/...` (frontmatter) or `Areas/Health/Measurements/YYYY-MM.md` |
| **Entity** (exists beyond an event) | Looks for current state | `Areas/Health/Conditions/` or `/Medications/` |
| **Event** (dated, finished) | Looks for "when" | `Areas/Health/Events/YYYY-MM-DD-<title>.md` |

If you hesitate between two categories, **ask**. Better a question than misclassification.

## Routing — how to decide

Read the user's phrase and apply this tree:

1. **Is it a daily number (weight, sleep, mood, blood pressure)?**
   → Measurement. If the measurement exists in the frontmatter of today's daily note, write it there. Otherwise, add to the monthly log `Areas/Health/Measurements/YYYY-MM.md`.

2. **Is it a consultation, lab test, exam, or one-off crisis?**
   → Event. Create `Areas/Health/Events/YYYY-MM-DD-<short-title>.md`.

3. **Is it a symptom?**
   - First episode or one-off: event (`category: symptom`).
   - Recurring / already discussed several times: escalate to condition. Ask: *"This back pain keeps coming back, should I promote it to a chronic condition?"*

4. **Is it a chronic illness, allergy, long-term history?**
   → Entity `health-condition` in `Areas/Health/Conditions/`.

5. **Is it a medication / treatment?**
   → Entity `health-medication` in `Areas/Health/Medications/`. A single dose = monthly log. A regular treatment = entity with `started`/`stopped`.

6. **Is it a search ("when did I have X", "trend of Y")?**
   → No writing. See the `## Search` section below.

## Conversational Workflow (standard case)

The user says something. You do:

1. **Identify** the category via the tree above.
2. **Ask 0-2 questions** only if critical info is missing (date, intensity, link to an existing condition). Examples:
   - "My back hurts" → *"Since when? And is it linked to your herniated disc or new?"*
   - "78kg" → write directly, it's unambiguous.
   - "Blood test results" → *"Which markers? And which lab / what day?"*
3. **Show the diff** (file path + content to add) before writing.
4. **Write** after implicit confirmation (continue conversation) or explicit.
5. **Confirm**: path created/modified + 1 summary line.

Stay sober. Never invent an intensity, date, or dosage that the user didn't provide.

## Templates

Templates bundled in `.agents/skills/sante/templates/`. Read the right template when writing — don't reinvent it.

- `templates/condition.md` — for `type: health-condition`
- `templates/medication.md` — for `type: health-medication`
- `templates/event.md` — for `type: health-event`

### Measurement format in daily notes

Frontmatter fields to add (create if missing, otherwise update):
```yaml
weight: 78.2          # kg, decimal point
sleep: 5              # hours
mood: 3               # already handled by /review evening
```

If today's daily note doesn't exist, create it first with the `Templates/daily-note.md` template.

### Measurement format in the monthly log

File `Areas/Health/Measurements/YYYY-MM.md`. Create it if it doesn't exist with frontmatter:
```yaml
---
type: health-measurement-log
month: YYYY-MM
---
```

Append a line under a dated section (create the section if missing):
```markdown
## YYYY-MM-DD
- HH:MM blood_pressure: 13/8
- HH:MM medication_taken: [[Tylenol]] 1000mg
- HH:MM symptom: headache (intensity 6/10)
```

Keep the format simple and grep-friendly. One line = one measurement event.

## File Naming

- **Conditions**: `Herniated-Disc.md`, `Pollen-Allergy.md` (PascalCase with dashes)
- **Medications**: `Tylenol.md`, `Levothyrox-50.md` (main brand name)
- **Events**: `2026-04-25-Cardio-Consultation-Smith.md` (date + short nature)
- **Measurements**: `2026-04.md`

## Health.md — entry point

`Areas/Health/Health.md` is the master dashboard. It's a `type: health-dashboard` file that aggregates via dataview. Don't write raw data there — just **stable macro facts** (blood type, critical allergies) at the top, then dataview blocks that scan the hierarchy files.

If Health.md is missing or broken, restore it from the reference block at the bottom of this skill.

## Search

The user may ask:
- *"When was the last time I had this migraine?"* → grep `migraine` in `Areas/Health/Events/` and `Measurements/`, sort by date desc, show the 3 most recent.
- *"My weight trend over 3 months"* → grep `weight:` in `Daily Notes/2026/` (last 3 months), build a mini text timeline. If many points, suggest a dataview visualization to paste into Health.md.
- *"What did the cardiologist tell me last time?"* → list events with `category: consultation` and `provider` cardio, take the most recent, read it.
- *"Monthly health recap"* → grep all `Areas/Health/Events/2026-04-*.md` + `Measurements/2026-04.md` + frontmatter of the month's daily notes.

Always respond factually, without medical interpretation (you are not a doctor).

## Links (wikilinks)

Maximize `[[...]]`:
- A consultation event cites the doctor: `provider: "[[Dr Smith]]"` (create the person file in `Areas/People/` if missing)
- An event linked to a condition: `related: ["[[Herniated-Disc]]"]`
- A medication dose cites the medication: `[[Tylenol]] 1000mg`
- A condition can cite its ongoing treatments in `## Active Facts`

## Rules

- Content **in English** (consistent with the vault)
- Frontmatter **always valid YAML** — quote values with `:` or special characters
- **Never** duplicate a measurement (if it's in daily frontmatter, don't also put it in the monthly log)
- **Never** give medical advice. You archive, you don't diagnose.
- Before writing, **always** show the diff (path + content) to the user
- Prefer **updating** an existing entity rather than creating a new one (search by name and alias before creating)
- For conditions/medications, follow the `## Active Facts` / `## Superseded Facts` vault pattern (cf skill `/fact`)

### Verify before assuming an entity

**Never** write a wikilink `[[Some-Thing]]` without verifying that the target exists — otherwise you create broken links or invent an entity.

Before writing `related: ["[[Herniated-Disc]]"]`, `provider: "[[Dr Smith]]"`, `treats: [[Migraines]]`, etc.:
1. List the relevant directory (`Areas/Health/Conditions/`, `Areas/People/`, `Areas/Health/Medications/`).
2. If the entity exists → use the wikilink.
3. If it doesn't exist → **ask**: *"I can't find [[Herniated-Disc]] in the vault. Do you want me to create the file, or leave it without a link?"*

This rule prevents writing assumptions that will pollute the graph later.

### Smart-default for clarification questions

When the user makes an ambiguous reference ("my pill", "this medication", "the treatment"), before asking **which one**:

1. List active candidate entities (ex: `Areas/Health/Medications/*.md` with `status: active`).
2. **If one candidate** → use it without asking, but state your inference: *"I assume you mean [[Tylenol]] (only active treatment). OK?"*
3. **If zero candidates** → ask explicitly and offer to create the file along the way.
4. **If multiple candidates** → list them and ask to choose.

Same for "the cardiologist", "my GP", "my physio" → search `Areas/People/` before asking.

## Post-action — Log

After each write, append a line to `Areas/Codex/operations-log.md`:
```
| YYYY-MM-DD HH:MM | <create|update> | sante | <short summary> | <file-path> |
```

## Reference Health.md

If `Areas/Health/Health.md` is absent, create it with this content:

```markdown
---
type: health-dashboard
title: Health
created: YYYY-MM-DD
---

# Health

Entry point for all vault health data. Raw data in `Conditions/`, `Medications/`, `Events/`, `Measurements/`.

## Macro Facts

<!-- Fill in manually: blood type, critical allergies, key family history -->

- Blood type:
- Critical allergies:
- Primary care physician:

## Active Conditions

```dataview
TABLE status, severity, last_synthesis as "Last Update"
FROM "Areas/Health/Conditions"
WHERE type = "health-condition" AND status = "active"
SORT severity DESC, last_synthesis DESC
```

## Current Medications

```dataview
TABLE dosage, frequency, started, prescribed_by as "Prescribed by"
FROM "Areas/Health/Medications"
WHERE type = "health-medication" AND status = "active"
SORT started DESC
```

## Recent Measurements (last 7 days)

```dataview
TABLE weight, sleep, mood
FROM "Daily Notes"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

## Recent Events (last 30 days)

```dataview
TABLE category, provider, related
FROM "Areas/Health/Events"
WHERE type = "health-event" AND date >= date(today) - dur(30 days)
SORT date DESC
```

## Upcoming Appointments

```dataview
TABLE date, provider, related
FROM "Areas/Health/Events"
WHERE type = "health-event" AND category = "appointment" AND date >= date(today)
SORT date ASC
```
```

## Examples

**Input**: "I slept 5h last night, it was awful"
→ You: *"Noting `sleep: 5` in the daily note for 2026-04-25. OK?"*
→ Write in `Daily Notes/2026/2026-04/2026-04-25.md` frontmatter.

**Input**: "my back has been hurting since yesterday"
→ You: *"Linked to your herniated disc (existing entity) or new? And approx intensity?"*
→ Depending on answer: add a fact to `Areas/Health/Conditions/Herniated-Disc.md` OR create `Areas/Health/Events/2026-04-24-Back-Pain.md`.

**Input**: "78.2kg this morning"
→ No question. Write `weight: 78.2` in today's daily note, confirm.

**Input**: "blood test results: cholesterol 2.4, ferritin 45"
→ You: *"Date of blood draw and lab?"*
→ Create `Areas/Health/Events/YYYY-MM-DD-Blood-Test.md` with `category: analysis`, body listing the markers.

**Input**: "when was the last time I had this migraine?"
→ No writing. Grep `migraine` in `Areas/Health/`, return sorted dates, read the 1-2 most recent for context.
