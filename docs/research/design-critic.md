# Critique of the CEM / Hermes memory-compression study: threats, fixes, 6 GPU-hour matrix, claims

## 0. Repo facts the plan doesn't account for yet (hermes-agent @ 67481b6)
1. **Budget counting.** `MemoryStore._char_count` = `len("\n§\n".join(entries))`. It counts Python code points, includes the 3-char delimiter and excludes the header and usage line (`tools/memory_tool_store.py` L25, L309; `_render_block` L638).
2. **Frozen snapshot.** `format_for_system_prompt` returns the snapshot captured at load (L618). Each session needs a fresh store/load. Otherwise the agent sees live state, which real Hermes never does.
3. **Retry cap.** `_MAX_CONSOLIDATION_FAILURES_PER_TURN = 3` (L184), reset per turn via `reset_consolidation_failures()`. The `FAILURE_CLASS` contextvar (over_budget, retry_cap, no-match...) gives a free failure taxonomy for the Hermes baseline.
4. **Responses.** Success responses deliberately do not echo entries. Errors do (`current_entries`).
5. **Design intent.** `MEMORY_SCHEMA` (`tools/memory_tool.py` L373) and `build_memory_guidance` (`agent/prompt_builder.py` L192) say memory is only for facts that apply to EVERY session, and to SKIP "easily re-discovered facts, raw data dumps".
   - The routing block in `agent/background_review.py` (L370-389) does put "paths and endpoints that matter, config gotchas" in MEMORY.md.
   - The real write trigger is `_MEMORY_REVIEW_PROMPT` (L383), which allows "Nothing to save."
6. **Threat scan.** `_scan_memory_content` (strict scope) rejects patterns such as `send|upload ... to https://`, `~/.ssh` and `authorized_keys`. Synthetic infra notes could trip it.
7. **Retrieval exists.** Hermes's `session_search` is FTS5/BM25 over past sessions (`tools/session_search_tool.py`). A BM25-over-raw baseline is therefore the Hermes-native retrieval analog, not an outside strawman.

## 1. Threats to validity and fixes
Format: ID, priority, issue → fix. Unless noted, each fix needs no GPU and is a few dozen lines of code.

### A. Data and construct validity
- **A1 [MUST] The data has the same shape as CEM's schema.** The generator emits (entity, attribute, value, scope) tuples, which is exactly what CEM extracts. A reviewer will say the benchmark was built for the method.
  - Fix: about 25% of notes come from "schema-breaking" families, each tagged with its family:
    - multi-fact notes (2 attributes, or 2 entities, in one sentence);
    - an entity alias declared once ("the primary DB" = db-03) and used later;
    - attribute synonyms ("listen port", "bound to");
    - relative dates ("two days after the Mar-3 change");
    - rejected or hypothetical changes ("considered 41873, kept 41022");
    - one retraction ("reverted the port change").
  - Also add about 15% free-text convention/quirk facts with a unique codeword (QA type NOTE) that do not fit the KV schema. This measures what CEM drops.
  - Report accuracy per note family.
- **A2 [MUST] Template artifacts.**
  - "Changed from A to B" gives PREV for free. → Half of updates omit the old value.
  - Restatements are verbatim, so trivially dedupable. → Paraphrase and reformat them (":41022" vs "port 41022").
  - Stream order equals time order. → About 10% of notes are logged late with an explicit earlier date; ground truth uses the effective date.
  - Use at least 5 templates per note type.
- **A3 [MUST] Questions reuse note wording.**
  - Use disjoint template pools for notes and questions, plus synonym maps for attributes and scopes.
  - Ask CUR and STABLE with the same wording so the question type isn't signaled.
  - Add EXC-NEG questions: a scope with no exception, where the correct answer is the default value. This catches exceptions applied where they shouldn't be.
  - Log the token Jaccard between each question and its gold note, and report accuracy by overlap tercile. This mainly affects BM25 and full-context.
- **A4 [SHOULD] Guessable values.** Use non-standard values (ports 40000-49999, 10.x.y.z, HH:MM like 03:17) so world knowledge can't produce correct guesses.
- **A5 [MUST] Threat-scan confound.** Run `_scan_memory_content` over every generated note and fact, and resample any that hit. Otherwise Hermes-native is penalized by security rejections that have nothing to do with consolidation.
- **A6 [SHOULD] Type weighting favors CEM.** Two of five QA types are CEM's targets.
  - Pre-declare the primary metric: macro accuracy over CUR/STABLE/PREV/EXC/EXC-NEG/ABSTAIN/NOTE.
  - Also report a natural-mix score, with weights proportional to how often each fact type occurs in the data.
  - Always show CUR/STABLE separately, to show CEM is not traded off there.

### B. Baselines and fairness
- **B1 [MUST] Structured-KV summary, one-shot.**
  - Same LLM, same priority instruction, output in an `entity: attr=val; prev=...; [scope]=val` format.
  - Without it, any CEM gain can be attributed to the format rather than the deterministic merger.
- **B2 [MUST] BM25 over raw notes, at query time.**
  - Take the top-k notes until B chars, re-sorted chronologically with dates shown.
  - Label it query-dependent, compare at equal reader-context chars, and cite session_search.
- **B3 [MUST] CEM-LLMmerge (Mem0-style).**
  - Same extracted facts as CEM. Per chunk, the LLM gets the touched entity entries plus the new facts and returns updated entries as JSON.
  - This is the direct test of claim (b), with extraction held constant. It reuses CEM's extraction, at about 37 calls per dataset.
- **B4 [MUST] Prompt-development parity.**
  - Tune all prompts on dev seed 0 only, then freeze them. Log a prompt hash in every output row.
  - Every LLM baseline gets the same priority statement (current > exceptions > previous) that CEM's tiers encode.
  - Same overflow handling for all: up to 2 "too long, shorten to ≤B chars" retries, then truncate at a line or entry boundary. Report the overflow rate.
- **B5 [MUST] Silent context truncation.** Ollama truncates prompts beyond `num_ctx` without warning, which would cripple the one-shot summary and full-context.
  - Fix `num_ctx` per model (e.g., 16384). Do not vary it between calls, or Ollama reloads the model.
  - Assert that `prompt_eval_count` ≥ the expected token count.
- **B6 [MUST] Decoding settings.**
  - qwen3.5: `think:false` everywhere, temperature 0, fixed `seed` option, same `num_predict` cap.
  - Log `eval_count`, to report cost and catch hidden thinking.
- **B7 [SHOULD] Dedup + recency.** Remove normalized duplicates, then truncate by recency. No GPU. It shows how much of the "compression" is only redundancy removal.
- **B8 [COULD] Regex template probe.** A rule extractor built from the generator's templates, fed into the CEM merger.
  - If it nearly matches Oracle on base templates but fails on the A1 families, that shows the hard slices are not template-solvable.
- **B9 [COULD] Rolling free-text summary.** Cost-matched to CEM's call count. Hermes-IC and CEM-LLMmerge already partly cover this.

### C. Hermes-native fidelity
- **C1 [MUST] Two Hermes variants**, to separate tool-call syntax failures from consolidation policy.
  - **Hermes-F (faithful):** real guidance plus `MEMORY_SCHEMA` through native Ollama tools, with `_MEMORY_REVIEW_PROMPT` verbatim after each session.
  - **Hermes-IC (instructed + constrained):**
    - the user turn says "remember all of these" with the same priority statement;
    - the output is constrained by Ollama `format` to `{operations:[{action,content?,old_text?}]}` (an empty list is allowed);
    - the parsed operations go to the real `memory_tool()`, and errors are fed back.
  - Log for both: tool-call validity, saves per session, rounds per session, and a `FAILURE_CLASS` histogram.
  - Hermes-F vs Hermes-IC measures the syntax and instruction effect; Hermes-IC vs CEM measures consolidation policy.
- **C2 [MUST] Session semantics.**
  - New store/load per session, so the frozen snapshot is injected into the system prompt.
  - `reset_consolidation_failures()` per turn; at most 4 tool rounds per session.
  - Sessions of about 8-10 notes, presented as user dialog.
- **C3 [MUST] Design-intent mismatch.** Faithful Hermes may rationally skip per-service values, given the schema's WHEN/SKIP text.
  - Frame the notes as environment facts ("endpoints/config that matter") and state this in the paper.
  - Never claim "Hermes is bad". The claim is about agent-driven consolidation by ≤9B models.
- **C4 [MUST] Scope of the claim.** The study drives MemoryStore, the schema and the guidance at commit 67481b6 through a minimal harness, not the full AIAgent loop (which needs 64K context). Say so explicitly.
- **C5 [SHOULD] Collateral-loss instrumentation.**
  - Before and after every applied op, compute retention over all ground-truth values.
  - Attribute each disappearance to the op type (add/patch/remove), and to intended (superseded) vs collateral.
  - No GPU needed. This ties directly to the documented removal of `replace`.

### D. Measurement and scoring
- **D1 [MUST] JSON answers.**
  - Answer schema via `format`: `{"answer": str, "unknown": bool}`.
  - Normalize per value type: port as int, IP, HH:MM (including "9:00" and "noon"), release-NN variants.
  - Add a HEDGE error class when an answer contains two or more known values for that key.
  - Without normalization, rephrased LLM summaries are penalized on retention, not only on accuracy.
- **D2 [MUST] Bound retention.**
  - Use the same normalizers for retention.
  - A value counts as retained only when it appears in the same entry or line as its entity, plus the scope keyword for EXC.
  - Report unbound retention only as an upper bound.
- **D3 [MUST] Storage vs reading decomposition.** Per question, cross (bound-present in memory) with (correct):
  - not present → storage loss;
  - present but wrong → reading loss;
  - correct but not present → leak or luck.
  - CEM-Oracle minus CEM isolates extraction loss. No GPU, and this is the core analytical contribution.
- **D4 [SHOULD] Manual audit.** Hand-check about 150 sampled scored answers across the main methods and report the scorer's error rate.
- **D5 [SHOULD] Selective accuracy.** Report accuracy, the abstention rate on answerable questions, and the false-answer rate on ABSTAIN. This prevents "store less and abstain" or "guess" gaming.
- **D6 [MUST] Budget accounting.**
  - One counter for every method: the Hermes `_char_count` on the final entry list.
  - CEM pays delimiters, and any legend or abbreviation key counts inside the budget.
  - Also report tokens per memory (Ollama tokenize, or `prompt_eval_count` of a memory-only prompt), to show the char budget isn't gamed by symbol-dense notation.
  - Keep all notes in one language (English); Korean changes chars-per-fact.
- **D7 [MUST] Archive leakage.** The CEM archive is never visible at QA time in the main comparison. "CEM+archive" can only appear as a separate variant against BM25, at equal reader chars.
- **D8 [SHOULD] Same-model compress-and-answer confound.**
  - Cross-reader: 9B memories answered by gemma4:e4b and qwen3.5:4b (QA only).
  - Model-free retention is reader-independent and complements this.

### E. Statistics
- **E1 [MUST] Seeds.** Seeds are generator instances, since temperature is 0. Seed 0 is dev only; seeds 1-3 are test.
- **E2 [MUST] Primary tests.**
  - Pre-declare at most 3 primary contrasts at E=24 / B=2200 on macro accuracy: CEM vs Struct-KV, CEM vs Hermes-IC, CEM vs CEM-LLMmerge.
  - McNemar on per-question correctness pooled over seeds (exact, or CMH stratified by seed), with Holm correction.
  - Cluster bootstrap that resamples entities (2,000 resamples), with CIs on accuracy differences.
- **E3 [SHOULD] Power and sweeps.**
  - About 126 questions per seed gives roughly 378 pooled per method. Overall differences of about 7-8 pp are detectable; per-type CIs are about ±11 pp, so per-type claims need large effects.
  - The E and B sweeps use 1 seed: report them descriptively, with no p-values.

### F. Novelty and positioning
- **F1 [MUST] Related work a reviewer will expect:**
  - LongMemEval: its knowledge-update, temporal and abstention categories roughly match CUR/PREV/ABSTAIN; map the QA types to them in one sentence.
  - Mem0: LLM extraction plus an LLM ADD/UPDATE/DELETE/NOOP decision, which is what CEM-LLMmerge replicates.
  - Zep/Graphiti: temporal validity edges.
  - MemGPT/Letta: agent-managed memory through tool calls, the same paradigm as Hermes-native.
  - LoCoMo.
- Claimed novelty:
  1. a hard char budget, small local LLMs and the real Hermes tool;
  2. a deterministic merger keyed by (entity, attribute, scope) vs LLM-decided updates, with extraction held fixed;
  3. a measured split into storage, reading, extraction and collateral loss.
- Do not claim "hierarchical memory" or improved deployed Hermes behaviour.

## 2. Analyses that make the result more meaningful
1. **Headline figure:** accuracy (and bound retention) vs compression ratio (raw chars / budget) over the E×B grid, one line per method. This covers ratios of roughly 4x to 34x.
2. **Loss order under pressure:** which QA type fails first for each method. Hypothesis: LLM summaries drop EXC before PREV, without being told to; CEM drops in its declared tier order.
3. **Waterfall of loss:** Full-context → CEM-Oracle → CEM → CEM-LLMmerge → Struct-KV → Hermes-IC → Hermes-F. Each step is labelled with its storage, reading or extraction share (D3).
4. **Hermes op-level table:** validity, retry_cap rate, collateral loss per patch/remove (C5), and chars actually used vs the 2,200 budget.
5. **Per note-family accuracy** (A1): where CEM extraction breaks (aliases, rejected changes, NOTE facts). This makes the result two-sided and harder to dismiss.
6. **Cost table:** LLM calls, generated tokens and wall-clock per method.
7. **Paper space (2-3 pages):** Table 1 = P1 main results (methods × types with CIs); Fig 1 = pressure curves; Fig 2 = stacked error taxonomy with the storage/reading split. Hermes statistics go in the text.

## 3. Engineering rules that save GPU time
- Cache every LLM call by hash(model, prompt, options). Write all memories, tool traces and answers to JSONL, so rescoring and reanalysis need no GPU.
- Group runs by model, with `OLLAMA_MAX_LOADED_MODELS=1` and `keep_alive=-1`. Keep a constant `num_ctx` per model.
- `OLLAMA_NUM_PARALLEL=3-4` with a thread pool for QA only; expect about 1.5-2x on QA. Note the possible tiny batching nondeterminism.
- Run seed 1 end to end and score it before starting seeds 2-3 (stop-loss).
- Kill criterion: if Hermes-F tool-call validity is below 20% in the pilot, record that as a finding and run Hermes-F only in P1 and P4.

## 4. Recommended experiment matrix (in run order; about 6 GPU-hours)
Assumptions for 9B Q4: QA about 0.85 s (full-context about 2 s), extraction or tool call about 4-5 s, one-shot summary about 30-40 s. E=24 gives about 185 notes (about 8x the budget) and about 126 questions per seed: CUR 24, STABLE 24, PREV 24, EXC 20, EXC-NEG 10, ABSTAIN 12, NOTE 12.

| # | Pri | Run | Est. GPU time |
|---|---|---|---|
| P0 | MUST | Pilot + prompt freeze: dev seed 0, E=12, B=2200, all methods, 9B. Verify truncation asserts, tool validity, scorer. | 0.5 h |
| P1 | MUST | Main: 9B, E=24, B=2200, seeds 1-3. 13 methods: Full-ctx (reference), Recency, Dedup+Recency, BM25, Summary (original prompt), Struct-KV, Hermes-F, Hermes-IC, CEM, CEM-noHist, CEM-noScope, CEM-LLMmerge, CEM-Oracle. About 17 min compression + 23 min QA per seed. | 2.0 h |
| P2 | MUST | Volume sweep: 9B, B=2200, seed 1, E∈{12,48}. Recency, BM25, Summary, Struct-KV, Hermes-IC, CEM, CEM-Oracle. E=48 subsampled to 126 questions. | 0.75 h |
| P3 | SHOULD | Budget sweep: 9B, E=24, seed 1, B∈{1100,4400}. CEM, Oracle, Recency and BM25 are re-packed at no compression cost; Summary and Struct-KV regenerated; Hermes-IC at B=1100 only. | 0.45 h |
| P4 | SHOULD | Model generality: gemma4:e4b and qwen3.5:4b, each as compressor and reader, E=24, seed 1. Summary, Struct-KV, Hermes-F, Hermes-IC, CEM, CEM-Oracle, Recency. | 0.65 h |
| P5 | SHOULD | Cross-reader, run during P4 while each model is loaded: 9B memories from P1 seed 1 answered by e4b and 4b. 8 methods, QA only. | 0.2 h |
| P6 | COULD | Robustness slice: notes paraphrased by gemma4:e4b, filtered by a value-token check. 9B with Summary, Struct-KV, CEM, BM25, Recency. | 0.3 h |
| P7 | COULD | Rolling summary, seeds 1-3. | 0.3 h |

- Totals: MUST only (P0-P2) about 3.25 h; through P5 about 4.55 h; everything about 5.15 h, leaving about 0.85 h buffer.
- If time runs short, drop P7, then P6, then the B=4400 half of P3.
- The CEM-noHist and CEM-noScope ablations and CEM-Oracle cost QA time only; the compression-side analyses (D2, D3, C5, B7, B8) need no GPU.

## 5. Headline claims (if hypotheses hold) and fallback wording

1. **Loss taxonomy.**
   - If hypothesized: "Under Hermes's 2,200-char budget, X% of errors from ≤9B LLM consolidation are stale-version or scope-conflation errors, not omissions."
   - Korean: "2,200자 예산에서 소형 LLM 통합 오류의 X%는 누락이 아닌 버전·범위 혼동이다."
   - If null: "Omission dominates: the bottleneck is capacity, not structure."
   - If mixed: "Version and scope errors dominate PREV/EXC, while omission dominates CUR."

2. **Deterministic vs LLM merging (the main method claim).**
   - If hypothesized: "With extraction held fixed, replacing LLM merging with a deterministic (entity, attribute, scope)-keyed merger raises PREV/EXC accuracy by Δ pp [CI] at equal budget, with no loss on CUR/STABLE."
   - If null (CEM ≈ CEM-LLMmerge ≈ Struct-KV): "The gain comes from the structured representation; a structured-summary prompt is a sufficient and cheaper fix, and deterministic merging adds predictability, not accuracy." This is still a usable practical finding.

3. **Where the loss happens.**
   - If hypothesized: "LLM-summary errors are mostly storage losses; CEM's remaining errors are mainly extraction errors (CEM vs Oracle gap of Y pp)."
   - If null or mixed (CEM shows high reading loss): "Dense key-value rendering is hard for small readers to use; readability is a design constraint for bounded memory."

4. **Hermes-native consolidation.**
   - If hypothesized: "Driving the real Hermes memory tool with 9B/4B local models: a% valid tool calls, b% of sessions hit retry_cap, c% of patch/remove ops cause collateral loss; constrained decoding recovers d pp." This gives a quantitative basis for the docs' warning about models under 30B.
   - If null (Hermes-IC ≈ CEM): "Once format failures are removed, agent-driven consolidation is competitive; the practical gap is tool-call reliability, not policy."

5. **Behaviour under memory pressure.**
   - If hypothesized: "From about 4x to 34x compression, LLM summaries lose exceptions and previous values first and collapse, while CEM degrades gradually in its declared tier order."
   - If null: "All methods degrade at similar rates; CEM's benefit is that its loss is explicit and auditable (tier-ordered, with an archive), not higher accuracy."
   - BM25 framing either way: "Query-time retrieval wins on CUR but makes stale errors; persistent compressed memory and retrieval are complementary, and Hermes already has both."

Wording guard for the paper: always say "synthetic, author-constructed benchmark", "Hermes memory subsystem at commit 67481b6", "≤9B Q4 local models on a single 12 GB GPU". Report per-family results that show where CEM fails.

The repo files these findings rely on are in `/home/dh/Projects/KSC_Hermes/third_party/hermes-agent/`:
- tools/memory_tool_store.py
- tools/memory_tool.py
- agent/prompt_builder.py
- agent/background_review.py
- tools/session_search_tool.py