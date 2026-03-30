---
type: moc
tags:
  - moc
  - dashboard
---

# MOC Companies

## Active Companies

```dataview
TABLE WITHOUT ID file.link as "Company", aliases as "Aliases", tags as "Tags", fact_count as "Facts", last_synthesis as "Last Synthesis"
FROM "Areas/Companies"
WHERE status = "active"
SORT file.name
```

## All Companies

```dataview
TABLE WITHOUT ID file.link as "Company", status, fact_count as "Facts"
FROM "Areas/Companies"
SORT file.name
```
