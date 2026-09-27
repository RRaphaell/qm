---
name: goal-check
description: Score every goal page in the brain against the evidence in the brain: status, the one next move, and what the brain does not know. Runs first in every chief-of-staff cycle.
scope: both
mutating: false
triggers:
  - how am I doing on my goals
  - goal check
  - which goal is stalled
  - what is the next move on my goals
  - am I on track
  - review my goals against the brain
---

# goal-check

The brain holds `goals/*` pages (type `goal`). Everything else in the brain is evidence: people, projects, decisions with outcomes, notes, signals. Your job is to read the evidence, not to restate the goal.

## For each goal, write

- `status`: one of `on-track`, `drifting`, `stalled`, `done`. `stalled` means no evidence of movement in the last 14 days. `drifting` means movement that does not serve the metric.
- `evidence`: at most three brain slugs that justify the status. A claim without a slug is not evidence.
- `next_move`: the single next action, under 30 minutes, that a person can do today. Never a list.
- `missing`: what the brain does not know that would change the status. This is the "heads up" line: the channels the brain does not see, the fact nobody filed.

## Rules

1. Read the goal's metric before judging. A goal without a metric gets `drifting` and a `next_move` of "write the metric".
2. Recent decisions with outcome `done` are movement; `skipped` and `expired` are not.
3. Never invent a number. If the brain has no count, say "no count in the brain".
4. Keep every field under 30 words. The person reads this across many sessions.
