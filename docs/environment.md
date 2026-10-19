# 실험 환경 (재현 정보)

| 항목 | 값 |
|---|---|
| GPU | NVIDIA GeForce RTX 3060 12GB (driver 595.99.02) |
| OS | Linux Mint 22.3 (kernel 7.0.0-34) |
| LLM 런타임 | Ollama 0.32.5 (로컬 서버 `127.0.0.1:11434`) |
| 주 모델 | `qwen3.5:9b` (9.0B, Q4_K_M, digest `56671c2ab938`) |
| 일반화 모델 | `gemma4:e4b` (digest `dc35e8d9c606`), `qwen3.5:4b` (Q4, digest `d8b0f5e9760c`) |
| 디코딩 | temperature 0, top_k 1, seed 0, `think: false`, `num_ctx` 16384, presence/repeat penalty 중립 |
| Hermes Agent | NousResearch/hermes-agent, commit `67481b6f37615e58f1434ba6a1528e4c6e9b754c` (2026-10-18), MIT |
| Hermes 메모리 설정 | `memory_char_limit` = 2,200(기본값), 항목 구분자 `\n§\n`, 문자 수 = `len("\n§\n".join(entries))` |
| Python | 3.12, numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, matplotlib 3.11.2, rapidfuzz 3.14.6, rank_bm25 |

## Hermes 코드 사용 방식
- `third_party/hermes-agent`에 위 커밋을 고정하여 내려받고(`.gitignore` 처리), `experiments/cem/hermes_bridge.py`가
  `tools.memory_tool.memory_tool`, `tools.memory_tool_store.MemoryStore`, `MEMORY_SCHEMA`,
  `agent.prompt_builder.build_memory_guidance`를 **수정 없이** import 한다.
- 전체 `AIAgent` 루프는 64K 문맥을 요구하므로(문서 `integrations/providers.md`) 사용하지 않고,
  동일한 도구 스키마·메모리 지침·세션별 고정 스냅샷·턴별 재시도 한도 초기화를 재현한 최소 하니스로 구동한다.
- 재현: `git clone https://github.com/NousResearch/hermes-agent third_party/hermes-agent && git -C third_party/hermes-agent checkout 67481b6`
