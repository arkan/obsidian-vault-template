---
name: sync
description: "Sync the Obsidian vault with git: pull, commit, and push. Use this skill whenever the user wants to sync, save, backup, commit, pull, push, or mentions /sync. Handles the full git workflow (pull --rebase, stage, commit, push) with automatic conflict resolution."
user_invocable: true
argument: "[pull|push]"
argument-hint: "/sync, /sync pull, /sync push"
---

# Git Sync

Sync the vault with the remote git repository. Three modes:

- `/sync` (default) — pull, commit, push (full round-trip)
- `/sync pull` — pull only (rebase)
- `/sync push` — commit and push only (no pull)

## Workflow

### 1. Commit (skip if `pull` mode)

Check if there are changes to commit:

```bash
git status --porcelain
```

If empty, skip to pull. Otherwise:

```bash
git add -A
git commit -m "vault sync $(date '+%Y-%m-%d %H:%M')"
```

Using `git add -A` is fine here — this is a personal vault, not a code repo. Everything should be tracked.

### 2. Pull (skip if `push` mode)

```bash
git pull --rebase origin main
```

Committing first means the working tree is always clean before pull — no stash gymnastics needed.

If the rebase hits conflicts:
- Run `git diff --name-only --diff-filter=U` to list conflicted files
- For each conflicted file, read it and resolve the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) by keeping both sides merged intelligently — this is an Obsidian vault, so prefer keeping all content rather than discarding
- After resolving, `git add <file>` and `git rebase --continue`
- If resolution fails after 2 attempts, abort with `git rebase --abort` and tell the user what happened

### 3. Push (skip if `pull` mode)

```bash
git push origin main
```

## Output

Report a short summary to the user:
- What was done (pulled, committed, pushed)
- Number of files changed if a commit was made
- Any conflicts that were resolved
- Any errors encountered

Keep it to 2-3 lines max. No fluff.
