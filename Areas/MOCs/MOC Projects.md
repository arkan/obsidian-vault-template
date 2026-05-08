---
type: moc
tags:
  - moc
  - dashboard
---

# MOC Projects

## Active Projects

```dataview
TABLE WITHOUT ID file.link as "Project", status, tags as "Tags", fact_count as "Facts", last_synthesis as "Last Synthesis"
FROM "Projects"
WHERE status = "active"
SORT file.name
```

## Waiting Projects

```dataview
TABLE WITHOUT ID file.link as "Project", status, tags as "Tags"
FROM "Projects"
WHERE status = "waiting"
SORT file.name
```

## Backlog Projects

```dataview
TABLE WITHOUT ID file.link as "Project", tags as "Tags"
FROM "Projects"
WHERE status = "backlog"
SORT file.name
```

## All Projects

```dataview
TABLE WITHOUT ID file.link as "Project", status, fact_count as "Facts"
FROM "Projects"
SORT status, file.name
```
