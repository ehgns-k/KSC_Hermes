"""Post-hoc (no GPU): replay cached CEM-LLM-merge calls to measure retention BEFORE the final
whole-entity truncation, separating merge loss from packing loss (review finding #11)."""
import json
import sys
from pathlib import Path

import pandas as pd

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP))

from analyze import bound_retained, load_episode
from cem import cem as C
from cem import hermes_bridge as hb
from cem.llm import LLM

out = []
for model in sys.argv[1:] or ["qwen3.5:9b", "qwen3.5:4b"]:
    slug = model.replace(":", "_")
    for seed in (1, 2, 3):
        d = EXP.parent / "results" / "main"
        rp = d / "memories" / slug / f"cem_records_E24_s{seed}.json"
        if not rp.exists():
            continue
        recs = json.loads(rp.read_text())["records"]
        ep = load_episode(d, 24, seed)
        llm = LLM(model, num_ctx=16384 if "9b" in model else 8192, cache_dir=EXP.parent / "results" / "cache")
        before = llm.usage.calls
        m = C.cem_llm_merge(ep, json.loads(json.dumps(recs)), 2200, llm)
        if llm.usage.cache_hits != llm.usage.calls:
            print("WARNING: cache miss", model, seed, file=sys.stderr)
        cemm = C.cem_from_records(recs, 2200)
        ents = sorted({f.entity for f in ep.facts if f.entity != "__note__"})
        qs = [q for q in ep.questions if q.qtype not in ("ABSTAIN",)]

        def ret(entries):
            return sum(bound_retained(entries, q.__dict__, ents) for q in qs) / len(qs)
        out.append(dict(model=model, seed=seed,
                        llmmerge_all_chars=hb.char_count(m["all_lines"]),
                        llmmerge_ret_before_cut=round(100 * ret(m["all_lines"]), 1),
                        llmmerge_ret_after_cut=round(100 * ret(m["entries"]), 1),
                        cem_ret=round(100 * ret(cemm["entries"]), 1),
                        cem_unbudgeted_ret=round(100 * ret(C.cem_from_records(recs, 10 ** 6)["entries"]), 1),
                        cem_unbudgeted_chars=C.cem_from_records(recs, 10 ** 6)["chars"]))
df = pd.DataFrame(out)
print(df.to_string())
TAB = EXP.parent / "paper" / "tables"
TAB.mkdir(parents=True, exist_ok=True)
df.to_csv(TAB / "llmmerge_posthoc.csv", index=False)
(TAB / "llmmerge_posthoc.md").write_text(
    "CEM−결정적 병합(LLM 병합)의 손실 위치 분해: 같은 추출 결과에서 예산 절단 전/후의 엔티티 결합 보존율(%). "
    "cem_unbudgeted = 예산 없이 결정적 병합만 했을 때.\n\n" + df.to_markdown(index=False) + "\n")
