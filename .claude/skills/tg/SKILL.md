---
name: tg
description: >
  Send a Telegram message (and optional attachments) via the `tg` CLI to one of two
  preconfigured destinations: **personal** (personal channel, `TELEGRAM_TOKEN_PERSONAL` +
  `TELEGRAM_CHAT_ID_PERSONAL`) or **automation** (automation channel, `TELEGRAM_TOKEN_AUTOMATION` +
  `TELEGRAM_CHAT_ID_AUTOMATION`). Use this skill whenever the user wants to push a Telegram
  message, send themselves a notification, ping a channel, or forward content to Telegram —
  even if they don't say "telegram" explicitly. Triggers on `/tg`, and conversationally on
  phrasings like "envoie ça à personal", "envoie à automation", "ping personal avec ...", "ping
  automation", "notif automation : ...", "préviens personal que ...", "balance ça à automation", "send to
  personal", or any sentence whose intent is to deliver content to a destination named personal or
  automation. Defaults to **automation** when no destination is given. Always shows a confirmation
  preview unless `--yes` / `-y` is passed.
user_invocable: true
argument-hint: "[personal|automation] <message> [--attach <path>] [--format markdown|html] [--yes]"
---

# tg

Sends content to one of two Telegram bots via the `tg` CLI (a thin wrapper around
`telegram-owl`, packaged via nix at `~/nix/pkgs/tg/`).

## Why two bots

- **personal** → personal voice. Used for messages Florian writes to himself or close circle.
- **automation** → automation voice. Used for task completions, alerts, scripted notifications.

The destination is the *only* thing that picks the persona. Everything else is identical.

## Destinations and aliases

| Canonical | Accepted aliases (case-insensitive) | Token env | Chat env |
|-----------|--------------------------------------|-----------|----------|
| `personal`    | `personal`, `p`                          | `TELEGRAM_TOKEN_PERSONAL`    | `TELEGRAM_CHAT_ID_PERSONAL`    |
| `automation`  | `automation`, `j`                        | `TELEGRAM_TOKEN_AUTOMATION`  | `TELEGRAM_CHAT_ID_AUTOMATION`  |

Default if no destination is specified: **automation**.

## Argument parsing

Input arrives as a free-form argument string (slash) or natural language (conversational).
Extract:

1. **dest**: first whitespace-delimited token if it matches an alias above. Otherwise no
   dest was provided — use `automation` and treat the whole input as body.
2. **flags** (parsed and forwarded to `tg`):
   - `--attach <path>` — file attachment (repeatable; path may be quoted)
   - `--from-file <path>` — read body from a file (overrides any inline body)
   - `--format markdown` / `--format html` — message format
   - `--silent`, `--spoiler`, `--protect`, `--no-link-preview`, `--as-document` — passthrough
3. **body**: whatever remains. Strip surrounding quotes if present. Preserve newlines.

For conversational input, infer the same fields. Examples:
- "envoie ça à personal : Le rapport est prêt" → dest=personal, body="Le rapport est prêt"
- "ping automation avec /tmp/log.txt — build done" → dest=automation, attach=[/tmp/log.txt], body="build done"
- "préviens automation que le déploiement est OK" → dest=automation, body="le déploiement est OK"

## Workflow

### 1. Preview and confirm in chat

Always show the user a preview first and wait for explicit confirmation, *unless* the user
already passed `--yes` / `-y`:

```
→ Destination : personal
  Format     : markdown
  Pièces jointes : /tmp/report.pdf
  Message :
  ---
  **Important** : appelle ta sœur
  ---

  Envoyer ? (y/n)
```

Wait for `y`/`yes`/`oui` (case-insensitive) before proceeding. Anything else cancels.

The model owns this confirmation step — `tg` itself has its own preview prompt, but we
always pass `--yes` to suppress it (the in-chat preview is the source of truth).

### 2. Execute via `tg`

Call the `tg` binary with the resolved arguments. The default user shell is **zsh**, which
will choke on unquoted parens, `&`, glob characters, accents in odd contexts, etc. — so any
body that is not a single trivial line MUST be sent via a temp file (not inlined, not
naively piped). The `--from-file` flag exists exactly for this.

```bash
# Form A — single trivial line, no special chars
tg --yes <personal|automation> "<body>" [--format markdown|html] [--attach <path>]...

# Form B — multi-line OR contains any of:  ( ) & ` $ * ? [ ] { } ! ~ \
# This is the safe default. Use it whenever in doubt.
cat > /tmp/tg-body.txt <<'EOF'
<paste body verbatim here, including newlines, parens, accents, links, etc.>
EOF
cat /tmp/tg-body.txt | tg --yes <personal|automation> [flags...]

# Form C — attachment-only (no body)
tg --yes <personal|automation> --attach <path>
```

**Why Form B exists**: zsh interprets `(text)`, `* ?`, etc. as patterns. Even inside
`printf '%s' '...'` the quoting can be lost across the Bash tool's shell wrapper, producing
errors like `(eval):1: no matches found: (some text)`. A heredoc with `<<'EOF'` (note the
single quotes around `EOF` — they disable variable and command substitution inside the
heredoc) sidesteps every shell-escaping pitfall in one shot. Piping the file via `cat | tg`
then delivers the exact bytes through stdin.

**Why we pipe instead of using `--from-file`**: `tg` resolves the body in this order —
*inline args > stdin (when piped) > --from-file*. When invoked from a non-interactive
shell (like the Bash tool), stdin is *not a tty* but is *empty*, so the stdin branch fires
and reads zero bytes — **the `--from-file` flag is silently ignored** and `tg` errors with
"rien à envoyer". Piping (`cat <file> | tg`) is the only reliable form: stdin is non-empty
*and* non-tty, so `tg`'s stdin branch reads the bytes correctly. (`--from-file` only works
from an interactive terminal — useless to us here.)

Pick Form A only when the body is one short line of plain text. When in doubt, Form B.

`tg` handles env var validation, dest resolution, and the actual `telegram-owl` call. If
env vars are missing it exits non-zero with an explicit French error like
`Erreur : variable d'environnement manquante : TELEGRAM_TOKEN_PERSONAL` — surface that to the
user verbatim.

### 3. Report back

One short sentence: `Envoyé à <dest>.` On failure, surface `tg`'s stderr.

## Examples

**Example 1 — slash, default dest (automation):**

```
/tg "Le déploiement est terminé"
```

→ Preview, confirm, then `tg --yes automation "Le déploiement est terminé"`.

**Example 2 — explicit personal with markdown:**

```
/tg personal --format markdown "**Important** : appelle ta sœur"
```

→ Preview, confirm, then `tg --yes personal --format markdown "**Important** : appelle ta sœur"`.

**Example 3 — conversational with attachment:**

```
envoie ça à automation avec /tmp/report.pdf : Rapport hebdo prêt
```

→ Preview, confirm, then `tg --yes automation --attach /tmp/report.pdf "Rapport hebdo prêt"`.

**Example 4 — bypass confirmation:**

```
/tg automation --yes "Ping done"
```

→ No preview, send immediately: `tg --yes automation "Ping done"`.

**Example 5 — multi-line body (the common case for shortlists, summaries, etc.):**

```
/tg personal "Ligne 1
Ligne 2 (avec des parens) et un & dans le texte
Ligne 3 — accents et tirets : éàç"
```

→ Use Form B (heredoc + pipe). Inlining or `printf '%s' '...'` will break under
zsh on the parens or the `&`:

```bash
cat > /tmp/tg-body.txt <<'EOF'
Ligne 1
Ligne 2 (avec des parens) et un & dans le texte
Ligne 3 — accents et tirets : éàç
EOF
cat /tmp/tg-body.txt | tg --yes personal
```

## Notes

- Do not silently fall back from personal to automation (or vice versa) if a token is missing —
  `tg` already errors explicitly; just relay the message.
- Always pass `--yes` to `tg` since the model handles confirmation in chat. Never let `tg`
  prompt — it would hang.
- `tg` is installed via the nix flake (`~/nix/pkgs/tg/`); source is `tg.sh` if you ever
  need to inspect what flags are available.
