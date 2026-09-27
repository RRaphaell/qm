---
name: chief-of-staff-interview
description: A 10-minute interview that fills the brain with what a Chief of Staff needs - the goals that matter this year and their metric, constraints, what the person owns and does not use, what they avoid, the people who matter, and the unknowns that would change the plan. Saves every answer to GBrain with provenance. Use when someone says "interview me", "set up my chief of staff", "what are my goals", or when the brain has no goal pages.
---

# chief-of-staff-interview - find goals, constraints, unknowns

Ten minutes. One question at a time. Never a form, never a list of questions.
Keep each question short. Reflect the answer back in one line before the next one.

## The questions (in this order, adapt the wording)

1. **Goals.** "What are the 1-3 things that must be true by the end of this year?" Then for each: "How will you know? What is the number?"
2. **Constraints.** "What limits you: time per week, money, a legal or visa-like limit, a date you cannot move?"
3. **Owned, not used.** "What do you already own and are not using? Unpublished work, data, credits, relationships, an audience."
4. **Avoiding.** "What are you avoiding right now, and why?"
5. **People.** "Who are the 3-5 people who matter most for these goals?" (names and role only; never health, family or money details)
6. **Unknown unknowns.** "What would change your plan if it were true?" Ask twice, once per top goal.

Stop at 10 minutes even if a section is thin. Thin is an unknown: save it as one.

## Save after every answer (do not batch)

Provenance on every write: `interview <YYYY-MM-DD>`.

If `gbrain` is on PATH (run from the brain dir):

- goal: `gbrain capture --slug goals/<slug> --type goal` with the goal, its metric and the date
- unknown: `gbrain capture --slug unknowns/<slug>` with the question and which goal it touches
- anything else (constraint, owned asset, avoided thing, person):
  `gbrain call remember '{"fact":"...","provenance":"interview <date>","kind":"<constraint|asset|avoid|person>"}'`

If `gbrain` is not available in the sandbox, POST to the Chief of Staff runtime
(`COS_URL` defaults to `http://host.docker.internal:8790`):

```bash
curl -s -X POST "${COS_URL:-http://host.docker.internal:8790}/api/capture" \
  -H 'content-type: application/json' \
  -d '{"type":"goal","title":"<short title>","body":"<answer + metric>","provenance":"interview <date>"}'
```

`type` is one of `goal`, `unknown`, `fact`.

## Privacy

Save short, sanitized goal titles with no money amounts. Never store third parties'
health, family, immigration, salary, address, email or phone details.

## End

Summarize in exactly 5 lines: the goals with their metric, then the top unknowns.
Then say: "Your brief is ready in the Brief tab."
