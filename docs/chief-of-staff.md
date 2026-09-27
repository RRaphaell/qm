# Chief of Staff

GBrain remembers what you know. QM does the work. Nothing in between owns a person's
goals and originates. Chief of Staff is that layer: goals live in the brain, an interview
finds goals, constraints and unknowns, a proactive loop brings decisions (recommendation,
default, expiry), opportunities and ideas, a Brief page shows them, and every answer
teaches the next run.

Built on 2026-09-27 at the YC "Own Your Intelligence" hackathon.

## Architecture

**QM (this repo)**

- Skills in `skills-seed/chief-of-staff-*`: `interview`, `goal-check`, `originate`,
  `decide`, `brief`, `learn-taste`. Seeded like every other skill in `skills-seed/`.
- A Loop (`loops/chief-of-staff.md`) that runs the skills every 3 hours.
- A **Brief** tab in the web UI (`plugins/web-ui/src/brief.ts`, route `/brief`). It frames
  the Chief of Staff runtime page (default `http://localhost:8790/`; override with
  `VITE_COS_BRIEF_URL` at build time or `localStorage["qm.cos.briefUrl"]`).
- Sandbox tools: the `gbrain` CLI when present, or `POST $COS_URL/api/capture`
  (default `http://host.docker.internal:8790`).

**GBrain ([garrytan/gbrain](https://github.com/garrytan/gbrain))**

- Page types from the `chief-of-staff` schema pack: `goal`, `decision`, `opportunity`, `brief`.
- Memory verbs: `gbrain call remember` (a fact with `provenance` and `kind`),
  `gbrain call recall`, `gbrain put`, `gbrain get`, `gbrain search`.
- Every fact carries provenance (`interview <date>`, `answer <decision slug>`, a signal id).

**Signals**: inbox, calendar, feeds. Each becomes a candidate with a stable slug.

## The learning loop

1. The person answers a card on the Brief: done, skip, or a note.
2. The answer becomes a fact in GBrain with provenance (`answer decisions/<slug>`).
3. `learn-taste` reflects: three answers of one kind become a learned rule.
4. The next run ranks with the rules, so the Brief changes because of the answer.

## How to run it

```bash
# 1. GBrain: install, then load the seed brain
export PATH=$HOME/.bun/bin:$PATH
cd ~/hack && gbrain import seed/        # goals, people, projects, decisions, notes

# 2. Chief of Staff runtime (serves the Brief and /api/capture on :8790)
cd ~/hack/chief-of-staff && ./run.sh     # see chief-of-staff/README

# 3. QM dev instance
cd ~/hack/qm && npm ci && npm run dev    # open the web UI, then Browse -> Brief
```

PGLite is single-writer: run one `gbrain` process at a time.

## The Loop

| Field             | Value                                                                                                    |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| Trigger           | every 3 hours (`0 */3 * * *`)                                                                            |
| Source of work    | open decisions in GBrain + new signals; dedupe key = page slug                                           |
| Success condition | a decision page with recommendation, default, expiry and goal, shown on the Brief; or closed with a note |
| Ship actions      | `update_brief`, held for review; never email, post or spend                                              |
| Caps              | 4 "only you" items, 3 ideas per fire, 8 fires a day                                                      |

Full definition: `loops/chief-of-staff.md`.

## GBrain as a QM memory provider

Config example, not exercised today. Run `gbrain serve --http` and point a route at it,
in the shape `docs/memory-providers.md` shows:

```json
{
  "providers": [
    {
      "id": "gbrain",
      "type": "mcp",
      "url": "http://localhost:8787",
      "timeoutMs": 3000,
      "read": {
        "tool": "recall",
        "clientIdEnv": "GBRAIN_RO_CLIENT_ID",
        "clientSecretEnv": "GBRAIN_RO_CLIENT_SECRET"
      },
      "write": {
        "tool": "remember",
        "clientIdEnv": "GBRAIN_RW_CLIENT_ID",
        "clientSecretEnv": "GBRAIN_RW_CLIENT_SECRET"
      }
    }
  ],
  "routes": [
    {
      "provider": "default",
      "scopes": ["channel", "group", "team"],
      "capture": "automatic"
    },
    {
      "provider": "gbrain",
      "scopes": ["personal"],
      "capture": "explicit",
      "manage": false,
      "label": "GBrain (Chief of Staff)"
    }
  ]
}
```

## Privacy

The Brief never shows third parties' personal situations, health, family, immigration,
salary, address, email or phone. People-kind decisions stay off the page. Goal titles are
short and carry no money amounts.
