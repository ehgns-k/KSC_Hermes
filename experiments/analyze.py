"""Turn raw QA rows + memories into paper tables (CSV/Markdown) and figures (PNG/PDF).

Usage:
  python analyze.py --main ../results/main --sweep ../results/sweep --xmodel ../results/xmodel \
      --out ../paper
Every input is optional; sections without data are skipped.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

TYPES = ["CUR", "STABLE", "PREV", "EXC", "EXCNEG", "NOTE", "ABSTAIN"]
TYPE_KO = {"CUR": "현재값", "STABLE": "불변값", "PREV": "이전값", "EXC": "예외값", "EXCNEG": "예외없음",
           "NOTE": "자유메모", "ABSTAIN": "모름"}
NAMES = {
    "full": "Full-context (무압축 참조)", "bm25": "BM25 검색 (질의시점 참조)",
    "recency": "Recency (최신 노트 유지)", "reject": "Hermes 무통합 (초과 시 거부)",
    "summary": "LLM 요약", "struct": "LLM 구조화 요약", "hermes": "Hermes 에이전트 (도구호출)",
    "hermes_ic": "Hermes 에이전트 (JSON 제약)", "cem": "CEM (제안)", "cem_nohist": "CEM − 이전값",
    "cem_noscope": "CEM − 범위키", "cem_llmmerge": "CEM − 결정적 병합 (LLM 병합)",
    "cem_oracle": "CEM-Oracle (정답 추출)",
    "compact1": "Hermes 문맥 압축 k=1", "compact3": "Hermes 문맥 압축 k=3",
    "compact5": "Hermes 문맥 압축 k=5", "compact10": "Hermes 문맥 압축 k=10",
    "cem_ledger": "CEM 사실 원장 (글자 제한 없음)",
}
SHORT = {"full": "Full", "bm25": "BM25", "recency": "Recency", "reject": "NoConsol", "summary": "Summary",
         "struct": "StructSum", "hermes": "Hermes-tool", "hermes_ic": "Hermes-JSON", "cem": "CEM",
         "cem_nohist": "CEM w/o 이전값", "cem_noscope": "CEM w/o 범위키", "cem_llmmerge": "CEM LLM병합",
         "cem_oracle": "CEM-Oracle"}
ORDER = ["full", "bm25", "recency", "reject", "summary", "struct", "hermes", "hermes_ic",
         "cem_llmmerge", "cem_noscope", "cem_nohist", "cem", "cem_oracle"]
ERRS = ["omission", "version", "scope", "attribute", "entity", "rejected", "fabricated", "hallucination"]
ERR_KO = {"omission": "누락(모름)", "version": "버전 혼동(구값/신값)", "scope": "범위 혼동(예외↔기본)",
          "attribute": "속성 혼동", "entity": "엔티티 혼동", "rejected": "기각값 채택",
          "fabricated": "근거 없는 값", "hallucination": "모름 질문에 값 생성"}
BASELINES = ["recency", "summary", "struct", "hermes", "hermes_ic", "cem_llmmerge"]


# ---------------------------------------------------------------------------- loading
EXAMPLE_VALUES = {"8080", "release-412", "412", "14:35", "10.2.3.4", "350"}   # shown in ANSWER_INSTR


def load_rows(d: Path, rescore_rows: bool = True) -> pd.DataFrame:
    rows = []
    for p in sorted((d / "qa").glob("*.jsonl")):
        rows += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.drop_duplicates(subset=["model", "E", "seed", "B", "method", "qid"], keep="last")
    if rescore_rows:
        df = rescore(df, d)
    # questions whose gold equals an example value of the answer instruction are excluded
    df = df[~df.gold.astype(str).isin(EXAMPLE_VALUES)]
    return df


def rescore(df: pd.DataFrame, d: Path) -> pd.DataFrame:
    """Re-judge every stored answer with the current Scorer (no LLM calls) and recompute the
    string-level retention from the saved memories (BM25 contexts are rebuilt deterministically)."""
    from cem.qa import BM25Retriever, Scorer
    out = []
    for (model, E, seed, B, method), g in df.groupby(["model", "E", "seed", "B", "method"]):
        ep = load_episode(d, E, seed)
        sc = Scorer(ep)
        qmap = {q.qid: q for q in ep.questions}
        mem = load_mem(d, model, method, B, E, seed)
        bm = BM25Retriever(ep) if method == "bm25" else None
        text = "\n".join(mem["entries"]) if mem else ""
        g = g.copy()
        res = []
        for _, r in g.iterrows():
            q = qmap.get(r["qid"])
            if q is None:
                res.append((r["pred"], r["correct"], r["err"], r.get("hedge", False), r["retained"]))
                continue
            j = sc.judge(q, str(r["answer"]))
            if bm is not None:
                mt = "\n".join(bm.context(q, B or 2200))
            else:
                mt = text
            res.append((j["pred"], bool(j["correct"]), j["err"], bool(j["hedge"]), sc.retained(mt, q)))
        g["pred"], g["correct"], g["err"], g["hedge"], g["retained"] = zip(*res)
        g["correct"] = g["correct"].astype(bool)
        g["retained"] = g["retained"].astype(bool)
        out.append(g)
    return pd.concat(out)


def load_mem(d: Path, model: str, method: str, B: int, E: int, seed: int) -> dict | None:
    slug = model.replace(":", "_").replace("/", "_")
    p = d / "memories" / slug / f"{method}_B{B if method != 'full' else B}_E{E}_s{seed}.json"
    if not p.exists():
        cands = list((d / "memories" / slug).glob(f"{method}_B*_E{E}_s{seed}.json"))
        if (method == "full" or method.startswith("compact")) and cands:
            p = cands[0]
        else:
            return None
    return json.loads(p.read_text())


def load_episode(d: Path, E: int, seed: int):
    from cem.datagen import Episode
    return Episode.from_json((d / "episodes" / f"E{E}_s{seed}.json").read_text())


# ---------------------------------------------------------------------------- metrics
def macro(df: pd.DataFrame) -> float:
    accs = [df[df.qtype == t].correct.mean() for t in TYPES if (df.qtype == t).any()]
    return float(np.mean(accs)) if accs else float("nan")


def _clusters(df: pd.DataFrame) -> pd.Series:
    """(seed, entity) clusters; free-form NOTE questions (no entity) are their own clusters."""
    ent = df["entity"].astype(str).where(df["entity"].astype(str) != "__note__", df["qid"].astype(str))
    return df["seed"].astype(str) + "|" + ent


def boot_macro_ci(df: pd.DataFrame, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Cluster bootstrap over (seed, entity) groups, stratified by nothing else."""
    rng = np.random.default_rng(seed)
    df = df.assign(cluster=_clusters(df))
    groups = {k: g for k, g in df.groupby("cluster")}
    keys = list(groups)
    vals = []
    for _ in range(n):
        pick = rng.choice(len(keys), len(keys), replace=True)
        bdf = pd.concat([groups[keys[i]] for i in pick])
        vals.append(macro(bdf))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def boot_diff_ci(a: pd.DataFrame, b: pd.DataFrame, n: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """Paired cluster bootstrap for macro(a) - macro(b) on the same questions."""
    rng = np.random.default_rng(seed)
    key = ["seed", "qid"]
    m = a[key + ["entity", "qtype", "correct"]].merge(b[key + ["correct"]], on=key, suffixes=("_a", "_b"))
    m["cluster"] = _clusters(m)
    groups = {k: g for k, g in m.groupby("cluster")}
    keys = list(groups)

    def md(x):
        return (np.mean([x[x.qtype == t].correct_a.mean() for t in TYPES if (x.qtype == t).any()]) -
                np.mean([x[x.qtype == t].correct_b.mean() for t in TYPES if (x.qtype == t).any()]))
    point = md(m)
    vals = []
    for _ in range(n):
        pick = rng.choice(len(keys), len(keys), replace=True)
        vals.append(md(pd.concat([groups[keys[i]] for i in pick])))
    return float(point), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def mcnemar(a: pd.DataFrame, b: pd.DataFrame) -> tuple[int, int, float]:
    key = ["seed", "qid"]
    m = a[key + ["correct"]].merge(b[key + ["correct"]], on=key, suffixes=("_a", "_b"))
    n10 = int(((m.correct_a) & (~m.correct_b)).sum())
    n01 = int(((~m.correct_a) & (m.correct_b)).sum())
    p = binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0
    return n10, n01, float(p)


def holm(ps: list[float]) -> list[float]:
    order = np.argsort(ps)
    adj = [0.0] * len(ps)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


def _scope_regex(scope: str) -> re.Pattern:
    head = re.sub(r"^(the)\s+", "", scope, flags=re.I).split()[0].lower()
    alias = {"fridays": r"fri(day)?s?", "weekend": r"weekends?"}
    return re.compile(r"\b" + alias.get(head, re.escape(head.rstrip("s")) + "s?") + r"\b", re.I)


def bound_retained(mem_entries: list[str], q: dict, entities: list[str] | None = None) -> bool:
    """Gold value is present AND the closest entity name mentioned before it (within the same
    entry) is the asked entity; for EXC the scope word must appear in that entity's segment."""
    from cem.qa import _pattern
    if q["qtype"] == "ABSTAIN":
        return True
    pat = _pattern(str(q["gold"]))
    ents = entities or [q["entity"]]
    ent_re = re.compile(r"\b(" + "|".join(re.escape(e) for e in sorted(ents, key=len, reverse=True)) + r")\b", re.I)
    for raw in mem_entries:
        e = re.sub(r"(?<=\d),(?=\d{3}\b)", "", raw)
        for m in pat.finditer(e):
            if q["qtype"] == "NOTE":
                return True
            before = list(ent_re.finditer(e, 0, m.start()))
            if not before or before[-1].group(1).lower() != q["entity"].lower():
                continue
            if q["qtype"] == "EXC" and not _scope_regex(q["scope"]).search(e[max(0, before[-1].start() - 60):m.end() + 30]):
                continue
            return True
    return False


# ---------------------------------------------------------------------------- tables
def fmt(x, pct=True):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{100 * x:.1f}" if pct else f"{x}"


# Files placed in the paper are named by their number there (fig1-3, table1 in the text; A-C supplementary).
FIG_FILES = {"main_online_retention": "fig2_retention", "compaction_k": "fig3_compaction",
             "main_error_breakdown": "figA_error_breakdown", "sweep_budget": "figB_budget_sweep",
             "main_type_heatmap": "figC_type_heatmap"}
TABLE_FILES = {"main_table1_compact": "table1_main", "main_table2_ablation": "table1_ablation",
               "info_types_qwen3.5_9b": "tableA_info_types_9b", "info_types_qwen3.5_4b": "tableB_info_types_4b"}


def write_table(df: pd.DataFrame, out: Path, name: str, note: str = "") -> None:
    out.mkdir(parents=True, exist_ok=True)
    name = TABLE_FILES.get(name, name)
    df.to_csv(out / f"{name}.csv", index=False)
    md = df.to_markdown(index=False)
    (out / f"{name}.md").write_text((note + "\n\n" if note else "") + md + "\n")


def main_tables(rows: pd.DataFrame, d: Path, out: Path, model: str, E: int, B: int, tag: str = "main"):
    R = rows[(rows.model == model) & (rows.E == E) & ((rows.B == B) | (rows.method == "full"))]
    if R.empty:
        return None
    seeds = sorted(R.seed.unique())
    methods = [m for m in ORDER if m in set(R.method)]
    tab, err_rows, dec_rows = [], [], []
    for m in methods:
        X = R[R.method == m]
        lo, hi = boot_macro_ci(X)
        mems = [load_mem(d, model, m, B, E, s) for s in seeds]
        mems = [x for x in mems if x]
        chars = np.mean([x["chars"] for x in mems]) if mems else float("nan")
        raw = np.mean([x.get("raw_chars", 0) for x in mems]) if mems else float("nan")
        calls = np.mean([x["usage"]["calls"] for x in mems]) if mems else float("nan")
        gen = np.mean([x["usage"]["gen_tokens"] for x in mems]) if mems else float("nan")
        secs = np.mean([x["usage"]["seconds"] for x in mems]) if mems else float("nan")
        row = {"방법": NAMES[m]}
        for t in TYPES:
            row[TYPE_KO[t]] = fmt(X[X.qtype == t].correct.mean())
        row["매크로 정확도"] = f"{100 * macro(X):.1f} [{100 * lo:.1f}, {100 * hi:.1f}]"
        row["전체 정확도"] = fmt(X.correct.mean())
        A = X[X.qtype != "ABSTAIN"]
        answered = A[~A.err.isin(["omission"])]
        row["오답률(값 제시·틀림)"] = fmt((~answered.correct).sum() / max(1, len(A)))
        row["응답 정밀도"] = fmt(answered.correct.mean()) if len(answered) else "–"
        row["메모리 글자수"] = "–" if m == "bm25" else f"{chars:.0f}"
        row["압축비(원문/메모리)"] = "–" if m in ("bm25",) or not chars else f"{raw / chars:.1f}×"
        row["압축 LLM 호출"] = "0" if not calls or math.isnan(calls) else f"{calls:.0f}"
        row["압축 생성토큰"] = "0" if not gen or math.isnan(gen) else f"{gen:.0f}"
        row["압축 시간(s)"] = "0" if not secs or math.isnan(secs) else f"{secs:.0f}"
        row["질의 프롬프트 토큰(평균)"] = f"{X.prompt_tokens.mean():.0f}" if "prompt_tokens" in X else "–"
        tab.append(row)
        # errors among all questions
        er = {"방법": NAMES[m], "n": len(X)}
        for e in ERRS:
            er[ERR_KO[e]] = fmt((X.err == e).mean())
        er["정답"] = fmt(X.correct.mean())
        er["복수값(hedge)"] = fmt(X.hedge.mean()) if "hedge" in X else "–"
        err_rows.append(er)
        # storage vs reading decomposition (bound retention), memory-based methods only
        if m not in ("bm25",):
            ans = X[X.qtype != "ABSTAIN"].copy()
            br = []
            for _, q in ans.iterrows():
                mem = load_mem(d, model, m, B, E, q["seed"])
                ents = sorted({f.entity for f in load_episode(d, E, q["seed"]).facts if f.entity != "__note__"})
                br.append(bound_retained(mem["entries"], q, ents) if mem else False)
            ans["bret"] = br
            dec_rows.append({"방법": NAMES[m], "n": len(ans),
                             "보존·정답": fmt((ans.bret & ans.correct).mean()),
                             "보존·오답(읽기 손실)": fmt((ans.bret & ~ans.correct).mean()),
                             "미보존·오답(저장 손실)": fmt((~ans.bret & ~ans.correct).mean()),
                             "미보존·정답": fmt((~ans.bret & ans.correct).mean()),
                             "보존율(엔티티 결합)": fmt(ans.bret.mean()),
                             "보존율(단순 문자열)": fmt(ans.retained.mean())})
    note = (f"모델 {model}, 엔티티 E={E}, 예산 B={B}자, 시드 {seeds} (질문 {len(R[R.method == methods[0]])}개/방법). "
            f"값은 정확도(%). 매크로 = {len(TYPES)}개 질문유형 평균, [95% 군집 부트스트랩 CI].")
    write_table(pd.DataFrame(tab), out / "tables", f"{tag}_accuracy", note)
    write_table(pd.DataFrame(err_rows), out / "tables", f"{tag}_errors", "전체 질문 대비 오류 유형 비율(%).")
    if dec_rows:
        write_table(pd.DataFrame(dec_rows), out / "tables", f"{tag}_decomposition",
                    "응답 가능 질문 대비 비율(%). 보존 = 정답 값이 해당 엔티티 항목 안에 존재(EXC는 범위어 포함).")
    # significance: CEM vs baselines
    if "cem" in methods:
        sig = []
        C = R[R.method == "cem"]
        cmp = [m for m in BASELINES + ["cem_noscope", "cem_nohist", "bm25", "full", "cem_oracle"] if m in methods]
        ps, recs = [], []
        for m in cmp:
            Y = R[R.method == m]
            n10, n01, p = mcnemar(C, Y)
            dpt, dlo, dhi = boot_diff_ci(C, Y)
            recs.append((m, n10, n01, p, dpt, dlo, dhi))
            ps.append(p)
        adj = holm(ps)
        for (m, n10, n01, p, dpt, dlo, dhi), pa in zip(recs, adj):
            sig.append({"비교 (CEM vs)": NAMES[m], "CEM만 정답": n10, "상대만 정답": n01,
                        "McNemar p": f"{p:.2g}", "Holm 보정 p": f"{pa:.2g}",
                        "매크로 차이(%p) [95% CI]": f"{100 * dpt:+.1f} [{100 * dlo:+.1f}, {100 * dhi:+.1f}]"})
        write_table(pd.DataFrame(sig), out / "tables", f"{tag}_significance",
                    "질문 단위 짝비교(시드 통합). 매크로 차이는 짝지은 군집 부트스트랩.")
    return R


def hermes_table(d: Path, out: Path, model: str, E: int, B: int, seeds, tag="main"):
    rows = []
    for m in ("hermes", "hermes_ic"):
        for s in seeds:
            mem = load_mem(d, model, m, B, E, s)
            if not mem:
                continue
            st = mem["stats"]
            r = {"방법": NAMES[m], "seed": s, "세션 수": st.get("sessions"),
                 "최종 글자수": mem["chars"], "항목 수": len(mem["entries"])}
            if m == "hermes":
                r.update({"도구 호출": st.get("tool_calls"), "실패 호출": st.get("failed_calls"),
                          "용량초과 오류": st.get("overflow_errors"), "무호출 세션": st.get("silent_sessions")})
            else:
                r.update({"도구 호출": st.get("batches"), "실패 호출": st.get("failed_batches"),
                          "용량초과 오류": st.get("overflow_errors"), "무호출 세션": st.get("empty_batches")})
            et = st.get("error_types", {})
            r["용량초과 오류"] = sum(v for k, v in et.items() if "would put memory" in k or "would exceed" in k)
            r["세션당 최대 손실(자)"] = max([0] + [sum(map(len, a)) - sum(map(len, b))
                                             for a, b in zip(mem.get("trace", [])[:-1], mem.get("trace", [])[1:])])
            r["LLM 호출"] = mem["usage"]["calls"]
            r["주요 실패 메시지"] = "; ".join(f"{k}({v})" for k, v in
                                       sorted(st.get("error_types", {}).items(), key=lambda x: -x[1])[:2])
            rows.append(r)
    if rows:
        write_table(pd.DataFrame(rows), out / "tables", f"{tag}_hermes_ops", "Hermes 실제 memory_tool 구동 통계.")


def extraction_table(d: Path, out: Path, model: str, E: int, seeds, tag="main"):
    """CEM stage-1 quality vs ground truth: value recall, scope agreement, rejected-value leakage."""
    from cem.cem import _norm, DEFAULT_SCOPES
    slug = model.replace(":", "_")
    rows = []
    for s in seeds:
        p = d / "memories" / slug / f"cem_records_E{E}_s{s}.json"
        if not p.exists():
            continue
        dd = json.loads(p.read_text())
        recs = [r for r in dd["records"] if "misc" not in r]
        ep = load_episode(d, E, s)
        by_t = defaultdict(list)
        for r in recs:
            by_t[r["t"]].append(r)
        gt = [f for f in ep.facts if f.kind in ("init", "update", "exception", "revert", "restate")]
        hit = scope_ok = 0
        for f in gt:
            cands = [r for r in by_t[f.t] if re.search(r"(?<![\w.])" + re.escape(f.core.split("-")[-1]) + r"(?![\w])",
                                                         r["value"].replace(",", ""))]
            if cands:
                hit += 1
                r = cands[0]
                is_def = _norm(r["scope"]) in DEFAULT_SCOPES
                scope_ok += int(is_def == (f.scope == "default"))
        rej = [f for f in ep.facts if f.kind == "rejected"]
        leak = sum(1 for f in rej if any(re.search(r"(?<![\w.])" + re.escape(f.core.split("-")[-1]) + r"(?![\w])",
                                                   r["value"].replace(",", "")) for r in by_t[f.t]))
        st = dd["stats"]
        rows.append({"seed": s, "정답 사실 수": len(gt), "값 재현율": fmt(hit / max(1, len(gt))),
                     "범위(기본/예외) 일치율": fmt(scope_ok / max(1, hit)),
                     "기각값 유입": f"{leak}/{len(rej)}", "근거불일치 제거": st.get("ungrounded", 0),
                     "LLM 호출": st.get("calls"), "파싱 오류": st.get("parse_errors"),
                     "추출 시간(s)": st.get("wall_s")})
    if rows:
        write_table(pd.DataFrame(rows), out / "tables", f"{tag}_cem_extraction", "CEM 1단계(LLM 추출) 품질.")


def family_table(R: pd.DataFrame, out: Path, tag="main"):
    """Accuracy by note family of the asked key (base / synonym / rejected-proposal / revert)."""
    if "family" not in R:
        return
    R = R[R.qtype.isin(["CUR", "STABLE", "PREV", "EXC", "EXCNEG"])].copy()
    R["fam"] = R.family.map(lambda f: "rev" if "rev" in f else "rej" if "rej" in f else "syn" if "syn" in f else "base")
    lab = {"base": "기본", "syn": "동의어 포함", "rej": "기각 제안 포함", "rev": "되돌림 포함"}
    tab = []
    for m in [m for m in ORDER if m in set(R.method)]:
        X = R[R.method == m]
        row = {"방법": NAMES[m]}
        for f in ("base", "syn", "rej", "rev"):
            Y = X[X.fam == f]
            row[f"{lab[f]} (n={len(Y) // max(1, X.seed.nunique())}/시드)"] = fmt(Y.correct.mean()) if len(Y) else "–"
        tab.append(row)
    write_table(pd.DataFrame(tab), out / "tables", f"{tag}_by_family",
                "질문 대상 키의 메모 계열별 정확도(%), CUR/STABLE/PREV/EXC/EXCNEG 질문.")


def compact_tables(R: pd.DataFrame, out: Path, tag="main"):
    """Paper-sized versions of Table 1: main comparison and ablations."""
    def row(m):
        X = R[R.method == m]
        A = X[X.qtype != "ABSTAIN"]
        answered = A[~A.err.isin(["omission"])]
        return {"방법": SHORT[m], "현재": fmt(X[X.qtype.isin(["CUR", "STABLE"])].correct.mean()),
                "직전": fmt(X[X.qtype == "PREV"].correct.mean()), "예외": fmt(X[X.qtype == "EXC"].correct.mean()),
                "전체": fmt(X.correct.mean()), "매크로": fmt(macro(X)),
                "오답률": fmt((~answered.correct).sum() / max(1, len(A))),
                "질의 토큰": f"{X.prompt_tokens.mean():.0f}" if "prompt_tokens" in X else "–"}
    main_m = [m for m in ["full", "bm25", "recency", "reject", "summary", "struct", "hermes", "hermes_ic", "cem"]
              if m in set(R.method)]
    abl_m = [m for m in ["cem", "cem_nohist", "cem_noscope", "cem_llmmerge", "cem_oracle"] if m in set(R.method)]
    seeds = sorted(R.seed.unique())
    note = (f"정확도(%). 현재=CUR+STABLE, 오답률=값을 제시했으나 틀린 비율(모름 제외), 질의 토큰=질문당 평균 입력 토큰. "
            f"시드 {list(map(int, seeds))}, 질문 {len(R[R.method == 'cem']) if 'cem' in set(R.method) else '?'}개/방법.")
    write_table(pd.DataFrame([row(m) for m in main_m]), out / "tables", f"{tag}_table1_compact", note)
    write_table(pd.DataFrame([row(m) for m in abl_m]), out / "tables", f"{tag}_table2_ablation", note)


# ---------------------------------------------------------------------------- figures
FIG_LABEL = {"full": "Full context", "bm25": "BM25", "recency": "Recency", "reject": "Hermes, no consolidation",
             "summary": "Summary", "struct": "Structured summary", "hermes": "Hermes agent",
             "hermes_ic": "Hermes agent (JSON)", "cem": "CEM", "cem_nohist": "CEM w/o history",
             "cem_noscope": "CEM w/o scope", "cem_llmmerge": "CEM w/ LLM merge", "cem_oracle": "CEM (oracle)"}
TYPE_EN = {"CUR": "Current", "STABLE": "Stable", "PREV": "Previous", "EXC": "Exception", "EXCNEG": "No exception",
           "NOTE": "Note", "ABSTAIN": "Abstain"}
ERR_EN = {"omission": "Omission", "version": "Wrong version", "scope": "Wrong scope", "attribute": "Wrong attribute",
          "entity": "Wrong entity", "rejected": "Rejected value", "fabricated": "Unsupported value",
          "hallucination": "Failed to abstain"}
MCOLOR = {"cem": "C0", "summary": "C1", "struct": "C2", "hermes": "C3", "recency": "C4", "bm25": "C5",
          "cem_oracle": "C0", "hermes_ic": "C6", "full": "C7", "cem_llmmerge": "C8"}
MMARK = {"cem": "o", "cem_oracle": "s", "summary": "^", "struct": "v", "hermes": "D", "recency": "x", "bm25": "*"}
GROUPS = [("full", "bm25"), ("recency", "reject", "summary", "struct", "hermes", "hermes_ic"),
          ("cem_llmmerge", "cem_noscope", "cem_nohist"), ("cem", "cem_oracle")]


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    plt.rcParams["savefig.dpi"] = 300
    return plt


def save(fig, out: Path, name: str):
    (out / "figures").mkdir(parents=True, exist_ok=True)
    name = FIG_FILES.get(name, name)
    fig.savefig(out / "figures" / f"{name}.png", bbox_inches="tight")
    fig.savefig(out / "figures" / f"{name}.pdf", bbox_inches="tight")


def fig_heatmap(R: pd.DataFrame, out: Path, tag="main"):
    plt = setup_mpl()
    methods = [m for m in ORDER if m in set(R.method)]
    M = np.array([[R[(R.method == m) & (R.qtype == t)].correct.mean() for t in TYPES] for m in methods]) * 100
    fig, ax = plt.subplots(figsize=(6.4, 0.32 * len(methods) + 1.0))
    im = ax.imshow(M, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(TYPES)))
    ax.set_xticklabels([TYPE_EN[t] for t in TYPES], rotation=30, ha="right")
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels([FIG_LABEL[m] for m in methods])
    for i in range(len(methods)):
        for j in range(len(TYPES)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=8,
                        color="black" if M[i, j] > 50 else "white")
    pos = 0
    for g in GROUPS[:-1]:                       # thin separators: references | baselines | ablations | CEM
        pos += sum(1 for m in g if m in methods)
        ax.axhline(pos - 0.5, color="white", lw=2)
    fig.colorbar(im, ax=ax, label="Accuracy (%)")
    fig.tight_layout()
    save(fig, out, f"{tag}_type_heatmap")
    plt.close(fig)


def fig_errors(R: pd.DataFrame, out: Path, tag="main"):
    plt = setup_mpl()
    methods = [m for m in ORDER if m in set(R.method)]
    cats = [("Omission", ["omission"]), ("Wrong version", ["version"]), ("Wrong scope", ["scope"]),
            ("Other", ["attribute", "entity", "rejected", "fabricated", "hallucination"])]
    fig, ax = plt.subplots(figsize=(6.4, 0.3 * len(methods) + 1.2))
    left = np.zeros(len(methods))
    for lab, es in cats:
        vals = np.array([100 * R[R.method == m].err.isin(es).mean() for m in methods])
        ax.barh(range(len(methods)), vals, left=left, label=lab)
        left += vals
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels([FIG_LABEL[m] for m in methods])
    ax.invert_yaxis()
    ax.set_xlim(0, 80)
    ax.set_xlabel("Errors (% of questions)")
    ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    fig.tight_layout()
    save(fig, out, f"{tag}_error_breakdown")
    plt.close(fig)


def fig_sweep(rows: pd.DataFrame, out: Path, model: str, x: str, fixed: dict, name: str, xlabel: str,
              methods=("cem", "summary", "struct", "hermes", "recency", "cem_oracle", "bm25")):
    plt = setup_mpl()
    R = rows[rows.model == model]
    for k, v in fixed.items():
        R = R[R[k] == v]
    if R.empty:
        return
    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    for m in methods:
        X = R[R.method == m]
        if X.empty:
            continue
        xs = sorted(X[x].unique())
        ys = [100 * macro(X[X[x] == v]) for v in xs]
        ax.plot(xs, ys, "--" if m in ("cem_oracle", "bm25") else "-", marker=MMARK.get(m, "o"),
                mfc="none" if m == "cem_oracle" else None, color=MCOLOR.get(m), label=FIG_LABEL[m])
    ax.set_xticks(sorted(R[x].unique()))
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Macro accuracy (%)")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()
    save(fig, out, name)
    plt.close(fig)


def sweep_table(rows: pd.DataFrame, out: Path, model: str, x: str, fixed: dict, name: str):
    R = rows[rows.model == model]
    for k, v in fixed.items():
        R = R[R[k] == v]
    if R.empty:
        return
    xs = sorted(R[x].unique())
    tab = []
    for m in [m for m in ORDER if m in set(R.method)]:
        row = {"방법": NAMES[m]}
        for v in xs:
            X = R[(R.method == m) & (R[x] == v)]
            row[f"{x}={v}"] = fmt(macro(X)) if len(X) else "–"
        tab.append(row)
    fixed_txt = ", ".join(f"{k}={v}" for k, v in fixed.items())
    write_table(pd.DataFrame(tab), out / "tables", name,
                f"매크로 정확도(%) — {x} 변화 ({fixed_txt}), 모델 {model}, 시드 1(148문항). "
                f"B=2200 값은 시드 1만이라 표 1(시드 1–3)과 다르다.")


def xmodel_table(rows: pd.DataFrame, out: Path, E: int, B: int, name="xmodel_accuracy"):
    R = rows[(rows.E == E) & ((rows.B == B) | (rows.method == "full"))]
    if R.empty:
        return
    models = sorted(R.model.unique())
    for suffix, RR in (("", R), ("_seed1", R[R.seed == 1])):
        tab = []
        for m in [m for m in ORDER if m in set(RR.method)]:
            row = {"방법": NAMES[m]}
            for mo in models:
                X = RR[(RR.method == m) & (RR.model == mo)]
                row[f"{mo} 전체"] = fmt(X.correct.mean()) if len(X) else "–"
                row[f"{mo} 매크로"] = fmt(macro(X)) if len(X) else "–"
            tab.append(row)
        seeds = {mo: sorted(map(int, RR[RR.model == mo].seed.unique())) for mo in models}
        write_table(pd.DataFrame(tab), out / "tables", name + suffix,
                    f"모델별 정확도(%), E={E}, B={B}. 사용 시드: {seeds}")


# ---------------------------------------------------------------------------- online retention
def _present(entries: list[str], entity: str, core: str, ents: list[str] | None = None) -> bool:
    return bound_retained(entries, {"qtype": "CUR", "gold": core, "entity": entity, "scope": "default"}, ents)


def online_retention(d: Path, model: str, E: int, B: int, seed: int) -> dict[str, list[float]]:
    """Per session: share of currently-valid facts (defaults + exceptions) learned so far that are
    present (entity-bound) in memory. Hermes uses its saved per-session trace; CEM/Oracle are replayed."""
    from cem import cem as C
    from cem import methods as M
    ep = load_episode(d, E, seed)
    ents = sorted({f.entity for f in ep.facts if f.entity != "__note__"})
    last_note = [s["notes"][-1] for s in ep.sessions]
    curves: dict[str, list[float]] = {}
    gt_by_sess = []
    for ln in last_note:
        cur: dict[tuple, str] = {}
        for f in sorted(ep.facts, key=lambda f: f.t):
            if f.t > ln or f.kind in ("rejected", "note"):
                continue
            cur[(f.entity, f.attr, f.scope)] = f.core
        gt_by_sess.append(cur)
    for m in ("hermes", "hermes_ic"):
        mem = load_mem(d, model, m, B, E, seed)
        if mem and mem.get("trace"):
            curves[m] = [np.mean([_present(tr, k[0], v, ents) for k, v in gt.items()]) if gt else 1.0
                         for tr, gt in zip(mem["trace"], gt_by_sess)]
    slug = model.replace(":", "_")
    rp = d / "memories" / slug / f"cem_records_E{E}_s{seed}.json"
    srcs = {"cem_oracle": C.oracle_records(ep)}
    if rp.exists():
        srcs["cem"] = json.loads(rp.read_text())["records"]
    for m, recs in srcs.items():
        ys = []
        for ln, gt in zip(last_note, gt_by_sess):
            r = C.cem_from_records([x for x in recs if x["t"] <= ln], B)
            ys.append(np.mean([_present(r["entries"], k[0], v, ents) for k, v in gt.items()]) if gt else 1.0)
        curves[m] = ys
    ys = []
    for ln, gt in zip(last_note, gt_by_sess):
        sub = type(ep)(ep.seed, ep.n_entities, ep.notes[:ln + 1], ep.facts, ep.questions, ep.sessions)
        ys.append(np.mean([_present(M.recency(sub, B)["entries"], k[0], v, ents) for k, v in gt.items()]) if gt else 1.0)
    curves["recency"] = ys
    return curves


def fig_online(d: Path, out: Path, model: str, E: int, B: int, seeds, tag="main"):
    plt = setup_mpl()
    allc = defaultdict(list)
    for s in seeds:
        for m, ys in online_retention(d, model, E, B, s).items():
            allc[m].append(ys)
    if not allc:
        return
    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    rows = []
    grid = np.linspace(5, 100, 39)
    for m in ("cem", "cem_oracle", "hermes", "hermes_ic", "recency"):
        if m not in allc:
            continue
        Y = np.array([np.interp(grid, (np.arange(len(y)) + 1) / len(y) * 100, y) for y in allc[m]]) * 100
        ax.plot(grid, Y.mean(0), "--" if m == "cem_oracle" else "-", color=MCOLOR.get(m), label=FIG_LABEL[m])
        rows.append({"방법": NAMES[m], **{f"{q}%": f"{np.interp(q, grid, Y.mean(0)):.1f}" for q in (25, 50, 75, 100)}})
    ax.set_xlim(0, 100)
    ax.set_xlabel("Sessions processed (%)")
    ax.set_ylabel("Valid facts retained (%)")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()
    save(fig, out, f"{tag}_online_retention")
    plt.close(fig)
    write_table(pd.DataFrame(rows), out / "tables", f"{tag}_online_retention",
                f"세션 진행에 따른 유효 사실(현재 기본값+예외) 보존율(%), 엔티티 결합 기준, 시드 {list(map(int, seeds))} 평균.")


# ---------------------------------------------------------------------------- Exp 2: repeated compaction
INFO_TYPES = ["설정값(현재)", "변경 이력(직전값)", "예외 조건", "결정(기각 후 유지)", "교훈·명령 메모"]


def info_type(q) -> str:
    if q["qtype"] in ("CUR", "STABLE"):
        return "결정(기각 후 유지)" if "rej" in str(q.get("family", "")) else "설정값(현재)"
    return {"PREV": "변경 이력(직전값)", "EXC": "예외 조건", "NOTE": "교훈·명령 메모"}.get(q["qtype"], "")


def value_kind(gold: str) -> str:
    g = str(gold)
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", g) or g.startswith("release-"):
        return "식별자(IP·브랜치)"
    if re.fullmatch(r"\d{1,2}:\d{2}", g):
        return "시각"
    return "수치"


def info_type_table(rows: pd.DataFrame, d: Path, out: Path, model: str, methods: list[str], name: str):
    """Accuracy and entity-bound retention by information type (semantic and value kind)."""
    R = rows[(rows.model == model) & (rows.E == 24) & (rows.method.isin(methods))]
    R = R[R.qtype != "ABSTAIN"].copy()
    if R.empty:
        return
    R["itype"] = [info_type(r) for _, r in R.iterrows()]
    R["vkind"] = [value_kind(r["gold"]) for _, r in R.iterrows()]
    ents_by_seed = {}
    br = []
    for _, r in R.iterrows():
        if r["seed"] not in ents_by_seed:
            ents_by_seed[r["seed"]] = sorted({f.entity for f in load_episode(d, 24, r["seed"]).facts if f.entity != "__note__"})
        mem = load_mem(d, model, r["method"], r["B"] or 2200, 24, r["seed"])
        br.append(bound_retained(mem["entries"], r, ents_by_seed[r["seed"]]) if mem and r["method"] != "bm25" else np.nan)
    R["bret"] = br
    tab = []
    for m in [m for m in methods if m in set(R.method)]:
        X = R[R.method == m]
        row = {"방법": NAMES.get(m, m)}
        for t in INFO_TYPES:
            Y = X[X.itype == t]
            row[f"{t} 정답/보존"] = f"{fmt(Y.correct.mean())} / {fmt(Y.bret.mean())}" if len(Y) else "–"
        for v in ["수치", "식별자(IP·브랜치)", "시각"]:
            Y = X[(X.vkind == v) & (X.itype != "교훈·명령 메모")]
            row[f"{v} 정답"] = fmt(Y.correct.mean()) if len(Y) else "–"
        tab.append(row)
    seeds = sorted(map(int, R.seed.unique()))
    write_table(pd.DataFrame(tab), out / "tables", name,
                f"정보 유형별 정답률/보존율(%) — {model}, E=24, 시드 {seeds}. 보존 = 정답 값이 해당 엔티티 항목 안에 존재.")


def compaction_analysis(rows: pd.DataFrame, d: Path, out: Path):
    ks = [1, 3, 5, 10]
    recs, curves = [], {}
    for model in sorted(rows.model.unique()):
        R = rows[(rows.model == model) & (rows.E == 24)]
        if not any((R.method == f"compact{k}").any() for k in ks):
            continue
        cem_m = "cem_ledger" if (R.method == "cem_ledger").any() else "cem"
        seeds = set(R[R.method == cem_m].seed)
        for k in ks:                                    # only seeds where every k (and the ledger) finished
            seeds &= set(R[R.method == f"compact{k}"].seed)
        seeds = sorted(seeds)
        R = R[R.seed.isin(seeds)]
        for k in ks:
            X = R[R.method == f"compact{k}"]
            if X.empty:
                continue
            mems = [load_mem(d, model, f"compact{k}", 2200, 24, s) for s in seeds]
            mems = [m for m in mems if m]
            ptok = np.mean([m["usage"]["prompt_tokens"] for m in mems])
            gtok = np.mean([m["usage"]["gen_tokens"] for m in mems])
            chars = np.mean([m["chars"] for m in mems])
            recs.append({"모델": model, "방식": "요약본 재압축(Hermes 반복 압축)", "압축 횟수 k": k,
                         "전체 정확도": fmt(X.correct.mean()), "매크로": fmt(macro(X)),
                         "현재값": fmt(X[X.qtype.isin(["CUR", "STABLE"])].correct.mean()),
                         "직전값": fmt(X[X.qtype == "PREV"].correct.mean()), "예외값": fmt(X[X.qtype == "EXC"].correct.mean()),
                         "요약 글자수": f"{chars:.0f}", "압축 입력토큰(누적)": f"{ptok:.0f}", "압축 출력토큰": f"{gtok:.0f}"})
            curves.setdefault((model, "rolling"), []).append((k, 100 * X.correct.mean()))
        X1 = R[R.method == "compact1"]
        m1 = [load_mem(d, model, "compact1", 2200, 24, s) for s in seeds]
        p1 = np.mean([m["usage"]["prompt_tokens"] for m in m1 if m])
        for k in ks:
            est = sum((i + 1) / k for i in range(k)) * p1
            recs.append({"모델": model, "방식": "원본 참조 재압축", "압축 횟수 k": k,
                         "전체 정확도": fmt(X1.correct.mean()), "매크로": fmt(macro(X1)),
                         "현재값": fmt(X1[X1.qtype.isin(["CUR", "STABLE"])].correct.mean()),
                         "직전값": fmt(X1[X1.qtype == "PREV"].correct.mean()), "예외값": fmt(X1[X1.qtype == "EXC"].correct.mean()),
                         "요약 글자수": "(k=1과 동일)", "압축 입력토큰(누적)": f"{est:.0f} (추정)", "압축 출력토큰": "–"})
            curves.setdefault((model, "source"), []).append((k, 100 * X1.correct.mean()))
        C = R[R.method == cem_m]
        cm = [load_mem(d, model, cem_m, 2200, 24, s) for s in seeds]
        cp = np.mean([m["usage"]["prompt_tokens"] for m in cm if m])
        cg = np.mean([m["usage"]["gen_tokens"] for m in cm if m])
        for k in ks:
            recs.append({"모델": model, "방식": "CEM (사실 원장 재렌더링)", "압축 횟수 k": k,
                         "전체 정확도": fmt(C.correct.mean()), "매크로": fmt(macro(C)),
                         "현재값": fmt(C[C.qtype.isin(["CUR", "STABLE"])].correct.mean()),
                         "직전값": fmt(C[C.qtype == "PREV"].correct.mean()), "예외값": fmt(C[C.qtype == "EXC"].correct.mean()),
                         "요약 글자수": f"{np.mean([m['chars'] for m in cm if m]):.0f}",
                         "압축 입력토큰(누적)": f"{cp:.0f}", "압축 출력토큰": f"{cg:.0f}"})
            curves.setdefault((model, "cem"), []).append((k, 100 * C.correct.mean()))
    if not recs:
        return
    write_table(pd.DataFrame(recs), out / "tables", "compaction_k",
                "반복 압축 횟수 k에 따른 정확도(%)와 비용. 요약본 재압축 = Hermes ContextCompressor의 실제 반복 갱신 프롬프트"
                "(PREVIOUS SUMMARY + NEW TURNS, FOCUS TOPIC 사용). 원본 참조 = 매번 원본 전체를 새로 요약(최종 요약은 k=1과 동일, "
                "입력 토큰은 k=1 실측 × Σ(i/k)로 추정). CEM은 원본에서 추출한 사실 원장을 다시 렌더링하므로 k와 무관.")
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    style = {"rolling": ("-", "C3", "Hermes rolling"), "source": (":", "C7", "From source (= k=1)"),
             "cem": ("--", "C0", "CEM ledger (no limit)")}
    mark = {"qwen3.5:9b": "o", "qwen3.5:4b": "s"}
    for (model, kind), pts in sorted(curves.items(), key=lambda kv: (kv[0][1] != "rolling", kv[0][0])):
        xs, ys = zip(*pts)
        ls, col, lab = style[kind]
        ax.plot(xs, ys, ls, color=col, marker=mark.get(model) if kind == "rolling" else None,
                label=f"{lab}, {model.split(':')[1].upper()}")
    ax.set_xticks(ks)
    ax.set_xlabel("Number of compactions k")
    ax.set_ylabel("Overall accuracy (%)")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()
    save(fig, out, "compaction_k")
    plt.close(fig)
    for model in sorted(rows.model.unique()):
        ms = [f"compact{k}" for k in ks] + ["cem_ledger", "summary", "struct", "hermes", "cem", "full"]
        R = rows[(rows.model == model) & (rows.E == 24)]
        seeds = set(R[R.method == "cem_ledger"].seed)
        for k in ks:
            seeds &= set(R[R.method == f"compact{k}"].seed)
        info_type_table(rows[rows.seed.isin(seeds) | ~rows.method.isin(ms[:5])], d, out, model, ms,
                        f"info_types_{model.replace(':', '_')}")


def figures_only(allrows, rows, d: Path, out: Path, args):
    """Regenerate every data figure (their companion tables are rewritten with identical values)."""
    R = rows[(rows.model == args.model) & (rows.E == args.E) & ((rows.B == args.B) | (rows.method == "full"))]
    seeds = sorted(R.seed.unique())
    fig_heatmap(R, out, args.tag)
    fig_errors(R, out, args.tag)
    fig_online(d, out, args.model, args.E, args.B, seeds, args.tag)
    sw = allrows[(allrows.model == args.model) & ~allrows.method.str.startswith("compact")
                 & (allrows.method != "cem_ledger")]
    full = sw[sw.method == "full"]
    sw = pd.concat([sw[sw.method != "full"]] + [full.assign(B=b) for b in sorted(sw[sw.method != "full"].B.unique())])
    fig_sweep(sw[sw.seed == 1], out, args.model, "B", {"E": args.E}, "sweep_budget", "Memory budget (characters)")
    compaction_analysis(allrows, d, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="../results/main", help="results dir (all runs live here)")
    ap.add_argument("--model", default="qwen3.5:9b")
    ap.add_argument("--E", type=int, default=24)
    ap.add_argument("--B", type=int, default=2200)
    ap.add_argument("--out", default="../paper")
    ap.add_argument("--tag", default="main")
    ap.add_argument("--seeds", type=int, nargs="*", default=None, help="restrict the main table to these seeds")
    ap.add_argument("--skip", nargs="*", default=[], help="sections to skip: main sweep xmodel online")
    ap.add_argument("--figures-only", action="store_true", help="regenerate figures only (their companion tables are rewritten with identical values)")
    args = ap.parse_args()
    out = Path(args.out)
    d = Path(args.main)
    allrows = load_rows(d)
    rows = allrows[allrows.seed.isin(args.seeds)] if args.seeds else allrows
    if args.figures_only:
        figures_only(allrows, rows, d, out, args)
        return
    if "main" not in args.skip:
        R = main_tables(rows, d, out, args.model, args.E, args.B, args.tag)
        if R is not None:
            seeds = sorted(R.seed.unique())
            hermes_table(d, out, args.model, args.E, args.B, seeds, args.tag)
            extraction_table(d, out, args.model, args.E, seeds, args.tag)
            fig_heatmap(R, out, args.tag)
            fig_errors(R, out, args.tag)
            if "online" not in args.skip:
                fig_online(d, out, args.model, args.E, args.B, seeds, args.tag)
            family_table(R, out, args.tag)
            compact_tables(R, out, args.tag)
    if "sweep" not in args.skip:
        sw = allrows[(allrows.model == args.model) & ~allrows.method.str.startswith("compact")
                     & (allrows.method != "cem_ledger")]
        full = sw[sw.method == "full"]
        exp = [full.assign(B=b) for b in sorted(sw[sw.method != "full"].B.unique())]   # full is budget-free
        sw = pd.concat([sw[sw.method != "full"]] + exp)
        s1 = sw[sw.seed == 1]          # sweeps were run on seed 1 only
        sweep_table(s1, out, args.model, "B", {"E": args.E}, "sweep_budget")
        fig_sweep(s1, out, args.model, "B", {"E": args.E}, "sweep_budget", "Memory budget (characters)")
    if "xmodel" not in args.skip:
        xmodel_table(allrows, out, args.E, args.B)
    if "compaction" not in args.skip:
        compaction_analysis(allrows, d, out)


if __name__ == "__main__":
    main()
