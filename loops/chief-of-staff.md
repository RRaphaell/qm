# Loop: chief-of-staff

Defined in the shape `skills-seed/define-loop/SKILL.md` describes. Create it with the `loop` tool after one shadow run.

| Field                 | Value                                                                                                                                                                                                                             |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**              | chief-of-staff                                                                                                                                                                                                                    |
| **Purpose**           | Move the person toward their goals: bring decisions, opportunities and ideas they did not ask for, and learn from every answer.                                                                                                   |
| **Trigger**           | Cron `0 */3 * * *` in the person's timezone (every 3 hours).                                                                                                                                                                      |
| **Source of work**    | Open decision pages in GBrain (`type: decision`, `status: open`) plus new signals (inbox, calendar, feeds). Dedupe key: the GBrain page slug (`decisions/<slug>`); a signal gets a slug on intake.                                |
| **Playbook**          | 1. `chief-of-staff-goal-check` 2. `chief-of-staff-originate` (max 3 ideas) 3. `chief-of-staff-decide` (recommendation, default, expiry) 4. `chief-of-staff-brief` 5. `chief-of-staff-learn-taste` on answers since the last fire. |
| **Success condition** | For one item: a decision page exists with a recommendation, a default and an expiry, tied to a named goal, and it appears on the brief; or the item is closed with a note in "handled without you".                               |
| **Success checks**    | `gbrain get decisions/<slug>` returns frontmatter with `recommendation`, `default`, `expires`, `goal`.                                                                                                                            |
| **Ship actions**      | `update_brief` (write the brief page) - starts at `hold`. No email, no posting, no spending: those are always a decision for the person.                                                                                          |
| **Caps**              | Max 4 items on the "only you" strip; max 3 ideas per fire; max 8 fires per day; stop after 2 fires with no answer and ping once.                                                                                                  |
| **Escalation**        | The owner, in the Brief tab; a ping only for items that expire within 24 hours.                                                                                                                                                   |
