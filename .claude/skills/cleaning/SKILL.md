---
name: cleaning
description: "Track cleaning service sessions, hours, and payments. USE WHEN user says /cleaning to log a session, get a monthly recap, or view stats. Example of a personal custom skill."
user_invocable: true
argument: "log <date> <hours> [tasks] | recap [YYYY-MM] | stats"
---

# Cleaning Service Tracker

> **Note:** This is an example of a personal custom skill. Adapt it to your own context (name, rate, frequency, etc.).

Track cleaning service visits: hours, tasks performed, and payments.

## Trigger

`/cleaning <action> <args>`

## Data Storage

All data is stored in `Areas/Cleaning.md`.

### File Format

```markdown
---
type: infrastructure
tags: [cleaning, home]
rate_per_hour: 20
currency: EUR
payment_method: cash
---

# Cleaning

## Sessions

| Date | Hours | Amount | Tasks |
|------|-------|--------|-------|
| 2026-03-15 | 3 | 60€ | Vacuuming, mopping, bathroom |
| 2026-03-22 | 2.5 | 50€ | Kitchen, windows, dusting |

## Monthly Recaps

### 2026-03

- **Total hours**: 5.5h
- **Total due**: 110€
- **Paid**: yes
- **Sessions**: 2
```

## Actions

### Log

`/cleaning log 2026-03-15 3 Vacuuming, mopping, bathroom`

1. Read `Areas/Cleaning.md` (create the file if it doesn't exist, using the template above)
2. Parse arguments:
   - `date` (YYYY-MM-DD) — required
   - `hours` (number, decimals accepted) — required
   - `tasks` (free text after hours) — optional
3. Calculate amount: `hours * rate_per_hour` (read rate from frontmatter, default 20€/h)
4. Add a row to the `## Sessions` table
5. Confirm: "Session on YYYY-MM-DD logged: Xh, XX€"

### Recap

`/cleaning recap` (current month) or `/cleaning recap 2026-03`

1. Read `Areas/Cleaning.md`
2. Filter sessions for the requested month
3. Calculate:
   - Total hours
   - Total amount due
   - Number of sessions
4. Display the recap and offer to add it under `## Monthly Recaps` if it doesn't already exist

### Stats

`/cleaning stats`

1. Read `Areas/Cleaning.md`
2. Calculate global statistics:
   - Total hours since start
   - Total paid since start
   - Average hours per month
   - Average hours per session
   - Average frequency (days between sessions)
3. Present as a table

## Rules

- ALWAYS read `Areas/Cleaning.md` before any operation
- Create the file with the template if missing
- Hourly rate is read from frontmatter (`rate_per_hour`), not hardcoded
- Amounts are in euros, rounded to the nearest unit
- Dates must be in YYYY-MM-DD format
- Do not duplicate a session already logged (check by date)

## Examples

Input: `/cleaning log 2026-03-29 3 Vacuuming, mopping, bathroom`
→ Adds: `| 2026-03-29 | 3 | 60€ | Vacuuming, mopping, bathroom |`
→ Confirms: "Session on 2026-03-29 logged: 3h, 60€"

Input: `/cleaning recap`
→ Displays the current month's recap

Input: `/cleaning recap 2026-02`
→ Displays the February 2026 recap

Input: `/cleaning stats`
→ Displays global statistics
