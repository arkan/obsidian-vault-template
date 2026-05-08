---
type: infrastructure
tags:
  - tools
  - config
last_updated: 2026-02-21
---
# TOOLS.md — Local Configuration

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

---

## GitHub

- **Username:** your-username
- **Auth:** Token configured via `gh auth login`

## Gmail (gog)

- **Account:** you@example.com
- **Keyring password:** `GOG_KEYRING_PASSWORD=your-password`

## Twitter / X (bird)

- **Auth:** Cookies in `~/.config/bird/config.json5`
- **Env vars:** `AUTH_TOKEN`, `CT0` (see config)

## Telegraph

- **Access Token:** your-telegraph-token
- **Author:** Your Author Name

## Synology NAS

- **Hostname:** nas-hostname
- **Services:** Active Backup for Business, C2 Cloud Backup
- **Machine backed up:** your-machine-name

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.
