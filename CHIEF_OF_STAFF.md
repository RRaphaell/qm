# Chief of Staff on QM

Added on 2026-09-27 at the YC "Own Your Intelligence" hackathon.

GBrain remembers what you know; QM does the work. Chief of Staff owns a person's goals
and originates: an interview that finds goals, constraints and unknowns; a loop that
brings decisions (recommendation, default, expiry), opportunities and ideas; a Brief tab;
and a feedback loop where every answer becomes a fact with provenance in GBrain and
changes how the next run ranks.

## New and changed files

- `skills-seed/chief-of-staff-interview/SKILL.md` (new, 10-minute interview)
- `skills-seed/chief-of-staff-goal-check/SKILL.md`
- `skills-seed/chief-of-staff-originate/SKILL.md`
- `skills-seed/chief-of-staff-decide/SKILL.md`
- `skills-seed/chief-of-staff-brief/SKILL.md`
- `skills-seed/chief-of-staff-learn-taste/SKILL.md`
- `plugins/web-ui/src/brief.ts` (new Brief view, iframe)
- `plugins/web-ui/src/{shell-state,shell,browse,document-title}.ts` (register the `brief` view)
- `loops/chief-of-staff.md` (Loop definition, every 3 h)
- `docs/chief-of-staff.md` (architecture, learning loop, how to run, memory provider example)
- `CHIEF_OF_STAFF.md` (this file)

The Brief tab: Browse -> Brief, route `/brief`. It frames `http://localhost:8790/` by
default (`VITE_COS_BRIEF_URL` to change it).

The runtime and the GBrain skillpack live in `chief-of-staff/` (added by the integrator
before the deadline).

Start here: `docs/chief-of-staff.md`.
