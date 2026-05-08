---
type: health-medication
aliases: []
tags: [health, medication]
status: active
dosage: ""
frequency: ""
started: {{DATE}}
stopped: ""
prescribed_by: ""
treats: []
created: {{DATE}}
last_synthesis: {{DATE}}
fact_count: 0
---

# {{TITLE}}

## Résumé

<!-- Substance active, indication, durée prévue -->

## Faits actifs

<!-- Format : - `<id>` Description #status/active -->

## Faits supersedes

## Effets observés

<!-- Effets ressentis (positifs ou négatifs), au fil du temps -->

## Prises récentes

```dataview
TABLE file.name as "Log"
FROM "Areas/Health/Measurements"
WHERE contains(file.content, "{{TITLE}}")
SORT file.name DESC
LIMIT 5
```
