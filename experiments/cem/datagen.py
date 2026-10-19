"""Synthetic "memory stream" benchmark with exact ground truth.

An episode simulates months of Hermes Agent sessions. Each session leaves a
small dated note file (the "large pile of memory files"). Facts about
projects/hosts/teams are introduced, changed, given scoped exceptions,
restated, and mixed with distractor notes. Every value token is unique inside
an episode, so any wrong answer can be traced to its source (stale version,
other scope, other attribute, other entity, or fabricated).
"""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta

ENTITY_NAMES = [
    "Orion", "Vega", "Lyra", "Atlas", "Nimbus", "Cobalt", "Falcon", "Juniper", "Kestrel",
    "Marlin", "Nova", "Onyx", "Pegasus", "Quartz", "Raven", "Sierra", "Tundra", "Umbra",
    "Vortex", "Willow", "Xenon", "Yarrow", "Zephyr", "Aurora", "Basalt", "Cedar", "Dune",
    "Ember", "Fjord", "Garnet", "Helix", "Indigo", "Jasper", "Krypton", "Lumen", "Magma",
    "Nectar", "Opal", "Prism", "Quill", "Rune", "Saffron", "Topaz", "Velvet", "Wren",
    "Zircon", "Alder", "Birch", "Comet", "Delta", "Echo", "Flint", "Glacier", "Harbor",
    "Iris", "Jade", "Lotus", "Maple", "Nordic", "Oasis", "Pulsar", "Quasar", "Redwood",
    "Solstice", "Thistle", "Ursa", "Vesper", "Wildfire", "Yukon", "Zenith", "Acacia", "Bramble",
]

# kind -> (display noun, attribute pool, scope pool)
ENTITY_KINDS = {
    "service": ("service", [
        ("API port", "port"), ("deploy branch", "branch"), ("request timeout", "ms"),
        ("worker count", "count"), ("log retention", "days"), ("max upload size", "mb"),
        ("nightly backup time", "time"), ("DB pool size", "count"),
    ], ["staging", "the EU region", "the canary cluster", "batch jobs", "the mobile API"]),
    "host": ("host", [
        ("IP address", "ip"), ("SSH port", "port"), ("disk quota", "gb"),
        ("maintenance window", "time"), ("swap size", "gb"), ("max containers", "count"),
    ], ["the GPU queue", "weekend runs", "the CI runner", "the backup job"]),
    "team": ("team", [
        ("max line length", "chars"), ("stand-up time", "time"), ("code review SLA", "hours"),
        ("test coverage threshold", "pct"), ("monthly cloud budget", "usd"), ("build cache size", "gb"),
    ], ["the frontend squad", "hotfix branches", "the intern cohort", "Fridays"]),
}

INIT_T = [
    "{E} {a} is {v}.",
    "{E} uses {v} as its {a}.",
    "For {E}, the {a} is set to {v}.",
    "Noted: {E} — {a}: {v}.",
    "The {a} of {E} is {v}.",
    "Learned that the {E} {kind} runs with {a} {v}.",
]
INIT2_T = [
    "{E} {a} is {v} and its {a2} is {v2}.",
    "The {E} {kind} uses {a} {v}; {a2} is {v2}.",
    "Set up {E}: {a} {v}, {a2} {v2}.",
]
UPD_OLD_T = [
    "{E} {a} changed from {old} to {v}.",
    "Update: {E} moved its {a} from {old} to {v}.",
    "The {a} for {E} is no longer {old}; it is now {v}.",
]
UPD_NEW_T = [
    "{E} now uses {v} as its {a}.",
    "As of today, the {a} for {E} is {v}.",
    "{E}'s {a} has been updated to {v}.",
    "User switched {E} to {a} {v}.",
]
EXC_T = [
    "Exception: for {s}, {E} uses {a} {v}.",
    "{E} {a} is {v} on {s} only; elsewhere the normal setting applies.",
    "Note that {s} of {E} overrides the {a} with {v}.",
    "Except for {s}, where it is {v}, {E} keeps its usual {a}.",
    "Special case — {E} on {s}: {a} {v}.",
]
REST_T = [
    "Reminder: {E} {a} is still {v}.",
    "Confirmed again that {E} uses {a} {v}.",
    "Double-checked {E}: the {a} remains {v}.",
]
DISTRACTORS = [
    "User prefers concise answers with code blocks.",
    "Run 'make test' before pushing any branch.",
    "The user is based in Seoul (KST, UTC+9).",
    "User dislikes emoji in commit messages.",
    "Docker commands do not need sudo on this machine.",
    "Use ruff for linting Python code in all repos.",
    "User likes summaries at the end of long answers.",
    "Prefer pnpm over npm for JavaScript projects.",
    "The user reads documentation in English but chats in Korean.",
    "Large log files should be summarized, not pasted.",
    "User wants dates written as YYYY-MM-DD.",
    "Avoid force-pushing to shared branches.",
    "User usually works late in the evening.",
    "Screenshots go to ~/Pictures/shots by default.",
    "Prefer small pull requests with clear titles.",
]

ABSTAIN_ATTRS = {"service": ["cache TTL", "rate limit", "TLS certificate expiry"],
                 "host": ["kernel version", "GPU count", "rack location"],
                 "team": ["retro day", "budget code", "design review time"]}


@dataclass
class Fact:
    entity: str
    attr: str
    scope: str           # "default" or a scope phrase
    value: str           # display value, e.g. "450 ms"
    core: str            # unique token used for matching, e.g. "450"
    t: int               # global note index (time order)
    session: int
    kind: str            # init / update / exception / restate


@dataclass
class Note:
    idx: int
    session: int
    date: str
    text: str
    facts: list[int] = field(default_factory=list)   # indices into Episode.facts


@dataclass
class Question:
    qid: str
    qtype: str           # CUR / STABLE / PREV / EXC / ABSTAIN
    entity: str
    attr: str
    scope: str
    text: str
    gold: str            # core token or "unknown"
    gold_display: str
    has_exception: bool = False
    has_update: bool = False
    family: str = "base"


@dataclass
class Episode:
    seed: int
    n_entities: int
    notes: list[Note]
    facts: list[Fact]
    questions: list[Question]
    sessions: list[dict]

    def raw_text(self) -> str:
        return "\n\n".join(render_session(s, self.notes) for s in self.sessions)

    def to_json(self) -> str:
        return json.dumps({"seed": self.seed, "n_entities": self.n_entities,
                           "notes": [asdict(n) for n in self.notes],
                           "facts": [asdict(f) for f in self.facts],
                           "questions": [asdict(q) for q in self.questions],
                           "sessions": self.sessions}, ensure_ascii=False, indent=1)

    @staticmethod
    def from_json(s: str) -> "Episode":
        d = json.loads(s)
        return Episode(d["seed"], d["n_entities"], [Note(**n) for n in d["notes"]],
                       [Fact(**f) for f in d["facts"]], [Question(**q) for q in d["questions"]],
                       d["sessions"])


def render_session(sess: dict, notes: list[Note]) -> str:
    body = "\n".join(f"- {notes[i].text}" for i in sess["notes"])
    return f"## memory/{sess['date']}.md\n{body}"


class ValueGen:
    """Generates values whose numeric core is unique within an episode."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.used: set[str] = set()

    def _uniq(self, make):
        for _ in range(10000):
            disp, core = make()
            bare = core.split("-")[-1]          # "release-935" also blocks "935"
            if core not in self.used and bare not in self.used:
                self.used.update({core, bare})
                return disp, core
        raise RuntimeError("value space exhausted")

    def new(self, vtype: str) -> tuple[str, str]:
        r = self.rng
        makers = {
            "port": lambda: (str(v := r.randint(2000, 9899)), str(v)),
            "branch": lambda: (f"release-{(v := r.randint(100, 999))}", f"release-{v}"),
            "ms": lambda: (f"{(v := r.randrange(150, 9950, 50))} ms", str(v)),
            "count": lambda: (str(v := r.randint(6, 480)), str(v)),
            "days": lambda: (f"{(v := r.randint(7, 400))} days", str(v)),
            "mb": lambda: (f"{(v := r.randrange(16, 4096, 8))} MB", str(v)),
            "gb": lambda: (f"{(v := r.randint(20, 3000))} GB", str(v)),
            "time": lambda: (v := f"{r.randint(10, 23)}:{r.choice(['05','10','15','20','25','35','40','45','50','55'])}", v),
            "ip": lambda: (v := f"10.{r.randint(1, 254)}.{r.randint(1, 254)}.{r.randint(2, 254)}", v),
            "chars": lambda: (f"{(v := r.randint(72, 240))} chars", str(v)),
            "hours": lambda: (f"{(v := r.randint(2, 96))} hours", str(v)),
            "pct": lambda: (f"{(v := r.randint(41, 99))}%", str(v)),
            "usd": lambda: (f"${(v := r.randrange(500, 9990, 10))}", str(v)),
        }
        return self._uniq(makers[vtype])


# Attribute synonyms used in some notes and some questions (schema-breaking paraphrase).
ATTR_SYN = {
    "API port": ["listen port", "HTTP port"], "deploy branch": ["release branch", "branch it ships from"],
    "request timeout": ["timeout for requests", "HTTP timeout"], "worker count": ["number of workers", "worker pool size"],
    "log retention": ["log retention period", "how long logs are kept"], "max upload size": ["upload limit", "maximum upload"],
    "nightly backup time": ["backup start time", "time of the nightly backup"], "DB pool size": ["database pool size", "DB connection pool"],
    "IP address": ["IP", "address"], "SSH port": ["port for SSH", "sshd port"], "disk quota": ["disk limit", "storage quota"],
    "maintenance window": ["maintenance start time", "maintenance slot"], "swap size": ["swap", "swap space"],
    "max containers": ["container limit", "maximum number of containers"],
    "max line length": ["line-length limit", "maximum line width"], "stand-up time": ["daily stand-up", "time of the stand-up"],
    "code review SLA": ["review turnaround target", "code-review deadline"], "test coverage threshold": ["coverage gate", "minimum test coverage"],
    "monthly cloud budget": ["cloud spending cap", "monthly cloud spend limit"], "build cache size": ["build cache", "size of the build cache"],
}
REJ_T = [
    "Considered changing {E} {a} to {x}, but decided to keep {v}.",
    "Proposal to move {E} to {a} {x} was rejected; it stays {v}.",
    "Tried {a} {x} on {E} for a test, reverted immediately; {v} remains the setting.",
]
REV_T = [
    "Rolled back the {a} change on {E}; it is {old} again.",
    "{E} {a} reverted to {old} after problems with {v}.",
]
NOTE_T = [  # free-form lessons with a unique code value; asked as NOTE questions
    ("Lesson learned: the office VPN only works with MTU {v}.", "Which MTU does the office VPN need?"),
    ("The flaky integration test passes reliably with a retry delay of {v} ms.", "What retry delay makes the flaky integration test pass (in ms)?"),
    ("Docker builds on the laptop need --memory={v}m to avoid OOM kills.", "What --memory value (in MB) do laptop Docker builds need?"),
    ("The shared lab printer is in room {v}.", "Which room is the shared lab printer in?"),
    ("Grafana dashboard #{v} is the one with the cluster health overview.", "Which Grafana dashboard number shows the cluster health overview?"),
    ("The license server answers on port {v}.", "On which port does the license server answer?"),
    ("Jira tickets for infra work go to board {v}.", "Which Jira board number do infra tickets go to?"),
    ("The GPU node pool autoscaler caps at {v} nodes.", "At how many nodes does the GPU node pool autoscaler cap?"),
]
EXC_Q_T = ["What {a} does {E} use for {s}?", "For {s}, what is {E}'s {a}?"]
CUR_Q_T = ["What is the current default {a} of {E}?", "What is {E}'s {a} right now (default setting)?"]
PREV_Q_T = ["What was the default {a} of {E} right before its most recent change?",
            "Before the latest change, what was {E}'s default {a}?"]
INIT_T += ["{E}: {a} = {v}.", "Config for {E} has {a} {v}."]
UPD_NEW_T += ["New {a} for {E}: {v}."]
REST_T += ["{E} {a}: {v} (unchanged).", "Checked {E} again: {a} is {v}."]


def generate_episode(seed: int, n_entities: int = 24, p_update: float = 0.5,
                     p_second_update: float = 0.25, p_exception: float = 0.35,
                     p_restate: float = 0.3, n_attrs: int = 3, distractor_frac: float = 0.08,
                     notes_per_session: tuple[int, int] = (3, 6), n_abstain: int | None = None,
                     p_synonym: float = 0.3, p_rejected: float = 0.12, p_revert: float = 0.25,
                     n_note: int | None = None, n_excneg: int | None = None) -> Episode:
    rng = random.Random(seed)
    vg = ValueGen(rng)
    names = rng.sample(ENTITY_NAMES, n_entities)
    kinds = [rng.choices(list(ENTITY_KINDS), weights=[0.5, 0.25, 0.25])[0] for _ in names]

    def an(k):  # attribute name as written in a note (sometimes a synonym)
        if rng.random() < p_synonym:
            k["syn"] = True
            return rng.choice(ATTR_SYN[k["attr"]])
        return k["attr"]

    events: list[tuple[float, str, dict]] = []
    keys = []
    for e, kind in zip(names, kinds):
        noun, pool, scopes = ENTITY_KINDS[kind]
        attrs = rng.sample(pool, n_attrs)
        t_intro = rng.uniform(0.0, 0.45)
        paired = rng.random() < 0.35
        for j, (a, vtype) in enumerate(attrs):
            key = dict(entity=e, kind=kind, attr=a, vtype=vtype, versions=[vg.new(vtype)], exc=None,
                       syn=False, rej=False, rev=False)
            keys.append(key)
            key["t0"] = t_intro + (0.0 if (paired and j < 2) else rng.uniform(0.0, 0.15))
        if paired:
            k1, k2 = keys[-n_attrs], keys[-n_attrs + 1]
            events.append((k1["t0"], "init2", dict(k1=k1, k2=k2)))
            rest = keys[-n_attrs + 2:]
        else:
            rest = keys[-n_attrs:]
        for k in rest:
            events.append((k["t0"], "init", dict(k=k)))

    for k in keys:
        t_last = k["t0"]
        if rng.random() < p_update:
            n_up = 2 if rng.random() < p_second_update else 1
            for u in range(n_up):
                t_up = rng.uniform(t_last + 0.02, min(1.0, t_last + 0.5))
                if u == 1 and rng.random() < p_revert:      # second change = rollback to the older value
                    k["versions"].append(k["versions"][-2])
                    k["rev"] = True
                    events.append((t_up, "revert", dict(k=k, vi=len(k["versions"]) - 1)))
                else:
                    k["versions"].append(vg.new(k["vtype"]))
                    events.append((t_up, "update", dict(k=k, vi=len(k["versions"]) - 1)))
                t_last = t_up
        if rng.random() < p_rejected:                        # considered-but-rejected value
            k["rej"] = True
            events.append((rng.uniform(t_last + 0.01, min(1.0, t_last + 0.4)), "rejected",
                           dict(k=k, x=vg.new(k["vtype"]))))
        if rng.random() < p_exception:
            scope = rng.choice(ENTITY_KINDS[k["kind"]][2])
            k["exc"] = (scope, vg.new(k["vtype"]))
            events.append((rng.uniform(k["t0"] + 0.01, 1.0), "exception", dict(k=k)))
        if rng.random() < p_restate:
            events.append((rng.uniform(k["t0"] + 0.01, 1.0), "restate", dict(k=k)))

    n_note = n_note if n_note is not None else max(3, n_entities // 6)
    note_items = []
    for tmpl, qtext in rng.sample(NOTE_T, min(n_note, len(NOTE_T))):
        v = vg.new("count" if "nodes" in tmpl else "port")
        note_items.append((tmpl, qtext, v))
        events.append((rng.uniform(0, 1), "note", dict(tmpl=tmpl, v=v)))
    n_distr = max(1, int(distractor_frac * len(events)))
    for _ in range(n_distr):
        events.append((rng.uniform(0, 1), "distractor", dict(text=rng.choice(DISTRACTORS))))
    events.sort(key=lambda x: x[0])

    notes: list[Note] = []
    facts: list[Fact] = []
    current_vi: dict[int, int] = {}

    def add_fact(k, scope, disp, core, t, kind):
        facts.append(Fact(k["entity"], k["attr"], scope, disp, core, t, -1, kind))
        return len(facts) - 1

    for t_key, ev, p in events:
        idx = len(notes)
        fidx: list[int] = []
        if ev == "init":
            k = p["k"]
            disp, core = k["versions"][0]
            text = rng.choice(INIT_T).format(E=k["entity"], a=an(k), v=disp, kind=ENTITY_KINDS[k["kind"]][0])
            fidx.append(add_fact(k, "default", disp, core, idx, "init"))
            current_vi[id(k)] = 0
        elif ev == "init2":
            k1, k2 = p["k1"], p["k2"]
            (d1, c1), (d2, c2) = k1["versions"][0], k2["versions"][0]
            text = rng.choice(INIT2_T).format(E=k1["entity"], a=an(k1), v=d1, a2=an(k2), v2=d2,
                                              kind=ENTITY_KINDS[k1["kind"]][0])
            fidx += [add_fact(k1, "default", d1, c1, idx, "init"), add_fact(k2, "default", d2, c2, idx, "init")]
            current_vi[id(k1)] = current_vi[id(k2)] = 0
        elif ev == "update":
            k, vi = p["k"], p["vi"]
            disp, core = k["versions"][vi]
            old = k["versions"][vi - 1][0]
            if rng.random() < 0.5:
                text = rng.choice(UPD_OLD_T).format(E=k["entity"], a=an(k), v=disp, old=old)
            else:
                text = rng.choice(UPD_NEW_T).format(E=k["entity"], a=an(k), v=disp)
            fidx.append(add_fact(k, "default", disp, core, idx, "update"))
            current_vi[id(k)] = vi
        elif ev == "revert":
            k, vi = p["k"], p["vi"]
            disp, core = k["versions"][vi]
            bad = k["versions"][vi - 1][0]
            text = rng.choice(REV_T).format(E=k["entity"], a=an(k), old=disp, v=bad)
            fidx.append(add_fact(k, "default", disp, core, idx, "revert"))
            current_vi[id(k)] = vi
        elif ev == "rejected":
            k = p["k"]
            xd, xc = p["x"]
            vd = k["versions"][current_vi.get(id(k), 0)][0]
            text = rng.choice(REJ_T).format(E=k["entity"], a=an(k), x=xd, v=vd)
            fidx.append(add_fact(k, "__rejected__", xd, xc, idx, "rejected"))
        elif ev == "exception":
            k = p["k"]
            scope, (disp, core) = k["exc"]
            text = rng.choice(EXC_T).format(E=k["entity"], a=an(k), v=disp, s=scope)
            fidx.append(add_fact(k, scope, disp, core, idx, "exception"))
        elif ev == "restate":
            k = p["k"]
            vi = current_vi.get(id(k), 0)
            disp, core = k["versions"][vi]
            text = rng.choice(REST_T).format(E=k["entity"], a=an(k), v=disp)
            fidx.append(add_fact(k, "default", disp, core, idx, "restate"))
        elif ev == "note":
            disp, core = p["v"]
            text = p["tmpl"].format(v=disp)
            facts.append(Fact("__note__", p["tmpl"], "default", disp, core, idx, -1, "note"))
            fidx.append(len(facts) - 1)
        else:
            text = p["text"]
        notes.append(Note(idx, -1, "", text, fidx))

    sessions = []
    i, s, d = 0, 0, date(2026, 1, 5)
    while i < len(notes):
        n = rng.randint(*notes_per_session)
        ids = list(range(i, min(len(notes), i + n)))
        for j in ids:
            notes[j].session, notes[j].date = s, d.isoformat()
            for f in notes[j].facts:
                facts[f].session = s
        sessions.append(dict(session=s, date=d.isoformat(), notes=ids))
        i += n
        s += 1
        d += timedelta(days=rng.randint(1, 3))

    def qa(k):
        return rng.choice(ATTR_SYN[k["attr"]]) if rng.random() < 0.25 else k["attr"]

    def fam(k):
        tags = [t for t in ("syn", "rej", "rev") if k[t]]
        return "+".join(tags) if tags else "base"

    qs: list[Question] = []
    for k in keys:
        e, a = k["entity"], k["attr"]
        cur_d, cur_c = k["versions"][-1]
        upd = len(k["versions"]) > 1
        exc = k["exc"] is not None
        qs.append(Question(f"{e}|{a}|CUR", "CUR" if upd else "STABLE", e, a, "default",
                           rng.choice(CUR_Q_T).format(a=qa(k), E=e), cur_c, cur_d, exc, upd, fam(k)))
        if upd:
            pd, pc = k["versions"][-2]
            qs.append(Question(f"{e}|{a}|PREV", "PREV", e, a, "default",
                               rng.choice(PREV_Q_T).format(a=qa(k), E=e), pc, pd, exc, upd, fam(k)))
        if exc:
            scope, (xd, xc) = k["exc"]
            qs.append(Question(f"{e}|{a}|EXC", "EXC", e, a, scope,
                               rng.choice(EXC_Q_T).format(a=qa(k), E=e, s=scope), xc, xd, exc, upd, fam(k)))
    no_exc = [k for k in keys if k["exc"] is None]
    n_excneg = n_excneg if n_excneg is not None else max(4, n_entities // 3)
    for k in rng.sample(no_exc, min(n_excneg, len(no_exc))):
        scope = rng.choice(ENTITY_KINDS[k["kind"]][2])
        cur_d, cur_c = k["versions"][-1]
        qs.append(Question(f"{k['entity']}|{k['attr']}|EXCNEG", "EXCNEG", k["entity"], k["attr"], "default",
                           rng.choice(EXC_Q_T).format(a=qa(k), E=k["entity"], s=scope), cur_c, cur_d,
                           False, len(k["versions"]) > 1, fam(k)))
    for tmpl, qtext, (disp, core) in note_items:
        qs.append(Question(f"note|{core}|NOTE", "NOTE", "__note__", tmpl, "default", qtext, core, disp,
                           False, False, "note"))
    n_abstain = n_abstain if n_abstain is not None else max(4, n_entities // 2)
    for e, kind in rng.sample(list(zip(names, kinds)), min(n_abstain, len(names))):
        a = rng.choice(ABSTAIN_ATTRS[kind])
        qs.append(Question(f"{e}|{a}|ABSTAIN", "ABSTAIN", e, a, "default",
                           f"What is the current default {a} of {e}?", "unknown", "unknown"))
    rng.shuffle(qs)
    return Episode(seed, n_entities, notes, facts, qs, sessions)


if __name__ == "__main__":
    import collections
    import sys
    ep = generate_episode(int(sys.argv[1]) if len(sys.argv) > 1 else 0,
                          int(sys.argv[2]) if len(sys.argv) > 2 else 24)
    raw = ep.raw_text()
    print(raw[:1500])
    print("...")
    print(f"notes={len(ep.notes)} sessions={len(ep.sessions)} facts={len(ep.facts)} raw_chars={len(raw)}")
    print(collections.Counter(q.qtype for q in ep.questions))
    print(collections.Counter(f.kind for f in ep.facts))
