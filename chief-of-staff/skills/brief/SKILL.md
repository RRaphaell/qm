---
name: brief
description: Write the one page the person reads: a strip of at most four items only they can do today, short sections by kind, the goal check, and a "handled without you" list. Size beats completeness.
scope: both
mutating: true
triggers:
  - build my brief
  - what needs me today
  - morning brief
  - daily brief
  - what is on my page
  - rebuild the brief
---

# brief

If the person never opens the page, nothing breaks: every item has a default and an expiry. If they open it, they read it in fifteen minutes. That constraint wins over every other rule here.

## Shape of `briefs/<date>` (type `brief`)

1. **Strip**: at most four items, only what they alone can do today, each with the recommendation and the default. Prio 1 first, then the nearest expiry.
2. **Goals**: one line per goal from `goal-check`: status, next move.
3. **Sections by kind**: decide, opportunity, people, learn, post, idea. At most five per section; the rest waits in the store, still open.
4. **Ideas**: what the brain brought that they did not ask for (`originate`). Zero to three.
5. **Handled without you**: defaults that ran, items that expired, facts the brain filed today. This is how they see the system working.

## Rules

- One line per item on the page: who, gist, chips. Detail lives on the decision page.
- Never nag. An item appears once; if it expires, the default runs and it is listed under handled.
- Three days with nothing acted on means the mix is wrong: shrink the page, change the mix, say so in one line at the top.
- Every named thing carries its link the first time it appears.
- Plain words, short sentences, answer first.

## Learned rules

Written by `cos reflect` from his answers. Each rule carries its evidence (decision ids); the ranking weight is in `out/state.json`.
