"""CEM — Change- and Exception-aware Memory consolidation (proposed).

Stage 1 (LLM, local): each note file -> atomic facts
        (entity, attribute, scope, value, previous_value), JSON-schema constrained.
Stage 2 (deterministic): canonicalise names, key facts by (entity, attribute, scope),
        order by time, keep the version chain.
Stage 3 (deterministic): render one dense Hermes entry per entity and pack it under the char
        budget with a marginal-character-cost greedy that maximises the number of retained facts
        (ties: current default > scoped exception > previous value > free-text note, then recency).
        Whatever does not fit goes to an archive (not shown to the reader).
The LLM never rewrites or merges memory, so it cannot overwrite an exception with a
default, keep a stale value as current, or silently drop a changed value.
"""
from __future__ import annotations

import json
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from . import hermes_bridge as hb
from .datagen import Episode
from .llm import LLM, Usage

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {"facts": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "note": {"type": "integer"},
            "entity": {"type": "string"},
            "attribute": {"type": "string"},
            "scope": {"type": "string"},
            "value": {"type": "string"},
            "previous_value": {"type": "string"},
        },
        "required": ["note", "entity", "attribute", "scope", "value", "previous_value"]}}},
    "required": ["facts"],
}

EXTRACT_PROMPT = """Known entities and their attributes so far (reuse these exact names when a note refers to the same thing):
{catalog}

Notes from session {date}:
{notes}

For EVERY concrete setting stated in the notes, output one fact:
- note: the note number
- entity: the project/service/host/team name only (e.g. "Orion"), never an environment or condition
- attribute: short attribute name (e.g. "API port"); reuse a known attribute name if it means the same thing
- scope: "default" if the value is the normal/general setting; otherwise the specific environment, group or condition it applies to ONLY (e.g. "staging", "weekend runs", "frontend squad"). Words such as "exception", "except", "only", "overrides", "special case", "for <group>" signal a scoped value, and the normal setting stays unchanged
- value: the value exactly as written (for a change, the NEW value that is now in effect)
- previous_value: the old value that was actually in effect before a change, if the note states it; otherwise "" (never a value that was only proposed or tried)
A note with two settings gives two facts. Values that were only proposed, considered or rejected are NOT settings: output only the value that is actually in effect. Output no fact for notes without a concrete setting."""

DEFAULT_SCOPES = {"", "default", "general", "normal", "all", "none", "global", "everywhere", "usual",
                  "elsewhere", "standard", "base", "n/a", "na", "null", "any"}
KIND_WORDS = r"\b(service|host|team|project|server|squad|machine|cluster)\b"


def _norm(s: str) -> str:
    s = (s or "").strip().lower().replace("_", " ").replace("-", " ")
    s = re.sub(r"^(the|on|for|in|during)\s+", "", s)
    s = re.sub(r"[\"'`’]s?\b", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .,:;-—")
    return s


BAD_VALUES = {"usual", "unchanged", "normal", "default", "same", "n/a", "none", "unknown", "previous",
              "old", "new", "standard", "as before", "the usual", "not specified", ""}


def grounded(value: str, text: str) -> bool:
    """A value is kept only if it literally occurs in its source note (numbers/codes all present)."""
    v, t = value.strip().lower(), text.lower()
    if v in BAD_VALUES:
        return False
    if v in t:
        return True
    nums = re.findall(r"\d[\d.:]*\d|\d", v)
    return bool(nums) and all(n in t for n in nums)


def short_scope(s: str) -> str:
    return re.sub(r"^(the)\s+", "", s.strip(), flags=re.I)


@dataclass
class Ledger:
    entity_order: list[str] = field(default_factory=list)
    attrs: "OrderedDict[str, list[str]]" = field(default_factory=OrderedDict)    # entity -> attrs
    chains: dict[tuple[str, str, str], list[tuple[int, str]]] = field(default_factory=dict)  # key -> [(t, value)]
    misc: list[tuple[int, str]] = field(default_factory=list)                   # free-text notes
    scopes: dict = field(default_factory=dict)

    def catalog(self) -> str:
        if not self.attrs:
            return "(none yet)"
        return "\n".join(f"- {e}: {', '.join(a)}" for e, a in self.attrs.items())

    # -- canonicalisation ------------------------------------------------------------
    def canon_entity(self, name: str) -> str:
        raw = re.sub(KIND_WORDS, "", name, flags=re.I)
        n = _norm(raw) or _norm(name)
        for e in self.entity_order:
            if _norm(e) == n:
                return e
        best = max(self.entity_order, key=lambda e: fuzz.ratio(_norm(e), n), default=None)
        if best is not None and fuzz.ratio(_norm(best), n) >= 90:
            return best
        disp = raw.strip(" .,:;-—\"'") or name.strip()
        disp = re.sub(r"^(the)\s+", "", disp, flags=re.I).strip()
        self.entity_order.append(disp)
        self.attrs[disp] = []
        return disp

    def canon_attr(self, entity: str, attr: str) -> str:
        n = _norm(attr)
        pool = self.attrs[entity]
        for a in pool:
            if _norm(a) == n:
                return a
        best = max(pool, key=lambda a: fuzz.token_set_ratio(_norm(a), n), default=None)
        if best is not None and fuzz.token_set_ratio(_norm(best), n) >= 92:
            return best
        disp = attr.strip(" .,:;-—")
        pool.append(disp)
        return disp

    def canon_scope(self, entity: str, attr: str, scope: str) -> str:
        n = _norm(scope)
        if n in DEFAULT_SCOPES:
            return "default"
        known = {s for (e, a, s) in self.chains if e == entity and a == attr and s != "default"}
        known |= {s for (_, _, s) in self.chains if s != "default"}
        for s in known:
            if _norm(s) == n:
                return s
        best = max(known, key=lambda s: fuzz.ratio(_norm(s), n), default=None)
        if best is not None and fuzz.ratio(_norm(best), n) >= 88:
            return best
        return scope.strip(" .,:;-—")

    # -- merge ------------------------------------------------------------------------
    def add(self, t: int, entity: str, attr: str, scope: str, value: str, prev: str = "") -> None:
        value = (value or "").strip()
        if not value or not entity.strip() or not attr.strip():
            return
        e = self.canon_entity(entity)
        a = self.canon_attr(e, attr)
        s = self.canon_scope(e, a, scope)
        chain = self.chains.setdefault((e, a, s), [])
        prev = (prev or "").strip()
        if prev and prev != value and not chain:
            chain.append((t - 1, prev))       # old value known only from the change note
        # once a key has an observed history, it wins over an LLM-reported previous value
        if not chain or chain[-1][1] != value:
            chain.append((t, value))          # identical restatement -> no new version

    def last_t(self, key) -> int:
        return self.chains[key][-1][0]


def extract(ep: Episode, llm: LLM) -> tuple[list[dict[str, Any]], Usage, dict[str, int]]:
    """Stage 1: per-session constrained extraction. Returns raw fact records with time t."""
    usage = Usage()
    led = Ledger()
    records: list[dict[str, Any]] = []
    st = dict(calls=0, parse_errors=0, facts=0)
    for sess in ep.sessions:
        ids = sess["notes"]
        notes = "\n".join(f"{k + 1}. {ep.notes[i].text}" for k, i in enumerate(ids))
        msgs = [{"role": "system", "content": "You convert an AI agent's memory notes into atomic facts for a "
                                              "versioned key-value ledger. Be exact and complete."},
                {"role": "user", "content": EXTRACT_PROMPT.format(catalog=led.catalog(), date=sess["date"],
                                                                   notes=notes)}]
        st["calls"] += 1
        out = llm.chat(msgs, fmt=EXTRACT_SCHEMA, max_tokens=900, usage=usage)["content"]
        try:
            facts = json.loads(out).get("facts", [])
        except Exception:
            st["parse_errors"] += 1
            facts = []
        extracted_notes = set()
        for f in facts:
            try:
                k = int(f.get("note", 0)) - 1
            except Exception:
                k = -1
            i = ids[k] if 0 <= k < len(ids) else ids[-1]
            rec = dict(t=i, entity=str(f.get("entity", "")), attribute=str(f.get("attribute", "")),
                       scope=str(f.get("scope", "default")), value=str(f.get("value", "")).strip(),
                       previous_value=str(f.get("previous_value", "")).strip())
            note_text = ep.notes[i].text
            if not grounded(rec["value"], note_text):
                st["ungrounded"] = st.get("ungrounded", 0) + 1
                continue
            if rec["previous_value"] and (not grounded(rec["previous_value"], note_text)
                                          or _norm(rec["scope"]) not in DEFAULT_SCOPES):
                rec["previous_value"] = ""
            records.append(rec)
            led.add(rec["t"], rec["entity"], rec["attribute"], rec["scope"], rec["value"], rec["previous_value"])
            extracted_notes.add(i)
            st["facts"] += 1
        for i in ids:  # notes without any fact are kept verbatim as free text
            if i not in extracted_notes:
                records.append(dict(t=i, misc=ep.notes[i].text))
    return records, usage, st


def build_ledger(records: list[dict[str, Any]], use_scope: bool = True) -> Ledger:
    led = Ledger()
    for r in sorted(records, key=lambda r: r["t"]):
        if "misc" in r:
            if r["misc"] not in [m for _, m in led.misc]:
                led.misc.append((r["t"], r["misc"]))
            continue
        scope = r["scope"] if use_scope else "default"
        led.add(r["t"], r["entity"], r["attribute"], scope, r["value"], r.get("previous_value", ""))
    return led


def oracle_records(ep: Episode) -> list[dict[str, Any]]:
    """Ground-truth facts in the same record format (isolates extraction error)."""
    recs = [dict(t=f.t, entity=f.entity, attribute=f.attr, scope=f.scope, value=f.value, previous_value="")
            for f in ep.facts if f.kind not in ("rejected", "note")]
    recs += [dict(t=n.idx, misc=n.text) for n in ep.notes
             if not n.facts or all(ep.facts[j].kind == "note" for j in n.facts)]
    return recs


# ------------------------------------------------------------------------- render + pack
def _entity_entry(led: Ledger, e: str, inc: set) -> str:
    """Compact one-line entry, e.g. 'Orion: API port 9090 (was 8080; staging: 8081); log retention 45 days'."""
    parts = []
    for a in led.attrs.get(e, []):
        dkey = (e, a, "default")
        chain = led.chains.get(dkey, [])
        has_cur = ("T1", dkey) in inc and bool(chain)
        extras = []
        if has_cur and ("T3", dkey) in inc and len(chain) >= 2:
            extras.append(f"was {chain[-2][1]}")
        for s in led.scopes.get((e, a), []):
            if ("T2", (e, a, s)) in inc:
                extras.append(f"{short_scope(s)}: {led.chains[(e, a, s)][-1][1]}")
        if has_cur:
            parts.append(f"{a} {chain[-1][1]}" + (f" ({'; '.join(extras)})" if extras else ""))
        elif extras:
            parts.append(f"{a} ({'; '.join(extras)})")
    return f"{e}: " + "; ".join(parts) if parts else ""


def _render(led: Ledger, inc: set) -> list[str]:
    entries = [x for x in (_entity_entry(led, e, inc) for e in led.entity_order) if x]
    entries += [m for (t, m) in led.misc if ("T0", t) in inc]
    return entries


TIER_RANK = {"T1": 0, "T2": 1, "T3": 2, "T0": 3}


def pack(led: Ledger, budget: int, tiers: tuple[str, ...] = ("T1", "T2", "T3", "T0")) -> tuple[list[str], dict]:
    """Marginal-cost greedy: repeatedly add the fact whose inclusion costs the fewest characters
    (ties: tier T1>T2>T3>T0, then most recently touched), until nothing more fits the budget.
    This maximises the number of retained facts; a previous value (T3) needs its current value (T1)."""
    led.scopes = {}
    for (e, a, s) in led.chains:
        if s != "default":
            led.scopes.setdefault((e, a), []).append(s)
    items = []   # (tier, key, entity, t)
    for key, chain in led.chains.items():
        t = chain[-1][0]
        if key[2] == "default":
            items.append(("T1", key, key[0], t))
            if len(chain) >= 2:
                items.append(("T3", key, key[0], t))
        else:
            items.append(("T2", key, key[0], t))
    items += [("T0", t, None, t) for (t, _) in led.misc]
    items = [it for it in items if it[0] in tiers]
    inc: set = set()
    ent_len: dict[str, int] = {}
    n_entries = 0
    total = 0

    def cost(it):
        tier, key, e, _ = it
        if tier == "T3" and ("T1", key) not in inc:
            return None
        if tier == "T0":
            text = next(m for (t, m) in led.misc if t == key)
            return len(text) + (3 if n_entries else 0)
        old = ent_len.get(e, 0)
        inc.add((tier, key))
        new = len(_entity_entry(led, e, inc))
        inc.discard((tier, key))
        return new - old + (3 if old == 0 and n_entries else 0)

    remaining = list(items)
    costs = {id(it): cost(it) for it in remaining}
    while remaining:
        cands = [it for it in remaining if costs[id(it)] is not None and total + costs[id(it)] <= budget]
        if not cands:
            break
        best = min(cands, key=lambda it: (costs[id(it)], TIER_RANK[it[0]], -it[3]))
        remaining.remove(best)
        inc.add((best[0], best[1]))
        total += costs[id(best)]
        if best[0] == "T0" or ent_len.get(best[2], 0) == 0:
            n_entries += 1
        if best[0] != "T0":
            ent_len[best[2]] = len(_entity_entry(led, best[2], inc))
            for it in remaining:          # only items of the same entity (or T3 deps) change cost
                if it[2] == best[2]:
                    costs[id(it)] = cost(it)
        else:
            for it in remaining:
                if it[0] == "T0" or ent_len.get(it[2], 0) == 0:
                    costs[id(it)] = cost(it)
    entries = _render(led, inc)
    while hb.char_count(entries) > budget:      # safety net (should not trigger)
        entries.pop()
    dropped = {k: sum(1 for it in items if it[0] == k and (it[0], it[1]) not in inc) for k in TIER_RANK}
    kept = {k: sum(1 for it in items if it[0] == k and (it[0], it[1]) in inc) for k in TIER_RANK}
    return entries, {"dropped": dropped, "kept": kept}


def cem_from_records(records: list[dict[str, Any]], budget: int, *, use_scope: bool = True,
                     use_history: bool = True, usage: Usage | None = None, **extra) -> dict[str, Any]:
    led = build_ledger(records, use_scope=use_scope)
    tiers = ("T1", "T2", "T3", "T0") if use_history else ("T1", "T2", "T0")
    entries, st = pack(led, budget, tiers)
    return {"entries": entries, "chars": hb.char_count(entries),
            "usage": (usage or Usage()).as_dict(),
            "stats": dict(st, keys=len(led.chains), entities=len(led.entity_order), **extra)}


# ------------------------------------------------------------------------- key canonicalisation
SAME_SCHEMA = {"type": "object", "properties": {"same": {"type": "boolean"}}, "required": ["same"]}
SAME_PROMPT = """In an AI agent's memory about "{entity}", two notes used these attribute names:
A: "{a}" (example value: {va})
B: "{b}" (example value: {vb})
Do A and B name exactly the same setting of {entity} (just worded differently)? Answer with JSON {{"same": true}} or {{"same": false}}."""


def value_type(v: str) -> str:
    v = v.strip().lower()
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", v):
        return "ip"
    if re.fullmatch(r"\d{1,2}:\d{2}", v):
        return "time"
    if re.search(r"release-\d+", v):
        return "branch"
    if v.startswith("$"):
        return "usd"
    if v.endswith("%"):
        return "pct"
    m = re.fullmatch(r"[\d.,]+\s*([a-z]+)", v)
    if m:
        return m.group(1).rstrip("s")
    if re.fullmatch(r"[\d.,]+", v):
        return "num"
    return "text"


def _compatible(t1: str, t2: str) -> bool:
    if t1 == t2:
        return True
    numeric = {"num", "ms", "mb", "gb", "day", "hour", "char"}
    return ("num" in (t1, t2)) and t1 in numeric and t2 in numeric


def canonicalize(records: list[dict[str, Any]], llm: LLM) -> tuple[list[dict[str, Any]], Usage, dict]:
    """KEY canonicalisation. (1) deterministic: case, '_'/'-', punctuation; (2) for attribute-name
    pairs of the same entity whose values have a compatible type, a yes/no LLM judgement
    ("same setting?"); positive pairs are merged (union-find) under the most frequent name.
    Values are never rewritten."""
    usage = Usage()
    led = Ledger()
    by_ent: dict[str, dict[str, list]] = {}
    for r in records:
        if "misc" in r:
            continue
        e = led.canon_entity(r["entity"])
        by_ent.setdefault(e, {}).setdefault(_norm(r["attribute"]).replace("-", " "), []).append(r)
    st = dict(calls=0, merged_pairs=0, parse_errors=0)
    for e, names in by_ent.items():
        keys = list(names)
        parent = {k: k for k in keys}

        def find(k):
            while parent[k] != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = keys[i], keys[j]
                ta, tb = value_type(names[a][0]["value"]), value_type(names[b][0]["value"])
                if not _compatible(ta, tb) or find(a) == find(b):
                    continue
                msgs = [{"role": "user", "content": SAME_PROMPT.format(
                    entity=e, a=names[a][0]["attribute"], b=names[b][0]["attribute"],
                    va=names[a][0]["value"], vb=names[b][0]["value"])}]
                st["calls"] += 1
                out = llm.chat(msgs, fmt=SAME_SCHEMA, max_tokens=20, usage=usage)["content"]
                try:
                    same = bool(json.loads(out).get("same", False))
                except Exception:
                    st["parse_errors"] += 1
                    same = False
                if same:
                    parent[find(b)] = find(a)
                    st["merged_pairs"] += 1
        groups: dict[str, list[str]] = {}
        for k in keys:
            groups.setdefault(find(k), []).append(k)
        for members in groups.values():
            canon = max(members, key=lambda k: (len(names[k]), -keys.index(k)))
            disp = names[canon][0]["attribute"].replace("_", " ")
            for k in members:
                for r in names[k]:
                    r["attribute_raw"] = r["attribute"]
                    r["attribute"] = disp
    return records, usage, st


# ------------------------------------------------------------------------- ablation: LLM merge
MERGE_SCHEMA = {"type": "object", "properties": {"entries": {"type": "array", "items": {
    "type": "object", "properties": {"entity": {"type": "string"}, "line": {"type": "string"}},
    "required": ["entity", "line"]}}}, "required": ["entries"]}

MERGE_PROMPT = """Current memory lines for the entities touched in this session:
{lines}

New facts from session {date}, in order (entity | attribute | scope | value | previous value):
{facts}

Rewrite the memory line of every touched entity so that it reflects ALL facts: the current default value of each attribute, scoped exceptions, and the previous value right before the latest change. Keep existing information that is still valid. Use exactly this compact format:
Name: attribute value (was previous; scope: value); attribute value
Return one line per touched entity."""


def cem_llm_merge(ep: Episode, records: list[dict[str, Any]], budget: int, llm: LLM,
                  extract_usage: Usage | None = None) -> dict[str, Any]:
    """Mem0-style ablation: SAME extracted facts, but the LLM (not the deterministic ledger)
    merges them into per-entity memory lines; least-recently updated entities are dropped to fit."""
    usage = Usage()
    led = Ledger()                     # only used for name canonicalisation
    lines: dict[str, str] = {}
    touched_t: dict[str, int] = {}
    by_session: dict[int, list] = {}
    for r in records:
        if "misc" not in r:
            by_session.setdefault(ep.notes[r["t"]].session, []).append(r)
    st = dict(calls=0, parse_errors=0)
    for sess in ep.sessions:
        recs = by_session.get(sess["session"], [])
        if not recs:
            continue
        ents = []
        for r in recs:
            r["_e"] = led.canon_entity(r["entity"])
            if r["_e"] not in ents:
                ents.append(r["_e"])
        cur = "\n".join(lines[e] for e in ents if e in lines) or "(none yet)"
        facts = "\n".join(f"- {r['_e']} | {r['attribute']} | {r['scope']} | {r['value']} | {r['previous_value'] or '-'}"
                          for r in recs)
        msgs = [{"role": "system", "content": "You maintain an AI agent's persistent memory as one compact line per entity."},
                {"role": "user", "content": MERGE_PROMPT.format(lines=cur, date=sess["date"], facts=facts)}]
        st["calls"] += 1
        out = llm.chat(msgs, fmt=MERGE_SCHEMA, max_tokens=900, usage=usage)["content"]
        try:
            got = json.loads(out).get("entries", [])
        except Exception:
            st["parse_errors"] += 1
            got = []
        for g in got:
            e = led.canon_entity(str(g.get("entity", "")))
            line = str(g.get("line", "")).strip()
            if line:
                lines[e] = line
                touched_t[e] = max(r["t"] for r in recs)
    order = [e for e in led.entity_order if e in lines]
    keep = sorted(order, key=lambda e: -touched_t.get(e, 0))
    while keep and hb.char_count([lines[e] for e in order if e in keep]) > budget:
        keep.pop()
    entries = [lines[e] for e in order if e in keep]
    total = Usage()
    if extract_usage:
        total.add(extract_usage)
    total.add(usage)
    return {"entries": entries, "chars": hb.char_count(entries), "usage": total.as_dict(),
            "all_lines": [lines[e] for e in order],
            "stats": dict(st, merge_usage=usage.as_dict(), entities=len(order), dropped_entities=len(order) - len(keep))}
