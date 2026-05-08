---
name: banking
description: >
  Interact with personal bank accounts via Enable Banking CLI to check balances,
  browse transactions, analyze spending, forecast cash flow, and manage alerts.
  Use this skill whenever the user mentions money, bank accounts, balances, transactions,
  spending, budgets, forecasts, cash flow, or anything related to personal finances.
  Also trigger when the user asks questions like "how much did I spend", "what is my balance",
  "my latest transactions", "cash flow forecast", or any financial query.
  Proactively use this skill even if the user doesn't explicitly say "banking" — any mention
  of expenses, income, categories like "groceries", "rent", "transport", or account aliases
  should trigger it.
---

# Banking — Enable Banking CLI Skill

This skill gives you access to the user's bank accounts through the Enable Banking CLI.
The user has 3 bank accounts configured, each identified by an alias: **primary**, **secondary**, **savings**.

## No-Argument Usage

When the skill is invoked without arguments (just `/banking` with no text after it),
display this usage summary and stop — do not run any command:

```
🏦 Banking — Available Commands

  /banking balance                 Balances for all accounts
  /banking balance <account>       Balance for one account (primary, secondary, savings)
  /banking transactions            50 latest transactions (all accounts)
  /banking transactions <account>  Transactions for one account
  /banking summary                 Full dashboard with categories and top spending
  /banking categories              Spending breakdown by category
  /banking uncategorized           Transactions without a category to sort
  /banking forecast                Cash flow forecast
  /banking alerts                  Check active alerts
  /banking alerts list             List alert rules
  /banking report                  Generate an interactive HTML report
  /banking delta <period>          Monthly change (ex: delta 3m, delta 6m)
  /banking refresh                 Refresh data from the API

  Examples:
    /banking balance primary
    /banking transactions secondary --from 2026-03-01
    /banking how much did I spend on groceries this month
    /banking summary savings
```

Any natural language query about finances also works (ex: "how much is in my account",
"my latest expenses", "forecast March").

## CLI Binary

```
~/Code/enable-banking-cli/enable-banking
```

Always use `--json` for machine-readable output.

## Commands

### `accounts` — Accounts & Balances

The primary command for viewing accounts and their balances. Balances are included
directly in the accounts output — there is no need to call `balances` separately.

```bash
~/Code/enable-banking-cli/enable-banking accounts --json
```

Flags:
- `--bank` — filter by bank alias
- `--refresh` — full refresh from API (fetches accounts, balances, AND transactions)

JSON output structure:
```json
{
  "data": [
    {
      "bank": "BNP Paribas",
      "uid": "...",
      "iban": "FR76...",
      "name": "Checking Account ****2214",
      "currency": "EUR",
      "alias": "primary",
      "balances": {
        "CLBD": "115080.80",
        "OTHR": "112318.09"
      }
    }
  ],
  "last_synced": "2026-03-28T16:51:12Z",
  "totals": [
    { "currency": "EUR", "totals": { "CLBD": "136962.79", "OTHR": "114013.90" } }
  ]
}
```

Balance types: CLBD (Closing Booked), OTHR (Other/Current), XPCD (Expected).
Totals are pre-computed per currency — use them directly, no need to sum manually.

### `transactions` — Transaction History

```bash
~/Code/enable-banking-cli/enable-banking transactions --json
```

Default limit: 50 transactions. Flags:
- `--account` — filter by IBAN, UID, or alias
- `--bank` — filter by bank
- `--from`, `--to` — date range (YYYY-MM-DD)
- `--limit` — max results (default 50)
- `--category` — filter by spending category
- `--direction` — `credit` or `debit`
- `--refresh` — fetch latest from API

JSON output — fields are **PascalCase**:
```json
{
  "data": [
    {
      "AccountUID": "...",
      "TransactionID": "000025137010188900",
      "Amount": "29.50",
      "Currency": "EUR",
      "BookingDate": "2026-04-01",
      "CreditDebitIndicator": "CRDT",
      "RemittanceInfo": ["VIR SEPA RECU /DE ..."],
      "CreditorName": "",
      "DebtorName": "",
      "Status": "BOOK",
      "Category": "Home",
      "CategorySource": "auto"
    }
  ],
  "last_synced": "...",
  "count": 42,
  "credits": "3200.00",
  "debits": "1850.50",
  "total": "1349.50"
}
```

### Monthly Delta Analysis

To compute monthly net change per account, fetch transactions with a large limit
and group by `BookingDate[:7]` (YYYY-MM). For each account:

```bash
~/Code/enable-banking-cli/enable-banking transactions --json --account <alias> --from <start> --to <end> --limit 1000
```

Then aggregate per month using `Amount` and `CreditDebitIndicator` (CRDT/DBIT).
Run all 3 accounts in parallel for speed. Present per-account tables then a global total.

### `forecast` — Cash Flow Projection

```bash
~/Code/enable-banking-cli/enable-banking forecast --json --all --detail
```

Flags: `--bank`, `--account`, `--all` (multi-bank), `--detail` (pending txns), `--refresh`.

### `summary` — Spending Analysis

```bash
~/Code/enable-banking-cli/enable-banking summary --json --period month --compare
```

Flags: `--period` (day/week/month), `--compare` (vs prior period), `--from`, `--to`, `--bank`.

### `alerts` — Alert Management

```bash
# Check alerts
~/Code/enable-banking-cli/enable-banking alerts check --json --refresh

# List rules
~/Code/enable-banking-cli/enable-banking alerts list --json

# Add rules
~/Code/enable-banking-cli/enable-banking alerts add --type transaction --amount 500 --direction DBIT --name "large-debit"
~/Code/enable-banking-cli/enable-banking alerts add --type category --category groceries --threshold 600 --period month

# Remove rule
~/Code/enable-banking-cli/enable-banking alerts remove "large-debit"
```

Exit codes for `alerts check`: 0 = no alerts, 1 = triggered, 2 = session expired.

### `tag` — Transaction Categorization

```bash
~/Code/enable-banking-cli/enable-banking tag apply       # Auto-apply configured rules
~/Code/enable-banking-cli/enable-banking tag preview     # Dry-run
~/Code/enable-banking-cli/enable-banking tag override --id <txn-id> --category <cat>
```

Do NOT use `tag interactive` — it's a TUI requiring user input.

### Uncategorized Transactions Report

When asked to list uncategorized transactions, first fetch categorized transactions
from all accounts to learn which categories exist and what merchants map to them.
Then fetch uncategorized transactions and present them with a suggested category.

**Step 1 — Learn existing categories**: fetch all transactions (all accounts, `--limit 1000`)
and build a mapping of merchant keywords → category. For instance, if "UBER * EATS" appears
tagged as "Food" in categorized transactions, then an uncategorized "UBER * EATS" should
suggest "Food". Also use common sense for obvious merchants (gas station → Car,
bakery → Food, restaurant → Entertainment, pharmacy → Health, etc.).

**Step 2 — Fetch uncategorized**: use `--category uncategorized --limit 1000` per account,
all 3 in parallel.

**Step 3 — Present** as a table per account with a `#` column for easy reference:

| # | Date | Amount | Dir. | Merchant | Description | Suggestion |
|---|------|-------:|------|----------|-------------|------------|

- **#**: Sequential number continuous across ALL account tables (1, 2, 3... never restarting).
  If primary has 5 transactions (1-5), secondary starts at 6. This ensures every transaction has
  a unique number so the user can reference them unambiguously when accepting/rejecting.
- **Date**: DD/MM/YYYY from `BookingDate`
- **Amount**: Local format (ex: `29.50 €`)
- **Dir.**: `credit` or `debit` from `CreditDebitIndicator`
- **Merchant**: Merchant name cleaned from `RemittanceInfo` (strip SEPA jargon)
- **Description**: Best guess at what this transaction is, in plain English
  (ex: "Esso gas station fuel", "Amazon purchase", "Bakery")
- **Suggestion**: The proposed category based on existing categories and merchant analysis.
  Use `?` suffix when uncertain (ex: `Food?`, `Entertainment?`). Leave empty if truly ambiguous.

Sort by date (most recent first) within each table. Skip accounts with no uncategorized
transactions. Use `--limit 1000` to capture everything.

**Step 4 — Summary and next actions**: after all tables, show:
1. Grand total (number of transactions, total debit amount)
2. A recap of suggestions grouped by category with count
3. List ALL available categories from `~/.enable-banking/config.yaml` `tag_rules` keys,
   so the user knows exactly what categories exist. Display them as a compact line, e.g.:
   ```
   📂 Available categories: Health, Home, Income, Transport, Services, Food, Car, Entertainment, Pets, Clothing, Misc, Pets
   ```
   Read the config dynamically — do not hardcode this list, as the user may add categories.
4. Ask the user what to do, with examples:
   - "ok" or "apply all" → apply all suggestions
   - "apply except 3, 7, 12" → apply all except those numbers
   - "apply 1-5, 8" → apply only those numbers
   - "3 → Food, 7 → Entertainment" → override specific suggestions
   - The user can mix these (ex: "apply all except 3, and 3 → Home")

**Step 5 — Validate and Apply**: when the user responds:

1. **Validate categories first**: before running any override, check that every category
   the user provided (including suggestions about to be applied) exists in the config's
   `tag_rules` keys. If any category is unknown, display an error and abort the entire
   operation — do NOT apply partial results:
   ```
   ❌ Unknown category: "Leisure"
   📂 Available categories: Health, Home, Income, Transport, Services, Food, Car, Entertainment, Pets, Clothing, Misc, Pets
   No changes applied. Correct and try again.
   ```
   Category matching is case-sensitive — use exact names from the config.

2. **Apply**: once all categories are validated, run `tag override` for each transaction:
   ```bash
   ~/Code/enable-banking-cli/enable-banking tag override --id <TransactionID> --category <category>
   ```
   Run overrides in parallel (batch of ~5 at a time) for speed. Report results when done.

Keep the TransactionID internally (don't clutter the table with it) — use it only when
running the `tag override` commands.

### Full Account Summary

When the user asks for a summary, overview, or "summary" of their transactions across all
accounts, build a rich terminal-friendly dashboard. Fetch ALL transactions from each account
in parallel (`--limit 1000`), then aggregate and present.

**Data collection** — run all 3 in parallel:
```bash
~/Code/enable-banking-cli/enable-banking transactions --json --account primary --limit 1000
~/Code/enable-banking-cli/enable-banking transactions --json --account secondary --limit 1000
~/Code/enable-banking-cli/enable-banking transactions --json --account savings --limit 1000
```

**Presentation** — for each account, output a section with:

1. **Header** with account alias, period covered (earliest → latest BookingDate), and
   totals (credits / debits / net)

2. **Category breakdown** — a table sorted by total debit descending:

```
## 💳 primary — 14 Jan → 7 Apr 2026

Credits: 23,235.03 €  |  Debits: 18,412.50 €  |  Net: +4,822.53 €

| Category       |   Nb |    Debits |   Credits |       Net |  %spend | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ |
|----------------|-----:|----------:|----------:|----------:|------:|----------------------|
| Home           |   12 | 2,850.00  |    29.50  | -2,820.50 | 15.5% | ████████               |
| Food           |   18 | 1,245.30  |           | -1,245.30 |  6.8% | ████                   |
| Services       |    8 |   487.20  |           |   -487.20 |  2.6% | ██                     |
| Income         |    5 |           | 8,200.00  | +8,200.00 |       |                        |
| uncategorized  |    6 |   293.77  |    59.03  |   -234.74 |  1.6% | █                      |
| ...            |      |           |           |           |       |                        |
```

3. **Bar chart** — the `▓` column uses Unicode block characters (`█`) to represent the
   proportion of total debits. Scale the longest bar to 20 chars, others proportionally.
   Only show bars for categories with debits. This gives a quick visual ranking of spending.

4. **Top 5 transactions** — the 5 largest debits across the account, as a mini-table:

```
| # | Date       | Amount     | Category  | Merchant                 |
|---|------------|------------|-----------|--------------------------|
| 1 | 01/03/2026 | 1,200.00 € | Home      | March rent               |
| 2 | 15/02/2026 |   890.00 € | Car       | Car insurance            |
```

**After all accounts**, show a **Global summary** table:

```
## 📊 Global Summary

| Account    |   Credits |    Debits |       Net | Nb tx |
|------------|----------:|----------:|----------:|------:|
| primary    | 23,235.03 | 18,412.50 | +4,822.53 |    96 |
| secondary  | 13,938.16 | 12,105.40 | +1,832.76 |   155 |
| savings    |  9,750.00 |  5,501.14 | +4,248.86 |     8 |
| **Total**  | **46,923.19** | **36,019.04** | **+10,904.15** | **259** |
```

Then a **Global breakdown** combining all accounts — same category table format as above
but merging data from all 3 accounts. This gives a single unified view of where money goes.

Keep amounts in local format (`1,234.56 €`), clean up RemittanceInfo for the top 5,
and sort categories by total debits descending. Categories with only credits (like Income)
go at the bottom of the table.

## HTML Report

When the user asks for a report, dashboard, or visual overview, generate a standalone
HTML dashboard. The script is at `scripts/generate_report.py` relative to this skill.

Workflow — run these commands:
```bash
# 1. Fetch data (accounts in one call, transactions per account in parallel)
~/Code/enable-banking-cli/enable-banking accounts --json > /tmp/banking-accounts.json
~/Code/enable-banking-cli/enable-banking transactions --json --account primary --limit 0 > /tmp/banking-txns-primary.json
~/Code/enable-banking-cli/enable-banking transactions --json --account secondary --limit 0 > /tmp/banking-txns-secondary.json
~/Code/enable-banking-cli/enable-banking transactions --json --account savings --limit 0 > /tmp/banking-txns-savings.json

# 2. Generate report
python3 <skill-base-dir>/scripts/generate_report.py

# 3. Open in browser
open /tmp/banking-report-$(date +%Y-%m-%d).html
```

The report features:
- Tabs per account + global view
- Balances, category breakdown, monthly evolution
- Drill-down: Month → Categories → Individual transactions
- Filters (category, direction, text search) on the transaction list
- Light mode, clean style

## Response Guidelines

- **Language**: Always respond in English.
- **Currency**: Local format (ex: `1,234.56 €`).
- **Accounts**: Never display full IBANs. Always use the account alias (primary, secondary, savings).
  If alias is unavailable, show only the last 4 digits (ex: `•••• 0123`).
- **Tables**: Markdown tables for chat output.
- **Obsidian reports**: Markdown with frontmatter (`type: note`, tags `#finance`, `#banking`).
  Save to `Inbox/` unless specified otherwise.
- **Dates**: English format in output (ex: `7 April 2026`), YYYY-MM-DD for CLI flags.
- **Amounts**: 2 decimal places, stored as text for precision.

## Error Handling

- Session error → tell user to re-authenticate: `enable-banking auth --bank <ALIAS> --country FR`
- Binary not found → remind user to plug in the USB key
- Never run `auth` yourself — it requires browser interaction

## What NOT to Do

- Do NOT run `tag interactive` or `auth`
- Do NOT use `balances` command separately — use `accounts` which includes balances
- Do NOT modify `~/.enable-banking/config.yaml` unless asked
- Do NOT use `--refresh` by default — local cache is sufficient and faster
