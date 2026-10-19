"""Question answering from a memory block, and fine-grained error typing."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from rank_bm25 import BM25Okapi

from . import hermes_bridge as hb
from .datagen import Episode, Question
from .llm import LLM, Usage

ANSWER_INSTR = ("Reply with only the value (for example: 8080, release-412, 14:35, 10.2.3.4, 350 ms). "
                "If your memory does not contain the answer, reply exactly: unknown")


def memory_context(entries: list[str], budget: int | None, raw: bool = False, header: str | None = None) -> str:
    if raw:
        return f"{header or 'MEMORY FILES (all raw notes, oldest first)'}\n" + "\n".join(entries)
    return hb.render_block(entries, budget or 2200)


def system_prompt(ctx: str) -> str:
    return ("You are Hermes Agent. Answer the user's question using ONLY your persistent memory below.\n\n" + ctx)


def answer(llm: LLM, ctx: str, q: Question, usage: Usage | None = None) -> tuple[str, int]:
    msgs = [{"role": "system", "content": system_prompt(ctx)},
            {"role": "user", "content": f"{q.text}\n{ANSWER_INSTR}"}]
    m = llm.chat(msgs, max_tokens=32, usage=usage)
    return m["content"].strip(), m.get("_prompt_tokens", 0)


# ------------------------------------------------------------------------------ BM25
_tok = re.compile(r"[a-z0-9]+(?:[.:-][a-z0-9]+)*")


def tokenize(s: str) -> list[str]:
    return _tok.findall(s.lower())


class BM25Retriever:
    def __init__(self, ep: Episode):
        self.docs = [f"({n.date}) {n.text}" for n in ep.notes]
        self.bm = BM25Okapi([tokenize(d) for d in self.docs])

    def context(self, q: Question, budget: int) -> list[str]:
        scores = self.bm.get_scores(tokenize(q.text))
        order = sorted(range(len(self.docs)), key=lambda i: -scores[i])
        kept: list[int] = []
        for i in order:
            if scores[i] <= 0:
                break
            if hb.char_count([self.docs[j] for j in kept] + [self.docs[i]]) <= budget:
                kept.append(i)
        return [self.docs[j] for j in sorted(kept)]     # chronological, dates shown


# ------------------------------------------------------------------------------ scoring
UNKNOWN_RE = re.compile(r"unknown|not (?:in|found|available|specified|mentioned|contain|stored|recorded)|"
                        r"no (?:information|record|data|mention)|don't know|do not know|cannot|n/a", re.I)

def _pattern(core: str) -> re.Pattern:
    """Value token: not inside a longer number, IP, time (21:15) or date (2026-03-15);
    a glued unit after it is allowed ('56h', '5150ms', '1933GB')."""
    return re.compile(r"(?<![\w.:])(?<!\d-)" + re.escape(core) + r"(?!\d|\.\d|:\d|-\d)")


class Scorer:
    def __init__(self, ep: Episode):
        self.inv: dict[str, list] = defaultdict(list)    # core -> facts
        for f in ep.facts:
            self.inv[f.core].append(f)
            bare = f.core.split("-")[-1]
            if bare != f.core:
                self.inv[bare].append(f)
        self.pats = {c: _pattern(c) for c in self.inv}
        self.versions: dict[tuple, list[str]] = defaultdict(list)
        for f in sorted(ep.facts, key=lambda f: f.t):
            if f.kind == "rejected":
                continue
            v = self.versions[(f.entity, f.attr, f.scope)]
            if not v or v[-1] != f.core:
                v.append(f.core)

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)

    def find_values(self, text: str) -> list[str]:
        text = self._clean(text)
        hits = []
        for c, p in self.pats.items():
            m = p.search(text)
            if m:
                hits.append((m.start(), -len(c), c))
        hits.sort()
        out = []
        for _, _, c in hits:   # collapse "release-412" + bare "412"
            canon = self._canon(c)
            if canon not in out:
                out.append(canon)
        return out

    def _canon(self, c: str) -> str:
        fs = self.inv[c]
        return fs[0].core if fs else c

    def retained(self, memory_text: str, q: Question) -> bool:
        if q.gold == "unknown":
            return True
        return bool(_pattern(q.gold).search(self._clean(memory_text)))

    def judge(self, q: Question, ans: str) -> dict[str, Any]:
        vals = self.find_values(ans)
        pred = vals[0] if vals else None
        same_key = [v for v in vals if any(f.entity == q.entity and f.attr == q.attr for f in self.inv[v])]
        hedge = len(same_key) >= 2
        out = self._judge(q, ans, vals, pred)
        out["hedge"] = hedge
        return out

    def _judge(self, q: Question, ans: str, vals: list[str], pred: str | None) -> dict[str, Any]:
        says_unknown = bool(UNKNOWN_RE.search(ans))
        if q.qtype == "ABSTAIN":
            ok = pred is None and says_unknown
            return dict(pred=pred, correct=ok, err="" if ok else ("hallucination" if pred else "fabricated"))
        if pred == q.gold:
            return dict(pred=pred, correct=True, err="")
        if pred is None:
            return dict(pred=None, correct=False, err="omission" if says_unknown else "fabricated")
        fs = self.inv[pred]
        if fs and all(f.kind == "rejected" for f in fs):
            return dict(pred=pred, correct=False, err="rejected")
        if any(f.entity == q.entity and f.attr == q.attr and f.scope == q.scope for f in fs):
            err = "version"
        elif any(f.entity == q.entity and f.attr == q.attr for f in fs):
            err = "scope"
        elif any(f.entity == q.entity for f in fs):
            err = "attribute"
        else:
            err = "entity"
        return dict(pred=pred, correct=False, err=err)
