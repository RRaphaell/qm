#!/usr/bin/env python3
"""cos: Chief of Staff runtime. Stdlib only. CLI + HTTP server (127.0.0.1:8790).
Reads seed pages from disk (fast), keeps live state in out/state.json, writes to GBrain in a background queue."""
import shutil, json, os, re, sys, threading, queue, subprocess, datetime, time, collections
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.environ.get("COS_SEED", "/home/ubuntu/hack/seed")

def sync_from_gbrain():
    """Read the brain from GBrain (gbrain export), so the Brief always reflects what the brain holds now."""
    global SEED
    dst = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "brain")
    env = dict(os.environ); env["PATH"] = "/home/ubuntu/.bun/bin:" + env.get("PATH", "")
    try:
        shutil.rmtree(dst, ignore_errors=True)
        r = subprocess.run(["gbrain", "export", "--dir", dst], cwd="/home/ubuntu/hack", env=env, capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and os.path.isdir(os.path.join(dst, "decisions")):
            SEED = dst; return True
    except Exception:
        pass
    return False
HACK = "/home/ubuntu/hack"
OUT = os.path.join(ROOT, "out"); os.makedirs(OUT, exist_ok=True)
STATE = os.path.join(OUT, "state.json")
SKILL_BRIEF = os.path.join(ROOT, "skills", "brief", "SKILL.md")
WEB = os.path.join(ROOT, "cos", "web")
DEMO = os.environ.get("COS_DEMO", "1") == "1"
TODAY = datetime.date.fromisoformat(os.environ.get("COS_TODAY", datetime.date.today().isoformat()))
REDACT = re.compile(r"\bTier \d+,?\s*(\d+ mutuals)?\s*(-|,)?\s*|\(Tier \d[^)]*\)\s*|,?\s*\d+ mutuals", re.I)
CARD_KINDS = {"decide", "opportunity", "learn", "post"}
LOCK = threading.RLock()

# privacy: never show these on the public page
SENSITIVE = re.compile(r"\b(openreview|emergency review|reviews? \(|paste (the|your) \d|paper \d+|ratings?|confidence \d|merge (backend|frontend)|#\d{3,}|rap-\d+|visas?|o-1|immigra\w*|green.?card|uscis|salary|salaries|health|doctor|dermat\w*|urolog\w*|blood|dental|eb-?1a|ledger|"
                       r"kids?|baby|wedding|sick|hospital|funeral|phone|passport|tatia|wife|family|pregnan\w*|lawyer|attorney|"
                       r"tax|taxes|bank|rent|lease|address|payments?|billing|invoices?|declined|refunds?|priced|pricing|credit card|(his|her) (last \d|life))\b|\$\s?\d|\d+\s?(usd|dollars)|@gmail|[\w.-]+@[a-z0-9.-]+\.(com|ai|ge|io)\b", re.I)

GOALS = [  # sanitized short titles of the 2026 goals (health and immigration goals are private: not shown)
    {"id": "brand", "title": "Be known for AI agents", "kw": r"\bpost|blog|thread|follower|quote|reply|plugin|skill|open.?source|launch|x\.com"},
    {"id": "career", "title": "Do frontier agent research", "kw": r"openai|anthropic|codex|claude code|role|job|hiring|team|portfolio|interview"},
    {"id": "conferences", "title": "Contribute at top AI venues", "kw": r"neurips|icml|iclr|acl|arr|workshop|paper|review|cfp|openreview|submission|benchmark"},
    {"id": "sf", "title": "Deep ties in the SF AI scene", "kw": r"\bsf\b|san francisco|meetup|event|luma|night|dinner|hackathon|room|mixer|summit"},
    {"id": "english", "title": "Speak with confidence", "kw": r"speak|talk|stage|panel|podcast|record|english"},
    {"id": "fullstack", "title": "Ship full-stack on his own", "kw": r"react|typescript|\bts\b|frontend|full.?stack|deploy|course|learn|tutorial"},
    {"id": "reflect", "title": "Monthly reflection", "kw": r"monthly|reflect|retro|review of the month"},
]
KIND_GOAL = {"post": "brand", "share": "brand", "learn": "fullstack", "news": "brand"}
NEXT_MOVE = {"brand": "Reply to one THE TEAMS post today", "career": "Ship one public artifact this week",
             "conferences": "Finish the open review assignment", "sf": "Pick one SF room this week",
             "english": "Record one 5-min talk", "fullstack": "One hour on the React track", "reflect": "Run the monthly review on the 1st"}
STOP = set("the a an and or of to in on for with is are be it this that from by at as his he you your not no".split())

def parse_page(path):
    t = open(path, encoding="utf-8").read()
    fm, body = {}, t
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    if m:
        body = m.group(2)
        lines = m.group(1).splitlines()
        for i, line in enumerate(lines):
            mm = re.match(r'(\w+):\s*(.*)', line)
            if mm:
                v = mm.group(2).strip()
                if v in (">-", ">", "|", "|-", ">+", "|+"):
                    cont = []
                    for nxt in lines[i + 1:]:
                        if nxt.startswith("  "): cont.append(nxt.strip())
                        else: break
                    v = " ".join(cont)
                if v.startswith('"') and v.endswith('"'):
                    try: v = json.loads(v)
                    except Exception: v = v[1:-1]
                elif len(v) >= 2 and v.startswith("'") and v.endswith("'"):
                    v = v[1:-1].replace("''", "'")
                fm[mm.group(1)] = v
    return fm, body, t

def field(body, label):
    m = re.search(r"^" + re.escape(label) + r":[ \t]*(.*)$", body, re.M)
    return m.group(1).strip() if m else ""

def load_decisions():
    out = []
    d = os.path.join(SEED, "decisions")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md"): continue
        fm, body, raw = parse_page(os.path.join(d, f))
        meta = re.search(r"priority (\d+) · created ([\d-]+) · expires ([\d-]+)", body)
        why = field(body, "Why it reached him")
        default = field(body, "Default if he said nothing")
        rec = ""
        mm = re.search(r"Recommendation:\s*(.+?)(?:\.\s|$)", why)
        if mm: rec = mm.group(1)
        ma = re.search(r"ANGLE[^:]*:\s*(.+?)(?:\.\s|$)", why)
        if ma:
            rec = "Reply with this angle: " + ma.group(1)
            why = why[:ma.start()].strip() or why
        if fm.get("kind") == "post" and not default: default = "Nothing is posted; the card expires"
        if fm.get("kind") == "post" and not rec: rec = "Reply with one line from your own work"
        links = [u for u in re.findall(r"https?://[^\s)\]]+", body) if "linear.app" not in u and "localhost" not in u]
        title = fm.get("title", f[:-3])
        author = (re.match(r"@(\w+)", title) or [None, None])[1] if title.startswith("@") else ""
        out.append({"id": f[:-3], "title": title, "kind": fm.get("kind", ""), "status": fm.get("status", ""),
                    "done_by": fm.get("done_by", ""), "date": fm.get("date", ""),
                    "prio": int(meta.group(1)) if meta else 3, "created": meta.group(2) if meta else fm.get("date", ""),
                    "expires": meta.group(3) if meta else "", "why": why, "default": default, "rec": rec or default,
                    "link": links[0] if links else "", "author": author, "raw": raw})
    return out

def goal_of(dec):
    text = (dec["title"] + " " + dec["why"][:300]).lower()
    for g in GOALS:
        if re.search(g["kw"], dec["title"].lower()): return g["id"]
    if dec["kind"] in KIND_GOAL: return KIND_GOAL[dec["kind"]]
    for g in GOALS:
        if re.search(g["kw"], text): return g["id"]
    return "career"

def private(dec):
    return dec["kind"] == "people" or bool(SENSITIVE.search(dec["raw"]))

def keywords(dec):
    words = re.findall(r"[a-z][a-z0-9-]{3,}", dec["title"].lower())
    return [w for w in words if w not in STOP][:8]

# ---------------- state ----------------
def load_state():
    if os.path.exists(STATE):
        try: return json.load(open(STATE))
        except Exception: pass
    return {"answers": [], "weights": {}, "rules": [], "ideas": None, "goal_status": {}, "events": []}

def save_state(s):
    tmp = STATE + ".tmp"; json.dump(s, open(tmp, "w"), indent=1); os.replace(tmp, STATE)

def event(s, kind, text):
    s.setdefault("events", []).append({"t": datetime.datetime.now().isoformat(timespec="seconds"), "kind": kind, "text": text})
    s["events"] = s["events"][-100:]

# ---------------- GBrain writer (one process at a time, never blocks HTTP) ----------------
GQ = queue.Queue()
def gbrain(args, tries=3):
    env = dict(os.environ); env["PATH"] = "/home/ubuntu/.bun/bin:" + env.get("PATH", "")
    for i in range(tries):
        try:
            p = subprocess.run(["gbrain"] + args, cwd=HACK, env=env, capture_output=True, text=True, timeout=90)
            with open(os.path.join(OUT, "gbrain.log"), "a") as lg:
                lg.write(f"{datetime.datetime.now():%H:%M:%S} rc={p.returncode} gbrain {' '.join(a[:80] for a in args)}\n{(p.stdout+p.stderr)[-400:]}\n")
            if p.returncode == 0: return True
        except Exception as e:
            with open(os.path.join(OUT, "gbrain.log"), "a") as lg: lg.write(f"ERR {e}\n")
        time.sleep(2 + i * 2)
    return False

def gbrain_worker():
    while True:
        args = GQ.get()
        try: gbrain(args)
        finally: GQ.task_done()

def enqueue_answer_writes(dec, verdict, note):
    fact = f"Raphael answered '{verdict}' on a {dec['kind']} card: {dec['title'][:140]}" + (f". Note: {note}" if note else "")
    GQ.put(["call", "remember", json.dumps({"fact": fact, "provenance": f"cos answer {dec['id']} {TODAY}", "kind": "preference"})])
    status = "done" if verdict == "done" else "skipped"
    raw = dec["raw"]
    raw = re.sub(r'^status: ".*"$', f'status: "{status}"', raw, count=1, flags=re.M)
    raw = re.sub(r'^done_by: ".*"$', 'done_by: "him"', raw, count=1, flags=re.M)
    raw = raw.replace('"open"]', f'"{status}"]')
    raw = re.sub(r"\*\*Outcome: open\*\*.*", f"**Outcome: {status}** (by him via cos, updated {TODAY})" + (f"\nNote: {note}" if note else ""), raw)
    GQ.put(["put", f"decisions/{dec['id']}", "--content", raw, "--force"])

# ---------------- LLM ----------------
def claude(prompt, timeout=90):
    try:
        p = subprocess.run(["claude", "-p", "--model", "claude-sonnet-5"], input=prompt, capture_output=True, text=True, timeout=timeout, cwd=OUT)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None

# ---------------- brief ----------------
class Brain:
    def __init__(self):
        self.decs = load_decisions()
        self.by_id = {d["id"]: d for d in self.decs}
        for d in self.decs: d["goal"] = goal_of(d)

    def score(self, d, w):
        s = (4 - d["prio"]) * 10
        try:
            days = (datetime.date.fromisoformat(d["expires"]) - TODAY).days
            s += max(0, 12 - 3 * max(days, 0))
        except Exception: pass
        s += w.get("kind:" + d["kind"], 0)
        if d["author"]: s += w.get("author:" + d["author"].lower(), 0)
        s += w.get("goal:" + d["goal"], 0)
        for k in keywords(d): s += w.get("kw:" + k, 0)
        return s

    def cards(self, s):
        answered = {a["id"] for a in s["answers"]}
        w = s["weights"]; out = []
        for d in self.decs:
            if d["status"] != "open" or d["kind"] not in CARD_KINDS or d["id"] in answered or private(d): continue
            try:
                if datetime.date.fromisoformat(d["expires"]) < TODAY: continue
            except Exception: pass
            out.append((self.score(d, w), d))
        out.sort(key=lambda x: (-x[0], x[1]["expires"], x[1]["id"]))
        return out

    def card_json(self, sc, d):
        gt = next(g["title"] for g in GOALS if g["id"] == d["goal"])
        why = REDACT.sub("", d["why"]); why = why if len(why) < 170 else why[:167].rsplit(" ", 1)[0] + "..."
        rec = d["rec"]; rec = rec if len(rec) < 130 else rec[:127].rsplit(" ", 1)[0] + "..."
        days = None
        try: days = (datetime.date.fromisoformat(d["expires"]) - TODAY).days
        except Exception: pass
        return {"id": d["id"], "title": d["title"], "kind": d["kind"], "why": why, "recommendation": rec or "Your call",
                "default": "" if d["default"] and d["default"] == d["rec"] else ((d["default"][:120] + ("..." if len(d["default"]) > 120 else "")) or "It waits"), "expires": d["expires"], "days_left": days, "goal": d["goal"],
                "goal_title": gt, "score": sc, "link": d["link"], "author": d["author"]}

    def goals(self, s):
        since = TODAY - datetime.timedelta(days=14)
        answered = {a["id"]: a["verdict"] for a in s["answers"]}
        ev = {g["id"]: [0, 0] for g in GOALS}
        for d in self.decs:
            if d["kind"] == "people" or d["done_by"] == "system" and d["status"] == "expired" and d["kind"] == "handled": continue
            try: dt = datetime.date.fromisoformat(d["date"])
            except Exception: continue
            st = d["status"]
            if d["id"] in answered: st = "done" if answered[d["id"]] == "done" else "skipped"
            if dt < since: continue
            if st == "done" and d["done_by"] in ("him", "assistant", "") or d["id"] in answered and st == "done": ev[d["goal"]][0] += 1
            elif st in ("skipped", "expired"): ev[d["goal"]][1] += 1
        cards = self.cards(s); out = []
        for g in GOALS:
            done, miss = ev[g["id"]]; tot = done + miss
            pct = round(100 * done / tot) if tot else 0
            status = "on-track" if tot and pct >= 45 else ("drifting" if tot and pct >= 20 else "stalled")
            status = s.get("goal_status", {}).get(g["id"], status)
            nxt = next((d for sc, d in cards if d["goal"] == g["id"]), None)
            move = (nxt["title"][:90] + ("..." if len(nxt["title"]) > 90 else "")) if nxt else NEXT_MOVE[g["id"]]
            out.append({"id": g["id"], "title": g["title"], "status": status, "progress": pct, "done": done, "missed": miss,
                        "next_move": move, "next_id": nxt["id"] if nxt else None})
        gd = os.path.join(SEED, "goals")
        for f in sorted(os.listdir(gd)) if os.path.isdir(gd) else []:
            fm, body, raw = parse_page(os.path.join(gd, f))
            if "(QM chat)" in raw and "smoke" not in raw.lower():
                out.insert(0, {"id": f[:-3], "title": fm.get("title", f[:-3])[:60], "status": "new", "progress": 0, "done": 0, "missed": 0,
                               "next_move": "from your interview, saved in GBrain", "next_id": None})
        return out

    def handled(self):
        items = [d for d in self.decs if (d["done_by"] == "system" or d["status"] == "expired") and not private(d)]
        items.sort(key=lambda d: d["date"], reverse=True)
        n_all = sum(1 for d in self.decs if d["done_by"] == "system" or d["status"] == "expired")
        return {"count": n_all, "latest": [{"id": d["id"], "title": REDACT.sub("", d["title"])[:110], "date": d["date"], "status": d["status"]} for d in items[:5]]}

    def opportunities(self, s):
        answered = {a["id"] for a in s["answers"]}
        ops = [d for d in self.decs if d["kind"] == "opportunity" and d["status"] == "open" and d["id"] not in answered and not private(d)]
        ops.sort(key=lambda d: d["expires"])
        return [{"id": d["id"], "title": d["title"][:140], "expires": d["expires"], "created": d["created"], "link": d["link"],
                 "days_left": (datetime.date.fromisoformat(d["expires"]) - TODAY).days if d["expires"] else None} for d in ops]

    def fallback_ideas(self):
        stale_people = sum(1 for d in self.decs if d["kind"] == "people" and d["status"] == "open")
        skipped_opp = [d for d in self.decs if d["kind"] == "opportunity" and d["status"] in ("skipped", "expired")]
        post_skipped = sum(1 for d in self.decs if d["kind"] == "post" and d["status"] == "skipped")
        post_total = sum(1 for d in self.decs if d["kind"] == "post")
        return [
            {"title": "Turn one finished research folder into a post", "why": f"{post_skipped} of {post_total} reply-post cards were skipped; your own findings post better than replies to others.",
             "first_step": "Pick the research folder with the most findings and draft 5 lines from it.", "goal": "Be known for AI agents"},
            {"title": f"Clear {stale_people} stale follow-ups in one 30-minute block", "why": "Relationships are the SF goal's metric, and these threads go cold while they wait.",
             "first_step": "Sort follow-ups by last touch; send the three oldest today.", "goal": "Deep ties in the SF AI scene"},
            {"title": "Put recurring events on a watch, not a card", "why": f"{len(skipped_opp)} opportunity cards were skipped or expired; many repeat every month.",
             "first_step": "List the organisers behind them and subscribe to their next date.", "goal": "Contribute at top AI venues"},
        ]

BR = None
def brief_json():
    with LOCK:
        s = load_state()
        cards = BR.cards(s)
        strip = [BR.card_json(sc, d) for sc, d in cards[:4]]
        queue_ = [BR.card_json(sc, d) for sc, d in cards[4:10]]
        return {"date": TODAY.isoformat(), "demo": DEMO, "strip": strip, "queue": queue_, "open_count": len(cards),
                "goals": BR.goals(s), "ideas": s.get("ideas") or BR.fallback_ideas(), "ideas_source": s.get("ideas_source", "rules"),
                "opportunities": BR.opportunities(s), "handled": BR.handled(), "rules": s["rules"], "weights": s["weights"],
                "answers": s["answers"][-20:], "events": s.get("events", [])[-10:], "gbrain_queue": GQ.qsize()}

def gen_ideas(force=False):
    s = load_state()
    if s.get("ideas") and not force: return s["ideas"]
    try: skill = open(os.path.join(ROOT, "skills", "originate", "SKILL.md")).read()[:4000]
    except Exception: skill = ""
    goals = "; ".join(g["title"] for g in GOALS)
    projects = ", ".join(f[:-3] for f in sorted(os.listdir(os.path.join(SEED, "projects"))) if f.endswith(".md") and "immigration" not in f)
    kinds = collections.Counter((d["kind"], d["status"]) for d in BR.decs if d["kind"] != "people")
    stale = [d["title"][:90] for d in BR.decs if d["status"] == "expired" and not private(d)][:8]
    proj = []
    for f in sorted(os.listdir(os.path.join(SEED, "projects"))):
        if not f.endswith(".md") or "immigration" in f: continue
        body = parse_page(os.path.join(SEED, "projects", f))[1]
        body = " ".join(l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#"))
        if not SENSITIVE.search(body[:400]): proj.append(f"{f[:-3]}: {body[:400]}")
    projects = " | ".join(proj)
    prompt = (f"{skill}\n\nYou are the Chief of Staff. Card kinds: post = a suggested reply to someone else's X post (not his draft); decide = a decision; "
              f"opportunity = event/CFP/role; people = follow-up. Goals: {goals}. Projects (what he owns): {projects}. Card history counts (kind,status): "
              f"{dict(kinds)}. Recently expired items: {stale}.\nBring exactly 3 ideas he did not ask for, from what he already owns and is not using. "
              "Never mention health, immigration, family, money amounts or private people. Answer ONLY a JSON array of 3 objects with keys "
              "title (<= 9 words), why (<= 25 words, one concrete number from the data), first_step (<= 15 words), goal (one of the goal titles).")
    out = claude(prompt, timeout=150)
    open(os.path.join(OUT, "ideas_raw.txt"), "w").write(out or "(no output)")
    ideas = None
    if out:
        m = re.search(r"\[.*\]", out, re.S)
        try:
            ideas = json.loads(m.group(0)) if m else None
            ideas = [i for i in ideas if not SENSITIVE.search(json.dumps(i))][:3]
            if len(ideas) < 3: ideas = None
        except Exception: ideas = None
    with LOCK:
        s = load_state()
        s["ideas"] = ideas or BR.fallback_ideas(); s["ideas_source"] = "claude-sonnet-5" if ideas else "rules"
        event(s, "ideas", f"3 ideas from {s['ideas_source']}"); save_state(s)
    return s["ideas"]

def answer(i, verdict, note=""):
    if verdict not in ("done", "skip"): raise ValueError("verdict must be done or skip")
    d = BR.by_id.get(i)
    if not d: raise KeyError(i)
    with LOCK:
        s = load_state()
        before = [x["id"] for x in brief_json()["strip"]]
        s["answers"] = [a for a in s["answers"] if a["id"] != i]
        s["answers"].append({"id": i, "verdict": verdict, "note": note, "kind": d["kind"], "author": d["author"], "goal": d["goal"],
                             "title": d["title"][:120], "t": datetime.datetime.now().isoformat(timespec="seconds")})
        event(s, "answer", f"{verdict} {i}"); save_state(s)
    enqueue_answer_writes(d, verdict, note)
    b = brief_json(); b["moved_up"] = [x["title"] for x in b["strip"] if x["id"] not in before]
    return b

def reflect():
    with LOCK:
        s = load_state()
        _b = brief_json(); before = [x["id"] for x in _b["strip"] + _b["queue"]]
        need = 2 if DEMO else 3
        groups = collections.defaultdict(list)
        for a in s["answers"]:
            groups[("kind", a["kind"], a["verdict"])].append(a)
            if a.get("author"): groups[("author", a["author"].lower(), a["verdict"])].append(a)
            for w in set(re.findall(r"[a-z][a-z0-9-]{3,}", (a.get("note") or "").lower())) - STOP:
                groups[("note", w, a["verdict"])].append(a)
        have = {r["key"] for r in s["rules"]}
        new = []
        for (gtype, val, verdict), items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if len(items) < need: continue
            key = f"{gtype}:{val}:{verdict}"
            if key in have: continue
            ev_ids = [a["id"] for a in items][-3:]
            delta = -15 if verdict == "skip" else 10
            notes = [a["note"] for a in items if a.get("note")]
            if gtype == "kind":
                label = {"post": "reply-to-post cards", "decide": "decision cards", "opportunity": "opportunity cards", "learn": "learning cards"}.get(val, val + " cards")
                text = (f"Rank {label} lower: you skipped {len(items)} in a row" if verdict == "skip" else f"Rank {label} higher: you acted on {len(items)}") + (f" ('{notes[-1]}')" if notes else "") + "."
                wkey = "kind:" + val
            elif gtype == "author":
                text = (f"Rank posts by @{val} lower" if verdict == "skip" else f"Bring posts by @{val} first") + f": {len(items)} answers agree."
                wkey = "author:" + val
            else:
                if gtype == "note" and any(r["key"].startswith("kind:") and r["verdict"] == verdict for r in s["rules"] + new) and len(items) < 3: continue
                text = f"Cards like '{val}' get {'skipped' if verdict == 'skip' else 'done'}: {len(items)} of your notes say so."
                wkey = "kw:" + val
            rule = {"key": key, "text": text, "evidence": ev_ids, "weight": {wkey: delta}, "verdict": verdict,
                    "created": datetime.datetime.now().isoformat(timespec="seconds"), "source": "template"}
            new.append(rule)
            if len(new) >= 2: break
        for r in new:
            s["rules"].append(r)
            for k, v in r["weight"].items(): s["weights"][k] = s["weights"].get(k, 0) + v
            event(s, "rule", r["text"])
        save_state(s)
        write_skill_rules(s)
    for r in new:
        GQ.put(["call", "remember", json.dumps({"fact": "Learned rule: " + r["text"], "provenance": f"cos reflect {TODAY} evidence {' '.join(r['evidence'])}", "kind": "preference"})])
        threading.Thread(target=rephrase, args=(r["key"],), daemon=True).start()
    b = brief_json(); b["new_rules"] = new
    after = [x["id"] for x in b["strip"] + b["queue"]]
    b["moved_up"] = [BR.by_id[i]["title"] for n, i in enumerate(after) if i not in before or before.index(i) > n]
    b["moved_down"] = [BR.by_id[i]["title"] for n, i in enumerate(before) if i not in after or after.index(i) > n]
    return b

def rephrase(key):
    with LOCK:
        s = load_state(); r = next((x for x in s["rules"] if x["key"] == key), None)
    if not r: return
    titles = [BR.by_id[i]["title"][:100] for i in r["evidence"] if i in BR.by_id]
    out = claude("Rewrite this learned ranking rule for a chief-of-staff brief as ONE plain-English imperative sentence, max 18 words, "
                 f"no names of private people. Rule: {r['text']} Evidence cards: {titles}. Answer with the sentence only.", timeout=60)
    if out and len(out) < 200 and not SENSITIVE.search(out):
        with LOCK:
            s = load_state()
            for x in s["rules"]:
                if x["key"] == key: x["text"] = out.strip().strip('"'); x["source"] = "claude-sonnet-5"
            save_state(s); write_skill_rules(s)

def write_skill_rules(s):
    try: t = open(SKILL_BRIEF, encoding="utf-8").read()
    except Exception: return
    head = t.split("\n## Learned rules")[0].rstrip()
    lines = ["", "", "## Learned rules", "", "Written by `cos reflect` from his answers. Each rule carries its evidence (decision ids); the ranking weight is in `out/state.json`.", ""]
    for r in s["rules"]:
        lines.append(f"- {r['text']} (evidence: {', '.join(r['evidence'])}; weight {json.dumps(r['weight'])}; {r['created'][:10]})")
    open(SKILL_BRIEF, "w", encoding="utf-8").write(head + "\n".join(lines) + "\n")

# ---------------- HTTP ----------------
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else (json.dumps(body) if not isinstance(body, str) else body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)
    def local_only(self):
        ip = self.client_address[0]
        if not (ip.startswith("127.") or ip.startswith("172.")):
            self.send(403, {"error": "local only"}); return False
        return True
    def do_GET(self):
        if not self.local_only(): return
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"): return self.send(200, open(os.path.join(WEB, "index.html"), "rb").read(), "text/html")
        if p == "/api/brief": return self.send(200, brief_json())
        if p == "/api/events": return self.send(200, load_state().get("events", [])[-50:])
        if p == "/api/health": return self.send(200, {"ok": True, "gbrain_queue": GQ.qsize()})
        self.send(404, {"error": "not found"})
    def do_POST(self):
        if not self.local_only(): return
        p = self.path.split("?")[0]
        n = int(self.headers.get("Content-Length") or 0)
        try: body = json.loads(self.rfile.read(n) or b"{}")
        except Exception: body = {}
        try:
            if p == "/api/answer": return self.send(200, answer(body.get("id", ""), body.get("verdict", ""), body.get("note", "")))
            if p == "/api/reflect": return self.send(200, reflect())
            if p == "/api/capture": return self.send(200, capture(body))
            if p == "/api/reset":
                global BR
                if sync_from_gbrain(): BR = Brain()
                with LOCK:
                    s = load_state(); ideas = s.get("ideas"); src = s.get("ideas_source")
                    s = {"answers": [], "weights": {}, "rules": [], "ideas": ideas, "ideas_source": src, "goal_status": {}, "events": []}
                    save_state(s); write_skill_rules(s)
                return self.send(200, brief_json())
        except (KeyError, ValueError) as e:
            return self.send(400, {"error": str(e)})
        self.send(404, {"error": "not found"})

def capture(body):
    """Interview answers from the QM sandbox: a goal or unknown page plus a remembered fact, both with provenance."""
    kind = body.get("type", "fact"); title = (body.get("title") or "").strip()[:120]; text = (body.get("body") or "").strip()[:2000]
    if not (title or text): raise ValueError("title or body required")
    prov = f"interview {TODAY.isoformat()} (QM chat)"
    if kind in ("goal", "unknown", "constraint", "asset"):
        slug = f"{'goals' if kind == 'goal' else 'unknowns'}/" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        page = f"---\ntitle: {json.dumps(title)}\ntype: {'goal' if kind == 'goal' else 'note'}\ntags: [\"interview\", \"{kind}\"]\n---\n\n{text}\n\nSource: {prov}\n"
        GQ.put(["put", slug, "--content", page, "--force"])
    GQ.put(["call", "remember", json.dumps({"fact": f"{kind}: {title}. {text}"[:900], "provenance": prov, "kind": "fact"})])
    with LOCK:
        s = load_state(); s.setdefault("captured", []).append({"type": kind, "title": title, "body": text, "at": datetime.datetime.now().isoformat(timespec="seconds")})
        event(s, "capture", f"interview saved a {kind}: {title}"); save_state(s)
    return {"ok": True, "saved": kind, "title": title}

def serve(port=8790):
    threading.Thread(target=gbrain_worker, daemon=True).start()
    if not load_state().get("ideas") or load_state().get("ideas_source") == "rules":
        threading.Thread(target=gen_ideas, kwargs={"force": True}, daemon=True).start()
    srv = ThreadingHTTPServer((os.environ.get("COS_HOST", "127.0.0.1"), port), H)
    print(f"cos serving http://127.0.0.1:{port}", flush=True)
    srv.serve_forever()

def main(argv):
    global BR
    sync_from_gbrain()
    BR = Brain()
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "serve": return serve(int(os.environ.get("COS_PORT", 8790)))
    if cmd == "run":
        if "--ideas" in argv: gen_ideas(force=True)
        b = brief_json(); json.dump(b, open(os.path.join(OUT, "brief.json"), "w"), indent=1)
        print(f"Brief for {b['date']}  ({b['open_count']} open cards)\nOnly you can do today:")
        for c in b["strip"]: print(f"  [{c['id']}] {c['kind']:<11} score {c['score']:>3}  {c['title'][:90]}")
        print("Goals:"); [print(f"  {g['status']:<9} {g['progress']:>3}%  {g['title']}") for g in b["goals"]]
        print("Ideas (" + b["ideas_source"] + "):"); [print("  - " + i["title"]) for i in b["ideas"]]
        print(f"Handled without you: {b['handled']['count']}"); print(f"Rules: {len(b['rules'])}")
        return
    if cmd == "answer":
        i, v = argv[2], argv[3]; note = argv[argv.index("--note") + 1] if "--note" in argv else ""
        threading.Thread(target=gbrain_worker, daemon=True).start()
        b = answer(i, v, note); print(json.dumps([(c["id"], c["title"][:60]) for c in b["strip"]], indent=1))
        GQ.join(); return
    if cmd == "reflect":
        threading.Thread(target=gbrain_worker, daemon=True).start()
        b = reflect(); print(json.dumps([r["text"] for r in b["new_rules"]], indent=1)); GQ.join(); return
    if cmd == "reset":
        s = {"answers": [], "weights": {}, "rules": [], "ideas": load_state().get("ideas"), "goal_status": {}, "events": []}
        save_state(s); write_skill_rules(s); print("reset"); return
    print("usage: cos.py [run [--ideas] | serve | answer <id> done|skip [--note ...] | reflect | reset]")

if __name__ == "__main__":
    main(sys.argv)
