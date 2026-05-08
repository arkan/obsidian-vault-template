---
name: recipes
description: Manage the user's cooking recipes — add, search, display, rate, mark as cooked. USE WHEN user mentions cooking, meals, recipes, ingredients, or asks questions like "what can I cook with X", "I made pasta last night", "give me a quick Italian dish idea", "rate this carbonara recipe 5 stars". Also explicitly triggered via `/recipes <command>` (list/search/show/add/used/rate/favorite/delete/random). Do NOT trigger for: health/symptom food talk ("I feel nauseous"), restaurants visited, metaphors ("the recipe for success").
user_invocable: true
argument: "(optional) recipes command or free-form text"
---

# Recipes Skill

Manages the vault's cooking recipes. Storage: `Resources/Recipes/<slug>.md`. Dashboard: `Resources/Recipes/Recipes.md`.

## Philosophy

The user talks about cooking in natural language. The skill's role = **route** the sentence to the right action — add a new recipe, mark a recipe as cooked, run a search, or suggest an idea — without imposing a rigid syntax. For deterministic operations (atomic file mutations), use `scripts/recipes.py`. For searches, prefer grep / dataview / direct read.

## Architecture

```
Resources/Recipes/
├── Recipes.md                      # Dataview dashboard (favorites, most used, by tag)
├── carbonara.md                    # One recipe = one file
└── ...
```

## Recipe Format

```yaml
---
type: recipe
aliases: ["carbo"]                  # optional — search nicknames
url: null                            # web source or null
rating: null                         # 1-5 or null
tags: [main, italian, quick]
prep_time: 15min
cook_time: 20min
portions: 4
difficulty: medium                   # easy/medium/hard
favorite: false
created: 2026-04-26
last_used: null
use_count: 0
---

# Recipe Name

## Ingredients
- 400g pasta
- ...

## Preparation
1. Step 1
2. ...

## Notes
Tips, variations, free-form wikilinks: [[Alice Martin|Alice]] loves it, inspired by a local restaurant, see also [[Carbonara]]...
```

Free-form wikilinks anywhere in the body — Obsidian automatically builds backlinks.

## Routing — how to decide

Read the sentence and apply this decision tree:

1. **Explicit command `/recipes <verb>`** → execute via `scripts/recipes.py` (see § "Commands" below).

2. **Conversational phrase** → identify the intent:
   - *"I made/cooked/ate X last night"* → `recipes.py used <slug>` (increments `use_count`, updates `last_used`). If not rated, suggest `rate`.
   - *"what can I cook with X"* → ingredient search (grep in body).
   - *"give me a quick Italian dish idea"* → `recipes.py list --tag italian` filtered by `quick`, or `recipes.py random --tag italian`.
   - *"add the recipe for Y"* → `recipes.py add` then ask for details (ingredients, preparation).
   - *"what do I know about carbonara"* → `recipes.py show <slug>`.
   - *"5 stars for carbonara"* → `recipes.py rate carbonara 5`.

3. **Not a recipe request** → do not trigger (see § "Anti-triggers").

## Commands (Python script)

All via `python3 .Codex/skills/recipes/scripts/recipes.py <command>` (from vault root).

| Command | Usage |
|---|---|
| `list` | List all (options `--tag X`, `--favorite`, `--sort rating\|use_count\|last_used`) |
| `search "term"` | Search in title/tags/body |
| `show "name"` | Display a recipe (slug or partial match) |
| `add "Name" [--url U] [--tags t1,t2] [--prep-time 15min] [--cook-time 30min] [--portions 4] [--difficulty easy]` | Create skeleton file |
| `used "name"` | Increment `use_count`, set `last_used` to today |
| `rate "name" <1-5>` | Rate the recipe |
| `favorite "name"` | Toggle favorite |
| `delete "name"` | Delete |
| `random [--tag X]` | Random recipe |
| `edit "name"` | Display meta + body to prepare an edit |

The script handles slugify (accents → ascii, spaces → dashes), consistent YAML writing, and appending to the operations log (`Areas/Codex/operations-log.md`).

## Typical Conversational Workflow

1. **Identify** the latent command via the decision tree.
2. **Ask 0-2 questions** only if critical info is missing:
   - "I made pasta last night" → *"Which one? carbonara, bolognese…"* (if multiple candidates)
   - "add Mushroom Risotto" → *"Tags? prep/cook time? We can fill it in later."*
   - "5 stars for carbo" → 0 questions, execute (smart-default on alias).
3. **Execute** the command (Python script for mutations, grep/dataview for reads).
4. **Confirm** with the result (script output or summary).

## Smart-default for ambiguous references

If the user says "carbo", "risotto", "that dish":
1. List candidates: `recipes.py list` or grep by alias.
2. If **1 match** → execute while stating the inference (*"assuming [[carbonara]]"*).
3. If **0 matches** → ask which recipe or offer to create one.
4. If **N matches** → list them and ask to choose.

## Suggested Tags

**Type**: appetizer, main, dessert, starter, side, sauce, drink, breakfast
**Cuisine**: french, italian, asian, mexican, indian, mediterranean, japanese
**Diet**: vegetarian, vegan, gluten-free, low-carb, healthy
**Occasion**: quick, batch-cooking, comfort-food, summer, winter, party
**Protein**: chicken, beef, pork, fish, seafood, tofu, eggs

Simple tags (no hierarchy). Dataview filtering via `WHERE contains(tags, "italian")`.

## Search

The user may ask:

- *"what Italian recipes do I have?"* → `recipes.py list --tag italian`
- *"find me something with chicken"* → `grep -li "chicken" Resources/Recipes/*.md`
- *"which recipe have I cooked the most?"* → `recipes.py list --sort use_count`
- *"give me a quick Italian dish"* → `recipes.py random --tag italian` (then filter for quick)
- *"open carbonara"* → `recipes.py show carbonara`

For multi-tag or complex searches, **prefer dataview** in the dashboard rather than chaining script flags.

## Dashboard `Recipes.md`

`Resources/Recipes/Recipes.md` aggregates everything via dataview. If missing or broken, restore from the reference block at the bottom of this skill.

## Anti-triggers (Do NOT trigger)

- *"I feel nauseous"*, *"I eat too much pizza"* → use `/sante` (symptom/anxiety), not cooking.
- *"we had lunch at restaurant X"* → not a personal recipe, optionally capture in `/inbox` or daily note.
- *"the recipe for success"*, *"miracle recipe"* → metaphor.
- *"Alice likes this dish"* (without an identified recipe context) → conversation, not a recipe file action.

## Rules

- **French** for all content (consistent vault)
- **Valid YAML snake_case frontmatter** — quote values with `:` or special characters
- **Slug = filename without accents**: `cake-au-chevre-et-epinards.md`, not `Cake au Chèvre.md`
- **Before mutating writes**, show the plan to the user (except explicit `/recipes <verb>` commands which are already instructions).
- **Prefer `recipes.py used` over manually editing frontmatter** — the script handles timestamps + logging.
- **Free-form wikilinks** in the body — don't invent targets, verify `Areas/People/`, `Resources/`, other recipes first.
- **One recipe per file** — no multi-recipe files.

## Links (wikilinks)

- Recipe notes: `[[Alice Martin|Alice]]` (who likes it), `a local restaurant` (inspiring restaurant), `[[Carbonara]]` (variation of)
- If citing a non-existent entity, **don't create the wikilink** — use plain text. Don't pollute the graph.

## Post-action — Log

The Python script `recipes.py` already automatically logs every mutation to `Areas/Codex/operations-log.md`:
```
| YYYY-MM-DD HH:MM | <action> | recipes | <summary> | <path>
```
For off-script actions (manual recipe edits via the Edit tool), manually append the line after the operation.

## Reference Recipes.md

If `Resources/Recipes/Recipes.md` is missing, create it with this content:

```markdown
---
type: dashboard
title: Recipes
created: YYYY-MM-DD
---

# Recipes

Entry point for all vault recipes. Add/search via the `/recipes` skill or natural conversation.

## ❤️ Favorites

```dataview
TABLE rating, tags, use_count as "Cooked"
FROM "Resources/Recipes"
WHERE type = "recipe" AND favorite = true
SORT rating DESC, use_count DESC
```

## 🔥 Most Used

```dataview
TABLE use_count as "Cooked", last_used as "Last time", rating
FROM "Resources/Recipes"
WHERE type = "recipe" AND use_count > 0
SORT use_count DESC
LIMIT 10
```

## 🆕 Recent (last 30 days)

```dataview
TABLE created, tags, difficulty
FROM "Resources/Recipes"
WHERE type = "recipe" AND created >= date(today) - dur(30 days)
SORT created DESC
```

## 📊 All Recipes

```dataview
TABLE rating, tags, use_count, last_used
FROM "Resources/Recipes"
WHERE type = "recipe"
SORT file.name ASC
```
```

## Examples

**Input**: `/recipes list --tag italian`
→ `python3 .Codex/skills/recipes/scripts/recipes.py list --tag italian`
→ Output: filtered list

**Input**: *"I made carbonara pasta last night, it was great"*
→ You: *"Nice, I'm marking [[carbonara]] as cooked yesterday (2026-04-25). Want to rate it?"*
→ If yes → `recipes.py used carbonara` then `recipes.py rate carbonara <N>`.

**Input**: *"what can I cook with chicken and rice?"*
→ `grep -li "chicken" Resources/Recipes/*.md` then filter for "rice" → present matches.

**Input**: *"give me a quick Italian dish idea"*
→ `recipes.py list --tag italian` then filter for "quick" tag → suggest 1-3 recipes.

**Input**: *"add Mushroom Risotto, Italian comfort food"*
→ You: *"OK, creating. Tags `italian, comfort-food, main`? prep/cook time? we can fill in later."*
→ `recipes.py add "Risotto aux champignons" --tags italian,comfort-food,main`
→ Confirm with the created path.

**Input**: *"5 stars for carbo"*
→ You: *"5⭐ for [[carbonara]]"* (smart-default — 1 candidate with alias "carbo")
→ `recipes.py rate carbonara 5`
