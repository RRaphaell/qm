---
name: decide
description: Turn anything that needs the person into a decision page with a recommendation, a default that runs if they say nothing, and an expiry. The person decides; the brain tracks.
scope: both
mutating: true
triggers:
  - what needs my decision
  - turn this into a decision
  - what do I have to decide today
  - add a decision with a default
  - what happens if I do nothing
  - decisions due
---

# decide

The person's bottleneck is deciding, not producing. So every item that reaches them is one decision, with one recommendation, and a default that runs if they stay silent. Nothing waits on them forever.

## A decision page (`decisions/<id>`, type `decision`)

- `title`: a plain action ("Take the free judge ticket for Oct 8"), never a topic.
- `why`: one line, the reason it is in front of them today.
- `recommendation`: what the chief of staff would do, one line.
- `default`: what happens if they say nothing by `expires`. A default is an action the brain can take or a safe non-action. Never "wait for him".
- `expires`: a date. After it, the default runs and the item moves to "handled without you".
- `kind`: `decide`, `opportunity`, `people`, `learn`, `post`, or `idea`.
- `prio`: 1 (only they can do it, today), 2 (this week), 3 (nice).
- `goal`: the goal slug it serves.
- `url`: the source, when there is one. Every named event, form, person or paper carries its link.

## Rules

1. **Hard deadlines only.** A form closes, an event happens, a ticket sells out: that reaches the person. A date the assistant set is the assistant's to move; it never reaches them.
2. **A parked decision does not come back.** A decision is only ready when the thing it must be compared against exists.
3. **Never ask what the record already answers.** If a trace (a sent mail, a registration, a post) shows it done, it is done.
4. **One item per source.** Two decisions from one page is a sign the page was misread.
5. **Recommendation before question.** They should be able to answer "yes" and nothing else.
