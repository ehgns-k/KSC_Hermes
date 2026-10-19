"""Run the memory-compression experiment grid.

Example:
  python run.py --model qwen3.5:9b --entities 32 --seeds 0 1 2 --budgets 2200 \
      --methods full recency reject summary struct hermes bm25 cem cem_nohist cem_noscope cem_oracle \
      --out ../results/main

Everything is resumable: LLM calls are cached on disk, finished memories and QA rows are
skipped on rerun.
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cem import cem as cemm
from cem import compaction as CP
from cem import methods as M
from cem.datagen import Episode, generate_episode
from cem.llm import LLM, Usage
from cem.qa import BM25Retriever, Scorer, answer, memory_context

ALL_METHODS = ["full", "recency", "reject", "summary", "struct", "hermes", "hermes_ic", "bm25",
               "cem", "cem_nohist", "cem_noscope", "cem_llmmerge", "cem_oracle"]
BUDGET_FREE = {"full", "compact1", "compact3", "compact5", "compact10", "cem_ledger"}


def slug(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")


def load_or_make_episode(out: Path, E: int, seed: int) -> Episode:
    p = out / "episodes" / f"E{E}_s{seed}.json"
    if p.exists():
        return Episode.from_json(p.read_text())
    ep = generate_episode(seed, E)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(ep.to_json())
    (out / "episodes" / f"E{E}_s{seed}_raw.md").write_text(ep.raw_text())
    return ep


def get_cem_records(out: Path, ep: Episode, llm: LLM, E: int, seed: int):
    p = out / "memories" / slug(llm.model) / f"cem_records_E{E}_s{seed}.json"
    if p.exists():
        d = json.loads(p.read_text())
        u = Usage(**{k: d["usage"][k] for k in ("calls", "prompt_tokens", "gen_tokens", "seconds")})
        return d["records"], u, d["stats"]
    t0 = time.time()
    recs, usage, st = cemm.extract(ep, llm)
    # Key canonicalisation is deterministic (Ledger._norm: case, '_', '-', punctuation, fuzzy match).
    # LLM-assisted synonym grouping (cemm.canonicalize) was tried on seed 1 and rejected: one-shot
    # grouping over-merged unrelated settings, pairwise yes/no never merged (docs/progress_log.md).
    st["wall_s"] = round(time.time() - t0, 1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"records": recs, "usage": usage.as_dict(), "stats": st}, ensure_ascii=False, indent=1))
    return recs, usage, st


def build_memory(method: str, ep: Episode, B: int, llm: LLM, out: Path, E: int, seed: int) -> dict:
    p = out / "memories" / slug(llm.model) / f"{method}_B{B}_E{E}_s{seed}.json"
    if p.exists():
        return json.loads(p.read_text())
    t0 = time.time()
    if method == "full":
        mem = M.full_context(ep)
    elif method == "recency":
        mem = M.recency(ep, B)
    elif method == "reject":
        mem = M.reject_on_full(ep, B)
    elif method == "summary":
        mem = M.llm_summary(ep, B, llm, structured=False)
    elif method == "struct":
        mem = M.llm_summary(ep, B, llm, structured=True)
    elif method == "hermes":
        mem = M.hermes_native(ep, B, llm)
    elif method == "hermes_ic":
        mem = M.hermes_constrained(ep, B, llm)
    elif method == "cem_llmmerge":
        recs, usage, st = get_cem_records(out, ep, llm, E, seed)
        mem = cemm.cem_llm_merge(ep, recs, B, llm, extract_usage=usage)
    elif method == "bm25":
        mem = {"entries": [], "chars": 0, "usage": Usage().as_dict(), "stats": {"query_time": True}}
    elif method in ("cem", "cem_nohist", "cem_noscope"):
        recs, usage, st = get_cem_records(out, ep, llm, E, seed)
        mem = cemm.cem_from_records(recs, B, use_scope=method != "cem_noscope",
                                    use_history=method != "cem_nohist", usage=usage, extract=st)
    elif method == "cem_ledger":                # complete CEM fact ledger, no char cap (compaction setting)
        recs, usage, st = get_cem_records(out, ep, llm, E, seed)
        mem = cemm.cem_from_records(recs, 10 ** 6, usage=usage, extract=st)
    elif method.startswith("compact"):          # compact1, compact3, compact5, compact10
        mem = CP.rolling_compaction(ep, int(method[len("compact"):]), llm)
    elif method == "cem_oracle":
        mem = cemm.cem_from_records(cemm.oracle_records(ep), B)
    else:
        raise ValueError(method)
    mem["wall_s"] = round(time.time() - t0, 1)
    mem["raw_chars"] = len(ep.raw_text())
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(mem, ensure_ascii=False, indent=1))
    return mem


def run_qa(method: str, mem: dict, ep: Episode, B: int, llm: LLM, scorer: Scorer, workers: int) -> list[dict]:
    bm = BM25Retriever(ep) if method == "bm25" else None
    raw = method == "full" or method.startswith("compact") or method == "cem_ledger"
    hdr = ("CONTEXT CHECKPOINT SUMMARY (earlier turns were compacted)"
           if method.startswith("compact") or method == "cem_ledger" else None)
    ctx = memory_context(mem["entries"], B, raw=raw, header=hdr) if not bm else None
    mem_text = "\n".join(mem["entries"])

    def one(q):
        if bm:
            ents = bm.context(q, B)
            c = memory_context(ents, B, raw=True, header="RETRIEVED MEMORY NOTES (most relevant first)")
            mtext = "\n".join(ents)
        else:
            c, mtext = ctx, mem_text
        a, ptok = answer(llm, c, q)
        j = scorer.judge(q, a)
        return dict(qid=q.qid, qtype=q.qtype, family=q.family, entity=q.entity, attr=q.attr, scope=q.scope,
                    gold=q.gold, answer=a[:120], pred=j["pred"], correct=bool(j["correct"]), err=j["err"],
                    hedge=j["hedge"], retained=scorer.retained(mtext, q), has_exception=q.has_exception,
                    has_update=q.has_update, prompt_tokens=ptok)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, ep.questions))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.5:9b")
    ap.add_argument("--entities", type=int, nargs="+", default=[24])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0])
    ap.add_argument("--budgets", type=int, nargs="+", default=[2200])
    ap.add_argument("--methods", nargs="+", default=ALL_METHODS)
    ap.add_argument("--out", default="../results/main")
    ap.add_argument("--num-ctx", type=int, default=16384)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit-questions", type=int, default=0)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = Path(__file__).resolve().parents[1] / "results" / "cache"
    llm = LLM(args.model, num_ctx=args.num_ctx, cache_dir=cache)
    qa_path = out / "qa" / f"{slug(args.model)}.jsonl"
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if qa_path.exists():
        for ln in qa_path.read_text().splitlines():
            r = json.loads(ln)
            done.add((r["E"], r["seed"], r["B"], r["method"]))

    for E in args.entities:
        for seed in args.seeds:
            ep = load_or_make_episode(out, E, seed)
            if args.limit_questions:
                ep.questions = ep.questions[:args.limit_questions]
            scorer = Scorer(ep)
            for B in args.budgets:
                for method in args.methods:
                    Bk = 0 if method in BUDGET_FREE else B
                    if (E, seed, Bk, method) in done:
                        continue
                    t0 = time.time()
                    mem = build_memory(method, ep, Bk if Bk else B, llm, out, E, seed)
                    t1 = time.time()
                    rows = run_qa(method, mem, ep, B, llm, scorer, args.workers)
                    acc = sum(r["correct"] for r in rows) / max(1, len(rows))
                    with qa_path.open("a") as f:
                        for r in rows:
                            r.update(model=args.model, E=E, seed=seed, B=Bk, method=method,
                                     mem_chars=mem["chars"], raw_chars=mem.get("raw_chars"))
                            f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    done.add((E, seed, Bk, method))
                    print(f"[{time.strftime('%H:%M:%S')}] {args.model} E={E} s={seed} B={Bk} {method:12s} "
                          f"chars={mem['chars']:6d} acc={acc:.3f} build={t1 - t0:6.1f}s qa={time.time() - t1:6.1f}s",
                          flush=True)
    print("LLM usage:", llm.usage.as_dict())


if __name__ == "__main__":
    main()
