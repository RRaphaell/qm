---
name: chief-of-staff-originate
description: Bring the person what they did not ask for. Look inward first (what they own and are not using), then at today's signals, and propose at most three ideas that each serve a named goal with a first step under 30 minutes.
mutating: false
triggers:
  - any ideas for me
  - what should I be doing that I am not
  - what am I missing
  - originate
  - what can you bring me today
  - what am I not using
---

# originate

The bar is origination, not reaction. The person should not have to provide the ideas; the brain knows their goals, so the brain thinks about what can be done.

## Where ideas come from, in this order

1. **What they own and are not using.** Unpublished research, captured data, a paper that unlocks a criterion, credits with no artifact, a person they met and never followed up (people pages with a stale `last_touch`), a deliverable that was built and never posted.
2. **Today's signals.** A person in town, a form that reopened, a deadline extended, a question in their lane they can answer, a room they will be in anyway.
3. **Patterns across the record.** Something that worked twice (a decision with outcome `done` twice) that has no standing habit yet.

## Each idea has

- `title`: plain action, under 12 words.
- `goal`: the goal slug it serves. No goal, no idea.
- `asset`: the brain slug of the thing it uses (a page, a person, a project).
- `first_step`: under 30 minutes, doable today.
- `why_now`: one line. If there is no "why now", it is a backlog item, not an idea.

## Noise budget

- At most three ideas per cycle. Zero is a valid answer.
- An idea the person skipped twice is dead. Check the decisions with outcome `skipped` before proposing.
- Never propose what the record shows they already do. Reinforce the streak instead, in one line.
