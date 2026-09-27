# Chief of Staff: pitch pack (YC "Own Your Intelligence", 2026-09-27)

Numbers below come from `memory/brief/items.jsonl` (444 items, 2026-09-14 to 2026-09-27), computed at 16:33 PT. The 243 are the items with `done_by: system` (122 skipped, 76 expired, 45 done); the Brief shows the same 243 as "handled without you" over the 443 seed decisions.

## 60-second spoken pitch (~150 words)

My agent remembers everything I tell it. It can do almost any task. But it still does not know what I want.
GBrain gives an agent memory. QM gives it a harness that does the work. Nothing in between owns a person's goals.
So I built that layer: Chief of Staff.
In QM's chat it interviews you and saves your goals into GBrain as you answer. Then it brings you a Brief: the four things only you can decide, each with a recommendation, a default, and an expiry. Today I run it by hand.
Every answer becomes a fact with provenance. Then it reflects and learns a rule.
In the demo, I skip two reply-to-post cards. It learns "rank reply-to-post cards lower", and the next Brief changes.
An earlier version ran in my own assistant for two weeks: 444 items, 243 closed without me. Today I rebuilt it on GBrain and QM, seeded with those real decisions.
I want every agent to start from your goals.

## One-liner (submission form)

Chief of Staff is the goals layer between GBrain (memory) and QM (the harness): it interviews you, keeps your goals in GBrain, brings you the few decisions only you can make, and learns from your answers how to rank the next Brief.

## Project description (~100 words)

Agents now remember a lot and can do a lot, but none of them owns what you are trying to achieve. Chief of Staff adds that layer on top of GBrain and QM. A short interview finds your goals, constraints and unknowns and stores them as GBrain pages with a new schema pack (goal, decision, opportunity, brief). A loop, run by hand today, ranks the open decisions against your goals and writes a Brief: four cards only you can act on, each with a recommendation, a default and an expiry. Your answer is saved as a fact with provenance; a reflect step turns patterns into learned rules that change the next ranking. It runs inside a QM fork as a Brief tab.

## What we built during the hackathon

- **The cos runtime** (`chief-of-staff/cos/cos.py`, stdlib Python): reads the brain out of GBrain (`gbrain export`) at start and on every reset, builds the Brief from it (including goals the QM interview just saved), takes answers, writes each answer and each learned rule to GBrain with provenance, and serves the Brief page on port 8790.
- **The Brief tab in QM** (fork `RRaphaell/qm`, branch `chief-of-staff`): a Brief view in the sidebar and under Browse. The web-ui server proxies the cos page same-origin under /cos/, and the portal allows framing only for /cos, so QM's frame policy stays DENY everywhere else.
- **Six skills**, run live in QM: the interview skill asked the questions in QM's chat and saved a goal to GBrain through the runtime's capture endpoint, and that goal appears on the Brief. Skills: interview, goal-check, originate, decide, brief, learn-taste (GBrain skillpack plus QM skill seeds).
- **The goals schema for GBrain**: a `chief-of-staff` schema pack with page types goal, decision, opportunity, brief, seeded from 443 real decisions.
- **The learning loop**: answer -> fact with provenance -> reflect -> learned rule -> next run ranks differently. In the demo, two skips become the rule "Rank reply-to-post cards lower", with the two decision ids as evidence, and the Brief re-ranks. The rule is a simple count (2 matching answers in demo mode, 3 otherwise), not a trained model.
- Config examples, not exercised live today: the QM Loop file that runs the brief every 3 h, and the GBrain memory-provider example in `docs/chief-of-staff.md`.
