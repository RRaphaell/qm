# Bootstrap: chief-of-staff on a fresh brain

1. Install GBrain (not on npm): `bun install -g github:garrytan/gbrain`, then `gbrain init --pglite --no-embedding`.
2. Activate the schema pack: copy `schema/pack.yaml` to `~/.gbrain/schema-packs/chief-of-staff/pack.yaml`, then `gbrain schema use chief-of-staff`.
3. Give the brain goals: one page per goal under `goals/`, each with an outcome and a metric (`gbrain capture --file goal.md --slug goals/<slug> --type goal`).
4. Point synthesis at the Claude CLI (keyless): `gbrain config set models.tier.subagent claude-cli:claude-sonnet-5`.
5. Run one cycle: `python3 cos/cos.py run --signals signals/` and open `out/brief.html`.
6. Answer one item: `python3 cos/cos.py answer <id> done --note "why"`, then run again and watch the ranking change.
7. Optional, River: `export RIVER_API_KEY=...`, `python3 cos/cos.py taste export`, `python3 cos/cos.py taste train`.
