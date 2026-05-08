---
name: brainstorm
description: "Stress-test a raw idea before turning it into a project: reformulate, research the market with Exa deep search, grill the assumptions adversarially, then output a decision log with Go/No-Go/Pivot verdict. Use when the user says /brainstorm, 'j'ai une idée', 'je pense lancer', 'je voudrais creer', 'idée de projet', 'idée de boite', 'on devrait faire X', or shares any half-baked product/business/side-project idea they want to vet before commiting. Especially valuable when the idea is fresh, unvalidated, and the user hasn't yet decided to pursue it."
user_invocable: true
argument: "[one-line pitch] (optional — can also be supplied conversationally)"
---

# Brainstorm — Idea Stress-Test Before Project Launch

Help the user decide whether a raw idea is worth turning into a real project. The skill orchestrates four phases — **Frame → Research → Grill → Verdict** — and ends with a tabulated decision log plus concrete next steps. If the verdict is Go, it scaffolds a `Projects/<Name>.md` file with `status: backlog`.

The whole conversation runs in **French**. The skill itself stays in English so future maintainers can follow the logic.

---

## Why this skill exists

Most ideas die in three ways:
1. **Unexamined assumptions** — "obviously people want this" without evidence
2. **Solved problem blindness** — three competitors already nailed it, the user hadn't checked
3. **Premature commitment** — the user falls in love with v1 of the idea and stops listening

Brainstorm fights all three: it forces reformulation (kills sloppy framing), brings external evidence (kills the bubble), and applies grill-me-style adversarial questioning (kills weak reasoning). The verdict is structured so even a No-Go produces value: a captured rationale that prevents the same idea from being relitigated in two months.

---

## Interaction Model

This is a **conversational** skill, not a one-shot generator. After most exchanges, wait for the user. But always honour these three controls — the user can drop them at any turn:

| User says | Behaviour |
|-----------|-----------|
| `autonome`, `vas-y`, `continue tout seul`, `enchaine` | Stop asking, run remaining phases without confirmation, present the full decision log at the end |
| `stop`, `termine`, `on s'arrete la`, `wrap up` | Wrap up where you are. Produce a partial decision log with explicit "explored / not explored" flags |
| `passe`, `skip`, `next`, `question suivante` | Mark the current branch as deferred (note it as an Open Question) and move on |

If the user asks a clarifying question mid-flow, answer it then resume the phase you were in.

---

## Phase 1 — Frame the Idea

Goal: extract a clean, testable formulation of the idea before doing anything else.

1. Take the user's pitch (from the slash command argument or the first message).
2. **Reformulate it back in 2–3 sentences**, in this canonical shape:
   - "Pour [audience cible], qui [problème ou besoin], on propose [solution] qui [mécanisme/différenciateur]. Le pari principal est que [hypothèse centrale]."
3. Surface the **3–5 implicit assumptions** you detect. Be specific — not "people want this" but "des freelances tech francais payent deja >50€/mois pour ce type d'outil".
4. Ask the user to validate the reformulation and the assumption list. Adjust until he says "ok" or equivalent.

Don't move on until the framing is sharp. A vague framing makes the rest of the skill useless.

---

## Phase 2 — Research the Reality (Exa deep search)

Goal: replace gut feeling with evidence. Use the **`exa`** skill with `type: deep` (it's the right tool for structured market scanning — surface-level `auto` queries are not enough for a launch decision).

Run **at least 3 deep searches**, picking from this menu based on the idea's nature:

- **Existing solutions** — direct and adjacent competitors. Query shape: `"alternatives to [solution] for [audience]"` or `"[problem] tools 2025"`. Use `outputSchema` to extract a list of `{name, description, pricing_model, geography}`.
- **Market signals** — search volume, recent fundings, trend articles, complaints/posts on Reddit/HN/X about the problem. Surface real quotes.
- **Audience reality** — who actually has this problem, where do they hang out, what are they currently doing instead. For B2B ideas, query LinkedIn/company indexes via Exa's `category: "company"` or `"people"`.
- **Failed attempts** — search for "shutting down", "we tried [thing]", post-mortems. Past failures reveal the killer constraints.
- **Regulation / structural blockers** — legal, technical, distribution constraints specific to the user's geography (e.g. France/EU).

Always use `type: "deep"`, `contents.highlights` (not full text — token budget matters since this is a long conversation), and capture **URLs for every claim** so the decision log is auditable.

After research, present a compact synthesis (≤15 lines):
- **Existants** : 3–5 acteurs identifiés avec positionnement
- **Signaux de demande** : forts / faibles / inexistants — citations
- **Audience** : qui, où, quoi font-ils aujourd'hui
- **Bloqueurs** : régulation / structure / technique
- **Surprises** : ce que la recherche a révélé que l'utilisateur n'avait pas anticipé

End the phase by asking: "Ces données changent comment ta vision de l'idée ?" Update the framing if needed.

---

## Phase 3 — Grill (adversarial questioning, evidence-armed)

Goal: stress-test the idea using the `grill-me` pattern, but now armed with the Exa research — every challenge cites evidence when possible.

Walk these branches **one at a time, depth-first**. Don't move to the next branch until the current one is resolved or explicitly deferred. For each question, **state your own recommended answer first**, then ask the user to confirm/correct.

### Branches to cover

1. **Value proposition vs. existants**
   - "Acteur X fait déjà Y pour ce prix — qu'est-ce qui te rend 10× meilleur ou différent ?"
   - "Si X copie ta feature en 2 semaines, qu'est-ce qu'il te reste ?"

2. **Audience & Wedge**
   - "Quel est le plus petit segment où tu peux gagner de manière indiscutable ?"
   - "Comment tu touches les 10 premiers clients ? Soit concret — pas 'on fera du SEO'."

3. **Hypothèse centrale (kill criterion)**
   - "Quelle expérience la moins chère possible peut invalider l'hypothèse principale en moins de 4 semaines ?"
   - "Si après cette experience c'est négatif, tu pivotes ou tu lâches ? Engage-toi maintenant."

4. **Business model & unit economics**
   - "Combien de clients × combien par mois pour que ça vaille ton temps ?"
   - "Coût d'acquisition réaliste vs. lifetime value — fais le calcul, même grossier."

5. **Coût d'opportunité & alignment**
   - "Tu vas sacrifier quoi pour faire ça ? Liste-le."
   - "Cette idée est-elle alignée avec tes objectifs dans `Areas/Goals.md` ? Si non, pourquoi celle-là maintenant ?"

6. **Failure modes**
   - "Cite les 3 raisons les plus probables pour que ce projet meure dans les 6 mois."
   - "Comment tu détectes chacune en avance ?"

7. **Skin in the game**
   - "Combien de temps / d'argent tu mets en risque sur les 90 prochains jours ?"
   - "Quel est le 1er livrable concret livrable la semaine prochaine ?"

Be relentless but not repetitive — close a branch as soon as the answer is concrete and cited. Challenge handwavy answers ("ça parait flou — chiffre ou exemple ?"). If a branch genuinely can't be answered now, log it as an Open Question and move on.

---

## Phase 4 — Verdict & Decision Log

Goal: a structured, auditable output. Present the decision log inline in chat **and** offer to write the project file.

### Output structure

```markdown
# Brainstorm — <Nom de l'idée>

## Reformulation finale
Pour [audience], qui [problème], on propose [solution] qui [différenciateur]. Pari : [hypothèse].

## Verdict
**[GO | NO-GO | PIVOT]** — <une ligne de justification>

## Decision Log

| # | Décision | Rationale | Evidence | Risques acceptés |
|---|----------|-----------|----------|------------------|
| 1 | …        | …         | <url ou "intuition"> | … |

## Existants (top 3)
- **[Nom]** — positionnement, prix, [url]
- …

## Open Questions (à résoudre avant launch)
- …

## Next Steps (si GO)
- [ ] Action très concrète #1, livrable sous 7 jours
- [ ] Action très concrète #2, livrable sous 14 jours
- [ ] Action très concrète #3, livrable sous 30 jours
```

### Verdict rules

- **GO** — l'hypothèse centrale est plausible, le wedge est défini, le coût d'opportunité est accepté, et il existe un kill criterion clair sous 4 semaines.
- **PIVOT** — le problème est réel mais la solution proposée n'est pas la bonne. Reformule l'idée pivotée et propose un nouveau brainstorm rapide.
- **NO-GO** — l'hypothèse centrale est invalidée par la recherche, ou un acteur dominant rend le wedge irréaliste, ou le coût d'opportunité est trop élevé. Capture la raison pour qu'elle ne soit pas relitigée dans 2 mois.

### File output

Always propose the file write — don't write silently. Show the path and a snippet, ask "j'écris ?" before creating.

**If GO** → `Projects/<Nom-Du-Projet>.md` with this frontmatter:

```yaml
---
type: project
aliases: []
tags: [brainstorm]
status: backlog
created: <YYYY-MM-DD>
last_synthesis:
fact_count: 0
area:
---
```

Body: insert the decision log markdown. Add a `## Faits actifs` empty section so future `/fact` calls work.

**If PIVOT** → same as GO but add `tags: [brainstorm, pivot]` and note the original framing in the body for context.

**If NO-GO** → write to `Inbox/<YYYY-MM-DD>-brainstorm-<short-slug>.md` (no project frontmatter, just `type: note` and `tags: [brainstorm, no-go]`). The point is to keep the rationale findable, not to clutter `Projects/`.

After writing, also propose 1–3 `/todo` lines the user can paste — first concrete actions linked to the new project (e.g. `/todo add Tester wedge auprès de 5 freelances @<Nom-Du-Projet> !high ⏳ +14d`).

---

## Operating Principles

- **One question per turn** during Phases 1 and 3 — don't machine-gun.
- **Cite evidence** whenever possible during Phase 3 — "selon [url], le marché est…". The whole point of Phase 2 is to make Phase 3 evidence-based.
- **Recommend before asking** — every grill question comes with your own best guess. the user's job is to confirm or correct, not to start from a blank page.
- **Respect autonomy** — you challenge, you don't decide. Even on a NO-GO, the user can override; just record the override in the decision log.
- **No empty politeness** — "intéressante idée" is forbidden. Either the idea survives the grill or it doesn't.
- **Ground in vault context** — silently read `Areas/Goals.md` and the last 2–3 weekly review notes before Phase 3, so the opportunity-cost branch is real, not theoretical.

---

## Example Session Skeleton

```
User: /brainstorm un outil pour aider les freelances à faire leurs devis automatiquement

Skill (Phase 1): "Reformulation: pour [freelances tech FR], qui [galèrent à chiffrer leurs devis], on propose [un outil qui génère un devis à partir d'un brief client] qui [propose des fourchettes de prix basées sur le marché]. Pari: les freelances payent pour gagner 30 min/devis. Hypothèses implicites: (1) ils font assez de devis pour que ça compte (2) ils trouvent leurs prix actuels mauvais (3) ils n'utilisent pas déjà ChatGPT pour ça. Tu valides cette formulation ?"

User: ok

Skill (Phase 2 — exa deep × 3): "Recherche en cours…" [3 searches] "Synthèse:
- Existants: Bonsai, AND.CO, Indy facturation… 3 acteurs établis sur facturation, mais aucun centré sur génération de devis
- Signaux de demande: r/freelance_fr, plusieurs threads 'comment chiffrer un devis' >100 commentaires
- Audience: 800k freelances en France, ~30% en tech
- Bloqueurs: aucun majeur
- Surprise: ChatGPT est déjà utilisé par ~40% des freelances tech selon enquête Malt 2025
Ça change quoi pour toi ?"

User: la concurrence ChatGPT change tout en fait

Skill (Phase 3): commence le grill, branche 1 (value prop): "Acteur de référence ici c'est ChatGPT générique, gratuit. Mon recommandation: ton wedge ne peut pas être 'générer un devis', il faut que ce soit 'devis FR conformes + prix marché vérifié + intégration facturation'. Tu es d'accord ou tu vois un autre angle ?"

[continue 6 branches]

Skill (Phase 4): produit la decision log table, verdict PIVOT (de générateur de devis vers assistant de pricing freelance), propose Projects/Pricing-Assistant-Freelance.md, propose 3 todos.
```

---

## When NOT to use this skill

- The user has already committed to the project and is past the "should I do this?" stage → use `/coach decision` or just start working.
- The user is asking a single factual question → use `/exa` directly.
- The user wants a polished market research report for stakeholders → use `/deep-research`.
- The user is debugging or executing on an existing project → no, just help with the work.

This skill is for the **pre-commitment** moment specifically.
