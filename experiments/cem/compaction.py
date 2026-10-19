"""Experiment 2 — cumulative information loss under REPEATED context compaction.

Hermes Agent compacts a long conversation by summarising older turns; on later compactions it
*iteratively updates the previous summary* ("PREVIOUS SUMMARY + NEW TURNS TO INCORPORATE").
We build the summarizer prompt with Hermes' own ContextCompressor._build_summary_prompt
(commit 67481b6) and split the same memo stream into k segments (k = 1, 3, 5, 10):

* rolling (summary-only re-compression):  S_i = C(S_{i-1}, segment_i)   — what Hermes does
* source  (original-referencing):          S_k = C(all original turns)  — one fresh pass over the
  originals; its final summary equals k = 1, but the input it must re-read grows with k
* CEM keeps a ledger of facts extracted from the originals and re-renders it, so its result is
  invariant to k by construction.

The FOCUS TOPIC feature of Hermes carries the same task hint every other method receives.
"""
from __future__ import annotations

from typing import Any

from . import hermes_bridge as hb  # noqa: F401  (sets sys.path / HERMES_HOME)
from .datagen import Episode
from .llm import LLM, Usage

import agent.context_compressor as _CC  # noqa: E402

FOCUS = ("configuration values of the user's projects, hosts and teams: the current default value of "
         "each setting, values that apply only to a specific scope (exceptions such as staging or weekend "
         "runs), the value a setting had right before its most recent change, and lessons learned. "
         "Values that were only considered or rejected are not settings")
SUMMARY_TOKENS = 2000         # Hermes: max(_MIN_SUMMARY_TOKENS=2000, 20% of content) -> 2000 here
MAX_GEN = 3000                # Hermes sets no wire cap on the summary call; this is only a runaway guard
# Long greedy generations made qwen3.5:4b loop ("Indigo, Indigo, ..."); the summarizer therefore uses the
# model's own Ollama default anti-repetition setting (presence_penalty 1.5), still at temperature 0.
SUMMARIZER_OPTIONS = {"presence_penalty": 1.5}


def _segments(ep: Episode, k: int) -> list[list[dict]]:
    n = len(ep.sessions)
    bounds = [round(i * n / k) for i in range(k + 1)]
    return [ep.sessions[bounds[i]:bounds[i + 1]] for i in range(k)]


def _turns(ep: Episode, sessions: list[dict]) -> str:
    out = []
    for s in sessions:
        facts = " ".join(ep.notes[i].text for i in s["notes"])
        out.append(f"[USER] ({s['date']}): {facts}\n[ASSISTANT]: Noted.")
    return "\n".join(out)


def _prompt(previous: str | None, content: str) -> str:
    c = object.__new__(_CC.ContextCompressor)
    c._previous_summary = previous
    c.tail_mode = "full"
    return c._build_summary_prompt(content, SUMMARY_TOKENS, FOCUS, "", True)


def rolling_compaction(ep: Episode, k: int, llm: LLM) -> dict[str, Any]:
    usage = Usage()
    summary: str | None = None
    lens = []
    for seg in _segments(ep, k):
        if not seg:
            continue
        msg = llm.chat([{"role": "user", "content": _prompt(summary, _turns(ep, seg))}],
                       max_tokens=MAX_GEN, usage=usage, extra_options=SUMMARIZER_OPTIONS)
        summary = msg["content"].strip()
        lens.append(len(summary))
    entries = [summary or ""]
    return {"entries": entries, "chars": len(summary or ""), "usage": usage.as_dict(),
            "stats": {"k": k, "round_chars": lens}}


def source_tokens_estimate(ep: Episode, k: int, prompt_tokens_full: int) -> int:
    """Input tokens an original-referencing compactor re-reads over k compactions (it re-summarises
    all originals seen so far each time): sum_i (i/k) * tokens(all originals)."""
    return int(sum((i + 1) / k for i in range(k)) * prompt_tokens_full)
