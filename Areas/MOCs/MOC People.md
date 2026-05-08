---
type: moc
tags:
  - moc
  - dashboard
---

# MOC People

## Active People

```dataview
TABLE WITHOUT ID file.link as "Name", aliases as "Aliases", tags as "Tags", fact_count as "Facts", last_synthesis as "Last Synthesis"
FROM "Areas/People"
WHERE status = "active"
SORT file.name
```

## All People

```dataview
TABLE WITHOUT ID file.link as "Name", status, fact_count as "Facts"
FROM "Areas/People"
SORT file.name
```
