---
type: dashboard
tags:
  - dashboard
---

# Home

## Navigation

| Section | Link |
|---------|------|
| Projects | [[MOC Projects]] |
| People | [[MOC People]] |
| Companies | [[MOC Companies]] |
| Resources | [[MOC Resources]] |
| Goals | [[Goals]] |

## Inbox

```dataview
LIST FROM "Inbox"
WHERE file.name != "A trier"
SORT file.ctime DESC
```

## Current Tasks

```dataview
TASK FROM ""
WHERE !completed AND !contains(file.path, "Templates") AND !contains(file.path, "Archive")
LIMIT 15
```

## Active Projects (overview)

```dataview
TABLE WITHOUT ID file.link as "Project", status, fact_count as "Facts"
FROM "Projects"
WHERE status = "active"
SORT file.name
LIMIT 10
```

## Recent Notes

```dataview
TABLE WITHOUT ID file.link as "Note", file.mtime as "Modified"
FROM ""
WHERE file.name != "Home" AND !contains(file.path, "Templates") AND !contains(file.path, ".obsidian")
SORT file.mtime DESC
LIMIT 10
```

## Archive

```dataview
TABLE WITHOUT ID file.link as "Project", status
FROM "Archive"
SORT file.name
```
