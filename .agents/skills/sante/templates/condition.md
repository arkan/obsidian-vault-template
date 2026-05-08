---
type: health-condition
aliases: []
tags: [health]
status: active
severity: medium
created: {{DATE}}
last_synthesis: {{DATE}}
fact_count: 0
related_medications: []
---

# {{TITLE}}

## Résumé

<!-- 1-3 phrases : nature de la condition, depuis quand, état actuel -->

## Faits actifs

<!-- Faits stables sur la condition. Format : - `<id>` Description #status/active -->

## Faits supersedes

<!-- Faits anciens, devenus faux. Conservés pour historique -->

## Événements liés

```dataview
TABLE date, category, provider
FROM "Areas/Health/Events"
WHERE contains(related, link("{{TITLE}}"))
SORT date DESC
```
