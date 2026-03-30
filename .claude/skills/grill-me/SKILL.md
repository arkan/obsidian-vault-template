---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

# Grill Me

**Trigger:** User says "grill me", "stress-test this", "poke holes", or wants to validate a plan/design/architecture.

## Session Structure

Iterative questioning loop until shared understanding is reached:

1. **Understand scope** — Read the plan/design provided (file or inline). Summarize back in 2-3 sentences to confirm understanding.
2. **Depth-first questioning** — Walk each branch of the decision tree one at a time. Do NOT move to the next branch until the current one is resolved.
3. **Converge** — Once all branches are explored, summarize decisions and output a decision log.

## Question Types

For each branch, cycle through these angles:

- **Assumptions** — "What are you assuming about X? What if that assumption is wrong?"
- **Edge cases** — "What happens when Y is empty / massive / concurrent / malformed?"
- **Tradeoffs** — "You chose A over B — what did you give up? Is that acceptable?"
- **Alternatives** — "Did you consider Z? Here's why it might be better/worse."
- **Failure modes** — "If this breaks at 3 AM, how do you detect it? How do you recover?"
- **Dependencies** — "This decision constrains future choice W — are you okay with that?"

## Rules

- For each question, provide YOUR recommended answer before asking the user.
- If a question can be answered by exploring the codebase, explore the codebase instead of asking.
- Be relentless but not repetitive — move on once a branch is resolved.
- Challenge weak answers: "That sounds hand-wavy — can you be more specific?"
- Track open threads and circle back if something was deferred.

## Output: Decision Log

At the end of the session, produce a structured decision log:

```markdown
## Decision Log — <Plan/Design Name>

| # | Decision | Rationale | Alternatives Considered | Risks Accepted |
|---|----------|-----------|------------------------|----------------|
| 1 | ...      | ...       | ...                    | ...            |

### Open Questions
- ...
```

## Example Session Flow

1. User shares a plan for a new caching layer.
2. Agent summarizes: "You want to add Redis in front of Postgres for read-heavy queries."
3. Agent asks: "You assume read/write ratio is 90/10 — where does that number come from?"
4. User answers. Agent follows up: "What's your invalidation strategy? TTL or event-driven?"
5. Branch resolved. Agent moves to next: "What happens during a Redis outage? Fallback to DB or error?"
6. ... continues until all branches covered.
7. Agent outputs decision log with all resolved decisions and remaining open questions.
