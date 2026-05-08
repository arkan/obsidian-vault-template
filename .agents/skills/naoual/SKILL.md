---
name: naoual
description: "Manage housekeeper visits and calculate CESU declaration + monthly bank transfer. Use this skill whenever the user mentions /naoual, housekeeping, cleaning, CESU, housekeeper hours, housekeeper visit, domestic employment declaration, or wants to log/consult monthly cleaning hours."
argument: "3h | 2026-03-17 3h | list | cesu | paid | stats | usage"
argument-hint: "3h | [date] 3h | list | cesu | paid [YYYY-MM] | stats | usage"
---

# Housekeeping — Cleaning Tracking & CESU

Skill for managing [[the housekeeper]] visits (housekeeper): logging hours, calculating monthly net salary, and preparing CESU declaration.

## Routing

| User says | Action |
|-----------|--------|
| `/naoual 3h`, `/naoual 2026-03-24 3h` | **Log** — record a visit |
| `/naoual`, `/naoual list`, `/naoual month` | **Recap** — show current month recap |
| `/naoual cesu`, `/naoual declaration` | **CESU** — calculate the monthly declaration + transfer |
| `/naoual paid`, `/naoual paid 2026-03` | **Paid** — mark a month as CESU declared + paid |
| `/naoual history`, `/naoual stats` | **Stats** — multi-month recap |
| `/naoual usage`, `/naoual help`, `/naoual ?` | **Usage** — display how to use the skill |

## Data file

All data is in `Areas/Cleaning.md`. The skill must read it before any operation and create it if it doesn't exist.

### File format

```markdown
---
type: note
tags:
  - service
  - cesu
---

# Cleaning Tracking — [[the housekeeper]]

**Hourly net rate**: 20 EUR/h

## 2026-03

| Date | Hours | Net |
|------|--------|-----|
| 2026-03-03 | 3 | 60 |
| 2026-03-10 | 3 | 60 |
| 2026-03-17 | 3 | 60 |
| Total | 9 | 180 |

> CESU declared and paid on 2026-04-01

## 2026-02

| Date | Hours | Net |
|------|--------|-----|
| ... | ... | ... |
| Total | X | Y |

> CESU declared and paid on 2026-03-05
```

Each month has its own `## YYYY-MM` section with a table. Months are ordered from most recent to oldest (current month first, right after the hourly rate).

The status line `> CESU declared and paid on YYYY-MM-DD` is added after the Total line when the month is marked as paid via `/naoual paid`. If this line is absent, the month has not yet been declared/paid.

## Actions

### Log (record a visit)

Syntax: `/naoual [date] <hours>h`

1. Parse input:
   - If no date → use today's date
   - Extract the number of hours (accept `3h`, `3`, `2.5h`, `2h30`)
   - `2h30` = 2.5 hours
2. Read `Areas/Cleaning.md`
3. Find the section for the corresponding month (YYYY-MM). If it doesn't exist, create it.
4. Check for an existing entry for this date (avoid duplicates). If duplicate, ask for confirmation.
5. Add the line to the table, sorted by date
6. Recalculate the **Total** line
7. Confirm: "Visit on DD/MM logged: Xh = Y EUR"

### Recap (display the month)

1. Read `Areas/Cleaning.md`
2. Extract the current month section (or requested month)
3. Display the table + total
4. If after the 25th of the month and the CESU declaration has not been mentioned, remind: "Remember to file the CESU declaration for this month."

### CESU (monthly declaration)

CESU (Cheque Emploi Service Universel) simplifies contributions: the employer declares hours and net salary, and CESU calculates contributions automatically.

1. Read `Areas/Cleaning.md`, extract the current month total (or requested month)
2. Calculate and display:

```
CESU Declaration — YYYY-MM
━━━━━━━━━━━━━━━━━━━━━━━━━
Visits         : N
Total hours    : X h
Hourly rate    : 20 EUR/h net

Net salary     : X * 20 = Y EUR
━━━━━━━━━━━━━━━━━━━━━━━━━
→ To declare on cesu.urssaf.fr: Y EUR net for X hours
→ Bank transfer to make: Y EUR
→ Declare here: https://www.cesu.urssaf.fr/decla/index.html
```

3. Do NOT attempt to calculate employer contributions — the CESU site does it automatically from the declared net amount. The skill focuses on the net amount to declare and the transfer to make.

### Paid (declare and pay)

Syntax: `/naoual paid [YYYY-MM]`

1. If no month specified → use the previous month (ex: if in April, take March)
2. Read `Areas/Cleaning.md`
3. Find the relevant month section
   - If section doesn't exist → error: "No visits recorded for YYYY-MM."
   - If the line `> CESU declared and paid on ...` already exists → error: "Month YYYY-MM is already declared and paid."
4. Add the status line right after the **Total** table line:
   ```
   > CESU declared and paid on YYYY-MM-DD
   ```
   (where YYYY-MM-DD = today's date)
5. Confirm: "Month YYYY-MM marked as CESU declared and paid (X EUR for Yh)."

### Stats (history)

1. Read all monthly sections from `Areas/Cleaning.md`
2. Display a summary table:

```
| Month | Visits | Hours | Net (EUR) | Status |
|------|----------|------|-----------|--------|
| 2026-03 | 4 | 12 | 240 | Paid (01/04/2026) |
| 2026-02 | 4 | 12 | 240 | Paid (05/03/2026) |
| 2026-04 | 2 | 6 | 120 | — |
| Total | 10 | 30 | 600 | |
```

The Status column shows "Paid (DD/MM/YYYY)" with the date extracted from the `> CESU declared and paid on YYYY-MM-DD` line, converted to DD/MM/YYYY format. If this line is absent, show "—".

### Usage (help)

When the user invokes `/naoual usage`, `/naoual help` or `/naoual ?`, display this help message:

```
Skill /naoual — Cleaning tracking & CESU declaration

Available commands:
  /naoual 3h                  Log a visit today (3 hours)
  /naoual 2026-03-24 3h       Log a visit on a specific date
  /naoual 2h30                Also accepts formats like 2h30 (= 2.5h)
  /naoual                     Show current month recap
  /naoual list                Same as above
  /naoual cesu                Calculate monthly CESU declaration + transfer
  /naoual paid                Mark previous month as declared and paid
  /naoual paid 2026-03        Same for a specific month
  /naoual stats               History across all months (with payment status)
  /naoual usage               Display this help
```

Do not read any file for this action — display the message directly.

## Rules

- Always read `Areas/Cleaning.md` before any operation
- The hourly rate is stored in the file (not hardcoded in the skill) so it can evolve
- If the file doesn't exist, create it with the frontmatter and current rate (20 EUR/h)
- Use `[[the housekeeper]]` as wikilink in the file
- Amounts are in EUR, rounded to the euro (no cents unless fractional hours)
- Language: English
- Terminal output: do not use bold markdown (`**`) in tables or recaps — the terminal doesn't render it. Keep text plain.
