---
type: moc
tags:
  - moc
  - dashboard
---

# MOC Resources

## Articles

```dataview
TABLE WITHOUT ID file.link as "Article", tags as "Tags", status, file.mtime as "Modified"
FROM "Resources/Articles"
SORT file.mtime DESC
```

## Awesome Lists

```dataview
TABLE WITHOUT ID file.link as "Resource", tags as "Tags", file.mtime as "Modified"
FROM "Resources"
WHERE contains(file.name, "Awesome")
SORT file.name
```

## Technical Documentation

```dataview
TABLE WITHOUT ID file.link as "Resource", tags as "Tags", file.mtime as "Modified"
FROM "Resources"
WHERE !contains(file.name, "Awesome") AND !contains(file.path, "Articles")
SORT file.name
```

## Global View

```dataview
TABLE WITHOUT ID file.link as "Resource", tags as "Tags", file.mtime as "Modified"
FROM "Resources"
SORT file.mtime DESC
```
