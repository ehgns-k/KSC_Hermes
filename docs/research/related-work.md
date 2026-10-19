**Related work and references for KSC 2026: Hermes MEMORY.md consolidation with small local LLMs**

Part of the planned novelty claim is already published. In 2026, more than ten preprints, workshop papers and conference papers already cover the error taxonomy (claim a) and the split between LLM extraction and a deterministic, version-aware merge (claim b). Part 3 gives a narrower claim that still holds, plus four changes to the experiment design that these papers point to.

## 1. Reference list (KIISE style)

I checked each entry below against arXiv abstract pages, the Crossref API, the ACL Anthology, IOS Press or ICLR/OpenReview. Notes in brackets flag anything uncertain. Entries marked ★ are the recommended core set (about 16) for a 2–3 page paper.

**Foundations, systems and benchmarks**

- [1]★ Nous Research, "Hermes Agent," GitHub repository, 2025–2026.
  - https://github.com/NousResearch/hermes-agent (commit 67481b6, accessed 2026.10.19)
  - Docs: "Persistent Memory," https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
  - [Repo created 2025-07-22; MIT License, ©2025 Nous Research. pyproject version is "0.0.0", so cite the commit, not a release.]
- [2]★ C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, J. E. Gonzalez, "MemGPT: Towards LLMs as Operating Systems," arXiv preprint arXiv:2310.08560, 2023.
- [3] J. S. Park, J. C. O'Brien, C. J. Cai, M. R. Morris, P. Liang, M. S. Bernstein, "Generative Agents: Interactive Simulacra of Human Behavior," Proc. of the 36th Annual ACM Symp. on User Interface Software and Technology (UIST '23), Article 2, pp. 1-22, 2023. DOI:10.1145/3586183.3606763
- [4] W. Zhong, L. Guo, Q. Gao, H. Ye, Y. Wang, "MemoryBank: Enhancing Large Language Models with Long-Term Memory," Proc. of the AAAI Conf. on Artificial Intelligence, Vol. 38, No. 17, pp. 19724-19731, 2024. DOI:10.1609/aaai.v38i17.29946 (arXiv:2305.10250)
- [5] W. Xu, Z. Liang, K. Mei, H. Gao, J. Tan, Y. Zhang, "A-MEM: Agentic Memory for LLM Agents," Advances in Neural Information Processing Systems (NeurIPS 2025), 2025. arXiv:2502.12110 [venue taken from the arXiv comment; pages not verified]
- [6]★ P. Chhikara, D. Khant, S. Aryan, T. Singh, D. Yadav, "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory," Proc. of ECAI 2025, Frontiers in Artificial Intelligence and Applications, Vol. 413, pp. 2993-3000, 2025. DOI:10.3233/FAIA251160 (arXiv:2504.19413)
- [7]★ P. Rasmussen, P. Paliychuk, T. Beauvais, J. Ryan, D. Chalef, "Zep: A Temporal Knowledge Graph Architecture for Agent Memory," arXiv preprint arXiv:2501.13956, 2025.
- [8]★ D. Wu, H. Wang, W. Yu, Y. Zhang, K.-W. Chang, D. Yu, "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory," Proc. of ICLR 2025, 2025. arXiv:2410.10813
- [9] A. Maharana, D.-H. Lee, S. Tulyakov, M. Bansal, F. Barbieri, Y. Fang, "Evaluating Very Long-Term Conversational Memory of LLM Agents," Proc. of the 62nd Annual Meeting of the ACL (Vol. 1: Long Papers), pp. 13851-13870, 2024. DOI:10.18653/v1/2024.acl-long.747
- [10]★ Y. Hu, Y. Wang, J. McAuley, "Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions," Proc. of ICLR 2026, 2026. arXiv:2507.05257
  - [This is MemoryAgentBench. The arXiv abstract calls the 4th competency "selective forgetting"; the code repo calls it "Conflict Resolution".]
- [11]★ H. Jiang, Q. Wu, C.-Y. Lin, Y. Yang, L. Qiu, "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models," Proc. of EMNLP 2023, pp. 13358-13376, 2023. DOI:10.18653/v1/2023.emnlp-main.825
- [12] Z. Pan, Q. Wu, H. Jiang, M. Xia, X. Luo, J. Zhang, Q. Lin, V. Rühle, Y. Yang, C.-Y. Lin, H. V. Zhao, L. Qiu, D. Zhang, "LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression," Findings of ACL 2024, pp. 963-981, 2024. DOI:10.18653/v1/2024.findings-acl.57
- [13] F. Xu, W. Shi, E. Choi, "RECOMP: Improving Retrieval-Augmented LMs with Context Compression and Selective Augmentation," Proc. of ICLR 2024, 2024. arXiv:2310.04408 [the arXiv v1 title has no word "Context"; use the ICLR title]
- [14]★ N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, P. Liang, "Lost in the Middle: How Language Models Use Long Contexts," Transactions of the ACL, Vol. 12, pp. 157-173, 2024. DOI:10.1162/tacl_a_00638
- [15] R. Xu, Z. Qi, Z. Guo, C. Wang, H. Wang, Y. Zhang, W. Xu, "Knowledge Conflicts for LLMs: A Survey," Proc. of EMNLP 2024, pp. 8541-8565, 2024. DOI:10.18653/v1/2024.emnlp-main.486
- [16] J. Xie, K. Zhang, J. Chen, R. Lou, Y. Su, "Adaptive Chameleon or Stubborn Sloth: Revealing the Behavior of Large Language Models in Knowledge Conflicts," Proc. of ICLR 2024, 2024. arXiv:2305.13300
- [17] Z. Zhang, X. Bo, C. Ma, R. Li, X. Chen, Q. Dai, J. Zhu, Z. Dong, J.-R. Wen, "A Survey on the Memory Mechanism of Large Language Model-based Agents," ACM Trans. on Information Systems, Vol. 43, No. 6, pp. 1-47, 2025. DOI:10.1145/3748302
- [18]★ D. Chen, S. Niu, K. Li, P. Liu, X. Zheng, B. Tang, X. Li, F. Xiong, Z. Li, "HaluMem: Evaluating Hallucinations in Memory Systems of Agents," arXiv:2511.03506, 2025.
- [19]★ Q. Zhang, C. Hu, S. Upasani, B. Ma, F. Hong, V. Kamanuru, J. Rainton, C. Wu, M. Ji, H. Li, U. Thakker, J. Zou, K. Olukotun, "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models," Proc. of ICLR 2026, 2026. arXiv:2510.04618
- [20] J. Kang, M. Ji, Z. Zhao, T. Bai, "Memory OS of AI Agent," Proc. of EMNLP 2025, pp. 25961-25970, 2025. DOI:10.18653/v1/2025.emnlp-main.1318 [pages differ: ACL Anthology says 25961-25970, Crossref says 25972-25981; check before final submission]
- [21] Z. Li et al. (39 authors), "MemOS: A Memory OS for AI System," arXiv:2507.03724, 2025.
- [22] J. Fang, X. Deng, H. Xu, Z. Jiang, Y. Tang, Z. Xu, S. Deng, Y. Yao, M. Wang, S. Qiao, H. Chen, N. Zhang, "LightMem: Lightweight and Efficient Memory-Augmented Generation," Proc. of ICLR 2026, 2026. arXiv:2510.18866 [name clash with [50]]
- [23] S. Yan, X. Yang, Z. Huang, E. Nie, Z. Ding, Z. Li, X. Ma, J. Bi, K. Kersting, J. Z. Pan, H. Schütze, V. Tresp, Y. Ma, "Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning," arXiv:2508.19828, 2025.
- [24] W. Ma, J. Nan, W. Wu, Y. Chen, "What Deserves Memory: Adaptive Memory Distillation for LLM Agents," arXiv:2508.03341, 2025. [This is the "Nemori" framework under its current arXiv title (v4). I could not confirm whether earlier versions had the title "Nemori: …".]
- [25] Z. Pan, Q. Wu, H. Jiang, X. Luo, H. Cheng, D. Li, Y. Yang, C.-Y. Lin, H. V. Zhao, L. Qiu, J. Gao, "SeCom: On Memory Construction and Retrieval for Personalized Conversational Agents," Proc. of ICLR 2025, 2025. arXiv:2502.05589
- [26] J. Liu, Y. Su, P. Xia, S. Han, Z. Zheng, C. Xie, M. Ding, H. Yao, "SimpleMem: Efficient Lifelong Memory for LLM Agents," arXiv:2601.02553, 2026. [the code README claims ICML'26; not verified, so cite as arXiv]
- [27] H. Yu, T. Chen, J. Feng, J. Chen, W. Dai, Q. Yu, Y.-Q. Zhang, W.-Y. Ma, J. Liu, M. Wang, H. Zhou, "MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent," Proc. of ICLR 2026, 2026. arXiv:2507.02259
- [28] Y. Wang, R. Takanobu, Z. Liang, Y. Mao, Y. Hu, J. McAuley, X. Wu, "Mem-α: Learning Memory Construction via Reinforcement Learning," arXiv:2509.25911, 2025.
- [29] M. Zhang, E. Choi, "SituatedQA: Incorporating Extra-Linguistic Contexts into QA," Proc. of EMNLP 2021, pp. 7371-7387, 2021. DOI:10.18653/v1/2021.emnlp-main.586

**2026 prior art closest to our claims**

Most of these are preprints. Single-author or workshop papers are marked "(preprint)" or "(workshop)".

- [30]★ V. Patel, "Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents," arXiv:2606.27472, 2026. (preprint)
- [31] H. Chao, Y. Bai, R. Sheng, T. Li, Y. Sun, "STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?," arXiv:2605.06527, 2026.
- [32]★ D. Zhang, Y. Lin, Z. Wu, Y. Sun, B. Li, D. Li, H. Peng, "Useful Memories Become Faulty When Continuously Updated by LLMs," arXiv:2605.12978, 2026.
- [33]★ V. Reddy, S. R. Challaram, "Reliable Post-Retrieval Assembly for Agent Memory: Separating Evidence Extraction from Policy Execution," Lifelong Agent Workshop at COLM 2026 (poster), arXiv:2606.01435, 2026. (workshop)
- [34]★ N. Yadav, "Temporal Validity in Retrieval Memory: Eliminating Stale-Fact Errors for AI Agents over Evolving Knowledge," arXiv:2606.26511, 2026. (preprint)
- [35]★ H. Deng, P. Sinchaisri, "Stale, Misattributed, or Late: Where Personal Memory Fails Before Generation," arXiv:2610.10265, 2026.
- [36]★ I. Garg, N. Kolhe, D. Song, X. Zhao, "MemFail: Stress-Testing Failure Modes of LLM Memory Systems," arXiv:2605.26667, 2026.
- [37]★ S. Zerhoudi, J. Mitrovic, M. Granitzer, "The Compaction Cliff in Long-Running AI Agent Memory," Proc. of the 35th ACM CIKM (CIKM 2026), 2026. arXiv:2608.22752, DOI:10.1145/3799682.3840567 [venue from the arXiv journal-ref; Crossref does not resolve the DOI yet; pages unknown]
- [38] Q. Kang, M. Liu, S. Kai, K. Liang, Z. Tang, Y. Cui, T. Zhong, M. Yuan, "Retain or Consolidate? Budget-Dependent Operator Selection for Language Agent Memory," arXiv:2607.17545, 2026.
- [39] N. Bhargava, R. S. Barrento, "MEMAUDIT: An Exact Package-Oracle Evaluation Protocol for Budgeted Long-Term LLM Memory Writing," arXiv:2605.02199, 2026.
- [40] A. K. G. Rao, A. Jaggi, "BudgetBench: A Budget-Tiered Protocol and Pilot Harness for Memory Strategy Evaluation in Local Large Language Model Agents," arXiv:2609.13149, 2026.
- [41] M. Kim, J. Baek, S. Jeong, S. J. Hwang, "MemRefine: LLM-Guided Compression for Long-Term Agent Memory," arXiv:2606.13177, 2026.
- [42]★ Z. Jiang, Z. Fu, Z. Li, Y. Kim, J. Mi, X. Peng, F. Teng, H. Wu, "Presentation, Not Mechanism: A Render Confound in Deprecation-Aware Memory Evaluation," arXiv:2607.16019, 2026.
- [43] Q. Spencer, "Ground Truth First: A Longitudinal Evaluation Instrument for Agent Memory, and the Tenure Crossover in Memory-Architecture Rankings," arXiv:2607.21962, 2026. (preprint)
- [44] N. Yadav, "When Old Facts Return: Re-Reads, Reverts, and the Limits of Temporal Memory," arXiv:2610.07715, 2026. (preprint)
- [45] L. Yang, S. Xu, Z. Li, T. Yang, L. Huang, "When Personal Memory Has No Single Answer: Evaluating LLM Agents under Irreducible Conflict," arXiv:2608.13921, 2026.
- [46] T. An, "Fidelity Before Structure: Verbatim Chunks Beat Lossy Artifact Extraction in Long-Conversation LLM Memory," arXiv:2601.00821, 2025 (v4, 2026). (preprint)
- [47] Z. Wang, "TOKI: A Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory," arXiv:2606.06240, 2026. (preprint)
- [48] H. Gu, X. Li, "Whose Memory Is It? Scope-Aware Commit Rules for Long-Term LLM Memory," NeurIPS 2026 Workshop LP4FM (poster), arXiv:2610.09008, 2026. (workshop)
- [49] J. Hu, S. Ramachandran, "The Memory Trust Gap: Capability-Dependent Failures in Persistent-Memory Agents," arXiv:2609.01852, 2026. (preprint, under workshop review)
- [50] J. Zhang, C. Zhang, S. Chen, Z. Huang, P. Zheng, Z. Wang, P. Guo, F. Mo, S.-H. Bae, J. Zou, J. Wei, Y. Yang, "Lightweight LLM Agent Memory with Small Language Models," Proc. of ACL 2026 (main), 2026. arXiv:2604.07798 [venue from the arXiv comment; the system is also called "LightMem"]
- [51] W. Zhou, X. Zhou, S. Han, H. Xu, G. Li, Z. Li, F. Xiong, F. Wu, "Are We Ready For An Agent-Native Memory System?," arXiv:2606.24775, 2026.
- [52] X. Chen, X. Xie, W. Fu, J. Zhou, S. Yu, Q. Xuan, "MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair," arXiv:2607.27080, 2026.

## 2. How each relates to our study

- [1] This is the system we study. MEMORY.md has a 2,200-character limit and does not auto-compact; the agent must consolidate it with add/patch/remove. The repo removed `replace` after it wiped multi-fact entries.
- [2] OS-style paging of memory that the LLM manages itself. It is the conceptual root of Hermes's self-edited bounded memory. Unlike us, it does not measure what is lost under a hard character budget.
- [3] Memory stream with reflection and summarization. It motivates our "memory stream" input, but it retrieves by recency, importance and relevance rather than packing into a fixed budget.
- [4] Long-term memory with a forgetting curve: an early forgetting policy, but with no version or scope handling.
- [5] Zettelkasten-style notes that the LLM links and evolves. Consolidation is done by the LLM, which is one of the factors we isolate.
- [6] An LLM picks ADD/UPDATE/DELETE/NOOP for each extracted fact (verified in the paper). This is the closest analogue to Hermes's memory ops. Our merge instead runs deterministic rules over (entity, attribute, scope) keys.
- [7] Bi-temporal edges (t_valid/t_invalid) and edge invalidation (verified). This is prior art for version-aware memory. It is a retrieval graph, not a bounded text file.
- [8] Defines the KU (knowledge update), TR (temporal reasoning) and ABS (abstention) categories (verified). Our CUR/PREV/ABSTAIN questions mirror these on synthetic data with exact ground truth.
- [9] Benchmark of very long conversations (single-hop, multi-hop, temporal). Its answer keys are not exact enough for automatic error typing.
- [10] MemoryAgentBench's FactConsolidation tests conflict resolution with serial-numbered updates. It has no character budget and no scope.
- [11, 12] Token-level prompt compression. Useful as a contrast: it does not understand versions, so dropping tokens can delete a qualifier or the previous value.
- [13] Extractive/abstractive compressors trained for RAG. Query-dependent compression, whereas memory must be written before the query is known.
- [14] Accuracy depends on where evidence sits in the context. This motivates both the full-context baseline and dense one-line-per-entity rendering.
- [15, 16] Behaviour under context/parametric conflict. Background for the stale-vs-current conflict our model faces when a memory contains both.
- [17] General survey of agent memory, used to frame the area.
- [18] HaluMem already gives an operation-level taxonomy of fabrication, errors, conflicts and omissions at the extraction and updating stages. Our omission and hallucination categories are not new.
- [19] ACE names "context collapse" (iterative LLM rewriting erodes detail) and fixes it with structured incremental delta updates. This is the closest conceptual precedent for our deterministic merger.
- [20, 21] Hierarchical memory OSes (short/mid/long term). Different axis: storage tiers, not version/scope correctness under a fixed character budget.
- [22] Compresses and filters memory before storage plus offline "sleep-time" updates. Optimizes cost on LoCoMo/LongMemEval rather than typing errors.
- [23] RL-trained ADD/UPDATE/DELETE/NOOP manager. Learned policy versus our training-free deterministic merge.
- [24] Nemori's selection of what to keep by predictability. Selection policy only, with no version/scope keys.
- [25] Segment-level memory with compression-based denoising (LLMLingua-2). Retrieval-oriented.
- [26] Explicitly targets "semantic lossless compression" of memory. This directly overlaps the "less information loss" wording of our topic, so we must contrast with it.
- [27, 28] RL agents that overwrite a fixed-length memory or build structured memory. Fixed-length memory is a precedent for a bounded memory budget.
- [29] Answers that depend on time or place context. The QA precedent for our scoped exceptions ("EU region", "weekends").
- [30] The closest prior art. Bounded self-maintained memory drops LongMemEval-KU accuracy from 92% to 77% even for frontier models. "Memory maintenance, not comprehension" is the bottleneck, and 24× more memory gives no recovery; the paper fixes it with RL on a 3B model. We differ in using Hermes's real tool, character budgets, scope, and training-free methods.
- [31] Implicit conflict, where a later observation invalidates an old memory without saying so. Benchmark with 400 scenarios; the best frontier models reach only 55.2%.
- [32] As consolidation proceeds, the utility of LLM-consolidated memory first rises, then falls below the no-memory baseline. This is the same phenomenon our Hermes-native condition is designed to show.
- [33] An LLM extracts candidates and a separate deterministic stage executes "latest wins" on FactConsolidation. Most of the gain comes from the separation itself, and the effect is not significant on LongMemEval. This directly precedes our claim (b).
- [34] MemStrata: a deterministic supersession rule on (subject, relation, object) keys in a bi-temporal ledger, with no LLM call, takes stale-fact errors to about 0%. Claim (b) again, for retrieval memory.
- [35] Measures stale exposure before generation. Serving only the active value of each correctly keyed slot eliminates staleness; the hard part is assigning facts to the right key ("missed merges" and "false merges"). Our CEM vs CEM-Oracle comparison should report the same thing.
- [36] Conditional-Facts task: summarization drops qualifying conditions, which is our "scope conflation". The scope-error category is therefore already shown, though without versions or a budget.
- [37] LLM compaction keeps 53% of rules after one round and 10% after five; deterministic per-type compaction keeps 2–4× more and is tested with McNemar. A bounded-memory precedent with a deterministic fix.
- [38] Whether consolidating or retaining raw records is better depends on budget pressure (LongMemEval/LoCoMo). This supports our budget sweep.
- [39] Measures budgeted memory writing against an exact oracle, including "validity-state preservation". The methodological precedent for CEM-Oracle and for memory-only metrics such as retention.
- [40] Budget-tiered evaluation on local small LLMs (e.g., qwen2.5:1.5b) with truncation and summary-buffer baselines. Close to our setup on the local-model side, but with token budgets and no version/scope typing.
- [41] LLM-judged delete/merge/preserve until a storage budget is met. A budgeted-memory baseline that is not version-aware.
- [42] Rendering confound: apparent mechanism gains in deprecation-aware memory are mostly easier presentation. Our CEM rendering vs free-text summary needs a control where presentation is matched.
- [43] Script-first synthetic ground truth with validity intervals, as in our generator. A budgeted "curated map" memory loses evicted content over longer histories.
- [44] Re-reading an old value can wrongly reactivate a retired one, and a re-read cannot be told apart from a genuine revert. This is a direct risk for our "redundant restatement" notes (see 3.3).
- [45] Context-partitioned conflicts. A precedent for scope-dependent values.
- [46] Lossy LLM fact extraction loses 16–22 points to storing raw text. A counterweight to atomic-fact CEM that must be acknowledged.
- [47] Formal bitemporal contradiction-resolution operators. Formal precedent for the deterministic merge.
- [48] "Scope" there means discourse ownership (plans vs facts), not conditional values. Cite it to avoid confusing the two meanings.
- [49] Small Qwen3 models (0.6–8B) over-trust stale notes. Supports studying small local models.
- [50] Agent memory built on small LMs. Shows small-model memory is an active topic; not budgeted.
- [51] Systematic comparison of 12 memory systems; finds localized maintenance more cost-efficient than global reorganization.
- [52] Uses Hermes as an evaluation harness for memory poisoning (security). The only paper found that uses Hermes; it does not study consolidation loss.

## 3. Novelty assessment

**3.1 Already covered by prior work**
- **Claim (a), the information-loss taxonomy, is not new as a taxonomy.**
  - Omission, hallucination and conflict: [18].
  - Stale/version errors: [30, 31, 34, 35].
  - Cross-entity misattribution: [35].
  - Condition stripping, i.e. scope conflation: [36].
  - Bounded or continuously updated LLM memory losing information: [30, 32, 37, 43].
- **Claim (b), LLM extraction separated from a deterministic version-aware merge, is not new.**
  - Directly shown in [33, 34, 35].
  - Close relatives: [7, 19, 37, 47].
  - Mem0 [6] is the "LLM decides the op" counterpart.
- **"Lossless compression of memory" wording collides with SimpleMem [26].** Avoid it in the title and abstract.
- **"Small models fail at memory" is partly shown** in [40, 49, 50].

**3.2 Still defensible (to our knowledge, after a targeted search)**
1. A controlled diagnosis of a real deployed harness's bounded file memory. Specifically:
   - Hermes's actual MemoryStore/memory_tool code with a 2,200-character budget.
   - No auto-compaction: overflow errors force the model to consolidate.
   - Driven by 4–9B local models on one 12 GB GPU.
   - No paper found evaluates Hermes's native consolidation; [52] uses Hermes only for security. [30] is the nearest, but it uses LongMemEval-KU, token budgets, frontier models and RL training.
2. Versions and scope measured jointly, with exact ground truth, in one stream:
   - CUR, PREV, EXC and ABSTAIN questions answered from the memory alone.
   - A budget × memory-volume sweep.
   - Prior work isolates staleness [30, 31, 34], condition stripping [36], or context-partitioned conflict [45], but not the combination under a hard character budget.
3. A training-free, format-compatible fix, presented as an application of the extraction/policy split [33–35] to Hermes's MEMORY.md format:
   - Keys of (entity, attribute, scope).
   - Priority-tier packing, with overflow to an archive file.
   - Oracle ablation separating extraction error from consolidation error, in the spirit of [33, 39].
   - Present it as an application, not an invention.

**Suggested contribution sentence:** "We do not propose a new memory architecture. We quantify, with exact ground truth, how Hermes Agent's native 2,200-char MEMORY.md consolidation loses current, previous and scoped values when driven by small local LLMs. We then show that applying the extraction / deterministic-merge separation [33–35] with scope-aware keys and budget-tier packing reduces stale and scope-conflation errors in the same file format."

**3.3 Design changes these papers point to (do before running)**
- **Add a presentation-matched control [42].** Two options:
  - Render the CEM facts as free prose.
  - Render the LLM-summary content in CEM's one-line-per-entity format.

  Otherwise reviewers can say CEM wins on layout alone.
- **Watch out for re-reads [44].** If a "redundant restatement" repeats an *old* value after an update, a merge that keeps the latest timestamp will roll it back. Two options:
  - Restrict restatements to the current value.
  - Keep old-value re-reads as an explicit stress subset, and add a guard against reactivating retired values.
- **Report key-assignment errors [35].** Count entity/attribute normalization misses and wrong merges separately from extraction misses. CEM vs CEM-Oracle covers part of this.
- **Expect the budget curve to be non-monotonic.** [30] found that 24× more memory gives no recovery, and [40] reports non-monotonic quality across budgets. State the budget sweep as a hypothesis, not an expected monotone gain.

## 4. Suggested Korean related-work text

LLM 에이전트의 장기 메모리 연구는 LLM이 스스로 기억을 관리하는 계층형 구조(MemGPT[2], MemoryOS[20]), 사실 단위 추출과 ADD/UPDATE/DELETE 갱신(Mem0[6], A-MEM[5]), 유효 구간을 갖는 시간 지식 그래프(Zep[7])로 발전해 왔으며, LongMemEval[8]과 MemoryAgentBench[10]는 지식 갱신·충돌 해결을 핵심 평가 축으로 제시하였다. 최근에는 제한된 자기 관리 메모리에서 갱신 정보가 소실되고[30], LLM의 반복 통합이 오히려 기억을 오염시키며[32], 요약 과정에서 조건(범위) 정보가 탈락하는[36] 현상이 보고되었고, 이에 대해 LLM의 근거 추출과 결정적 갱신 규칙을 분리하는 접근[33,34,35]이 제안되었다. 그러나 이들 연구는 주로 검색형 메모리와 대형 모델을 대상으로 하며, 본 연구는 실제 배포 에이전트인 Hermes Agent[1]의 2,200자 고정 예산 MEMORY.md를 소형 로컬 LLM이 통합할 때 발생하는 정보 손실을 버전·범위 축에서 정답 기반으로 정량화하고, 동일 형식과 호환되는 추출–결정적 병합 방식을 비교한다는 점에서 차별된다.

## Sources
- arXiv abstract pages: https://arxiv.org/abs/ followed by each listed arXiv id.
- Crossref API: https://api.crossref.org/works/ followed by each listed DOI.
- [20] ACL Anthology: https://aclanthology.org/2025.emnlp-main.1318/
- [6] IOS Press: https://ebooks.iospress.nl/doi/10.3233/FAIA251160
- [10] ICLR 2026: https://iclr.cc/virtual/2026/poster/10010781
- [13] ICLR 2024 / dblp: https://iclr.cc/virtual/2024/poster/17885 and https://dblp.org/rec/conf/iclr/XuSC24.html
- [25] OpenReview: https://openreview.net/forum?id=xKDZAW0He3
- [1] GitHub: https://github.com/NousResearch/hermes-agent and https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- [36] MemFail HTML: https://arxiv.org/html/2605.26667v1

No files were written. The local Hermes clone used for [1] is at /home/dh/Projects/KSC_Hermes/third_party/hermes-agent.