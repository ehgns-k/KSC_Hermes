"""Baseline memory-compression methods.

Every method turns an Episode's raw note files into Hermes MEMORY.md entries
whose Hermes char count (entries joined by '\\n§\\n') is <= budget B.
"""
from __future__ import annotations

import json
import re
from typing import Any

from . import hermes_bridge as hb
from .datagen import Episode
from .llm import LLM, Usage

# The same evaluation-aware hint is given to EVERY LLM-based method (fairness).
TASK_HINT = ("Later sessions will ask about: the current default value of each setting, values that "
             "apply only to a specific scope (exceptions such as staging or weekend runs), and the value "
             "a setting had right before its most recent change. Keep exact values. Values that were only "
             "considered or rejected are not settings.")


def _note_entry(ep: Episode, i: int) -> str:
    n = ep.notes[i]
    return f"({n.date}) {n.text}"


def _result(entries: list[str], usage: Usage | None = None, **stats) -> dict[str, Any]:
    return {"entries": entries, "chars": hb.char_count(entries),
            "usage": (usage or Usage()).as_dict(), "stats": stats}


# --------------------------------------------------------------------- no-LLM baselines
def full_context(ep: Episode) -> dict[str, Any]:
    """Reference upper bound: every raw note, no budget."""
    entries = [_note_entry(ep, i) for i in range(len(ep.notes))]
    return _result(entries, raw_chars=len(ep.raw_text()))


def recency(ep: Episode, budget: int) -> dict[str, Any]:
    """Keep the newest notes that fit (classic sliding window)."""
    kept: list[int] = []
    for i in range(len(ep.notes) - 1, -1, -1):
        trial = [_note_entry(ep, j) for j in sorted(kept + [i])]
        if hb.char_count(trial) <= budget:
            kept.append(i)
    entries = [_note_entry(ep, j) for j in sorted(kept)]
    return _result(entries, kept_notes=len(kept))


def reject_on_full(ep: Episode, budget: int) -> dict[str, Any]:
    """Hermes semantics with an agent that never consolidates: once MEMORY.md is
    full, every add that would overflow is rejected, so old notes stay forever."""
    store = hb.fresh_store(budget)
    rejected = 0
    for i in range(len(ep.notes)):
        res = json.loads(hb.memory_tool(action="add", target="memory", content=_note_entry(ep, i), store=store))
        rejected += 0 if res.get("success") else 1
    return _result(list(store.memory_entries), rejected_adds=rejected)


# --------------------------------------------------------------------- LLM summarisation
def _lines_to_entries(text: str) -> list[str]:
    out = []
    for ln in text.splitlines():
        ln = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", ln).strip()
        if ln and ln != "§" and not ln.startswith("```"):
            out.append(ln)
    return out


SUMMARY_FREE = ("Rewrite them into a compact memory of at most {B} characters in total. " + TASK_HINT +
                " Output only the memory entries, one entry per line, no commentary.")
SUMMARY_STRUCT = ("Rewrite them into a compact memory of at most {B} characters in total. " + TASK_HINT +
                  " Use exactly one line per project/host/team in this form:\n"
                  "Name — attribute: current value (was previous value; <scope>: scoped value) | attribute: value\n"
                  "Omit the parenthesis when there is no previous value or exception. If space runs out, keep "
                  "current default values first, then exceptions, then previous values. Output only the lines.")


def llm_summary(ep: Episode, budget: int, llm: LLM, structured: bool = False) -> dict[str, Any]:
    usage = Usage()
    instr = (SUMMARY_STRUCT if structured else SUMMARY_FREE).format(B=budget)
    msgs = [{"role": "system", "content": "You maintain the persistent memory of an AI agent (Hermes Agent). "
                                          f"The memory is injected into every future session and has a HARD "
                                          f"limit of {budget} characters."},
            {"role": "user", "content": "Below are memory note files collected over many sessions, oldest first.\n\n"
                                        f"{ep.raw_text()}\n\n{instr}"}]
    max_tok = int(budget / 2) + 300
    out = llm.chat(msgs, max_tokens=max_tok, usage=usage)["content"]
    entries = _lines_to_entries(out)
    first_chars, retried = hb.char_count(entries), False
    if first_chars > budget:
        retried = True
        msgs += [{"role": "assistant", "content": out},
                 {"role": "user", "content": f"That is {first_chars} characters; the hard limit is {budget}. "
                                             f"Shorten it to at most {budget} characters while keeping current "
                                             f"values, exceptions and previous values. Output only the entries."}]
        out = llm.chat(msgs, max_tokens=max_tok, usage=usage)["content"]
        entries = _lines_to_entries(out)
    over = hb.char_count(entries)
    entries = hb.fit_entries(entries, budget)
    return _result(entries, usage, first_chars=first_chars, retried=retried, chars_before_cut=over,
                   truncated=over > budget)


# --------------------------------------------------------------------- Hermes-native agent loop
def _parse_args(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {}


def hermes_native(ep: Episode, budget: int, llm: LLM, max_rounds: int = 6) -> dict[str, Any]:
    """The local LLM plays Hermes Agent: one session per note file, the REAL memory tool,
    a fresh frozen snapshot at each session start, overflow errors force consolidation."""
    store = hb.fresh_store(budget)
    usage = Usage()
    st = dict(sessions=0, tool_calls=0, ok_calls=0, failed_calls=0, overflow_errors=0,
              silent_sessions=0, text_only_claims=0, ops=0)
    guidance = hb.MEMORY_GUIDANCE or ""
    errs: dict[str, int] = {}
    trace: list[list[str]] = []
    for sess in ep.sessions:
        st["sessions"] += 1
        store.reset_consolidation_failures()          # Hermes resets the retry cap every turn
        snapshot = hb.render_block(store.memory_entries, budget)
        bullets = "\n".join(f"- {ep.notes[i].text}" for i in sess["notes"])
        msgs: list[dict[str, Any]] = [
            {"role": "system", "content": "You are Hermes Agent, an AI assistant with persistent memory.\n\n"
                                          f"{guidance}\n\n{snapshot}"},
            {"role": "user", "content": f"[Session {sess['date']}] While working with the user in this session "
                                        f"you learned these durable environment facts:\n{bullets}\n\n"
                                        "Update your persistent memory with the memory tool (target='memory'). "
                                        f"{TASK_HINT} When memory is full, consolidate (merge entries, shorten "
                                        "wording, drop superseded details) instead of skipping new facts."}]
        called = False
        for _ in range(max_rounds):
            msg = llm.chat(msgs, tools=[hb.TOOL_SPEC], max_tokens=1200, usage=usage)
            calls = msg.get("tool_calls") or []
            if not calls:
                if not called and msg.get("content"):
                    st["text_only_claims"] += 1
                break
            called = True
            msgs.append({"role": "assistant", "content": msg.get("content", ""), "tool_calls": calls})
            for c in calls:
                fn = c.get("function", {})
                args = _parse_args(fn.get("arguments"))
                st["tool_calls"] += 1
                if fn.get("name") != "memory":
                    res = json.dumps({"success": False, "error": f"Unknown tool {fn.get('name')}"})
                else:
                    ops = args.get("operations")
                    st["ops"] += len(ops) if isinstance(ops, list) else 1
                    try:
                        res = hb.memory_tool(action=args.get("action", ""), target=args.get("target", "memory"),
                                             content=args.get("content"), old_text=args.get("old_text"),
                                             new_text=args.get("new_text"), operations=ops, store=store)
                    except Exception as e:  # malformed arguments
                        res = json.dumps({"success": False, "error": f"{type(e).__name__}: {e}"})
                try:
                    rj = json.loads(res)
                except Exception:
                    rj = {}
                ok = bool(rj.get("success", False))
                st["ok_calls" if ok else "failed_calls"] += 1
                if not ok:
                    msg_key = re.sub(r"[\d,]+", "N", str(rj.get("error", res)))[:70]
                    errs[msg_key] = errs.get(msg_key, 0) + 1
                if "would exceed" in res or "would put memory at" in res or "over_budget" in res:
                    st["overflow_errors"] += 1
                msgs.append({"role": "tool", "content": res, "tool_name": "memory"})
        if not called:
            st["silent_sessions"] += 1
        trace.append(list(store.memory_entries))
    res = _result(list(store.memory_entries), usage, error_types=errs, **st)
    res["trace"] = trace
    return res


OPS_SCHEMA = {"type": "object", "properties": {"operations": {"type": "array", "items": {
    "type": "object", "properties": {"action": {"type": "string", "enum": ["add", "patch", "remove"]},
                                     "content": {"type": "string"}, "old_text": {"type": "string"}},
    "required": ["action"]}}}, "required": ["operations"]}


def hermes_constrained(ep: Episode, budget: int, llm: LLM, max_rounds: int = 4) -> dict[str, Any]:
    """Hermes-IC: same sessions, guidance, frozen snapshots and REAL memory_tool, but the model
    emits one JSON 'operations' batch (schema-constrained) instead of free tool calls, so
    tool-call syntax failures are removed and only the consolidation policy is measured."""
    store = hb.fresh_store(budget)
    usage = Usage()
    st = dict(sessions=0, batches=0, ok_batches=0, failed_batches=0, overflow_errors=0, empty_batches=0, ops=0)
    errs: dict[str, int] = {}
    trace: list[list[str]] = []
    guidance = hb.MEMORY_GUIDANCE or ""
    for sess in ep.sessions:
        st["sessions"] += 1
        store.reset_consolidation_failures()
        snapshot = hb.render_block(store.memory_entries, budget)
        bullets = "\n".join(f"- {ep.notes[i].text}" for i in sess["notes"])
        msgs: list[dict[str, Any]] = [
            {"role": "system", "content": "You are Hermes Agent, an AI assistant with persistent memory.\n\n"
                                          f"{guidance}\n\nMemory tool documentation:\n{hb.MEMORY_SCHEMA['description']}"
                                          f"\n\n{snapshot}"},
            {"role": "user", "content": f"[Session {sess['date']}] While working with the user in this session "
                                        f"you learned these durable environment facts:\n{bullets}\n\n"
                                        "Update your persistent memory: reply with ONE JSON object "
                                        "{\"operations\": [...]} (actions add / patch / remove, target is memory). "
                                        f"{TASK_HINT} When memory is full, consolidate (merge entries, shorten "
                                        "wording, drop superseded details) instead of skipping new facts."}]
        for _ in range(max_rounds):
            out = llm.chat(msgs, fmt=OPS_SCHEMA, max_tokens=1200, usage=usage)["content"]
            try:
                ops = json.loads(out).get("operations", [])
            except Exception:
                ops = None
            if not ops:
                st["empty_batches"] += 1
                break
            st["batches"] += 1
            st["ops"] += len(ops)
            try:
                res = hb.memory_tool(target="memory", operations=ops, store=store)
            except Exception as e:
                res = json.dumps({"success": False, "error": f"{type(e).__name__}: {e}"})
            try:
                rj = json.loads(res)
            except Exception:
                rj = {}
            if rj.get("success"):
                st["ok_batches"] += 1
                break
            st["failed_batches"] += 1
            key = re.sub(r"[\d,]+", "N", str(rj.get("error", res)))[:70]
            errs[key] = errs.get(key, 0) + 1
            if "would exceed" in res or "would put memory at" in res:
                st["overflow_errors"] += 1
            if rj.get("done"):
                break
            msgs += [{"role": "assistant", "content": out},
                     {"role": "user", "content": f"Memory tool result: {res}\nReply with a corrected operations batch."}]
        trace.append(list(store.memory_entries))
    res = _result(list(store.memory_entries), usage, error_types=errs, **st)
    res["trace"] = trace
    return res
