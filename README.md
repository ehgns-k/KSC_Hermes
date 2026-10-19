# KSC 2026 주니어 논문 — Hermes Agent 제한 메모리의 정보 손실 진단과 변경·예외 인지 압축(CEM)

Hermes Agent(NousResearch)의 2,200자 `MEMORY.md`에 대량의 메모 파일을 압축해 넣을 때 어떤 정보가 어떻게 사라지는지를
정답이 알려진 합성 벤치마크로 측정하고, LLM은 사실 추출만 하고 병합·압축은 결정적 규칙으로 하는 **CEM**을 비교한다.
모든 LLM은 RTX 3060(12GB)에서 Ollama로 로컬 실행한다.

## 폴더 구조
```
KSC_Hermes/
├── README.md                  ← 이 파일
├── environment.yml            ← conda 환경 정의
├── requirements.txt           ← Python 의존성(버전 고정, environment.yml이 참조)
├── paper/                     ← ★ 논문 작성용 자료 (본문 초안, 표, 그림)
│   ├── manuscript.md          ← 투고용 원고 (국문, 2~3쪽, 그림·표 삽입 위치 표시)
│   ├── tables/                ← 표 (CSV + Markdown)
│   └── figures/               ← 그림 (PNG 300dpi + PDF 벡터)
├── experiments/               ← 실험 코드
│   ├── cem/datagen.py         ← 합성 메모리 스트림 + 질문 생성(정답 포함)
│   ├── cem/hermes_bridge.py   ← Hermes 실제 memory_tool/MemoryStore import
│   ├── cem/methods.py         ← 기준선(Recency, 요약, Hermes 에이전트 등)
│   ├── cem/cem.py             ← 제안 방법 CEM과 제거 실험
│   ├── cem/qa.py              ← 질의응답, BM25, 오류 유형 판정
│   ├── cem/llm.py             ← Ollama 클라이언트(결정적 디코딩, 디스크 캐시)
│   ├── cem/compaction.py      ← 실험 2: Hermes ContextCompressor 프롬프트로 반복 문맥 압축
│   ├── run.py                 ← 실험 실행(재개 가능)
│   ├── analyze.py             ← 표·그림·통계 생성(저장된 답변을 오프라인 재채점)
│   └── scripts/               ← 실행 순서 스크립트(queue_*.sh), 그림 1 생성, LLM 병합 사후 분석
├── results/                   ← 원자료: main/(에피소드·메모리·QA 행), 실행 로그, dev·smoke(개발용, 보고 제외), cache(LLM 응답 캐시, git 제외)
├── docs/
│   ├── experiment_design.md   ← 실험 설계와 v1 대비 변경 이유
│   ├── environment.md         ← 재현 정보(모델 digest, Hermes 커밋 등)
│   ├── research/              ← 관련 연구 조사, KSC 규정 조사, 설계 비판 검토
│   └── KSC_Hermes_대화기록.md  ← 이전 대화 기록
├── reference/                 ← 논문 양식(HWP), 이전(실험 전) 원고
└── third_party/hermes-agent   ← Hermes Agent 소스(커밋 67481b6 고정, git 미포함)
```

## 재현
```bash
conda env create -f environment.yml && conda activate ksc
git clone https://github.com/NousResearch/hermes-agent third_party/hermes-agent && git -C third_party/hermes-agent checkout 67481b6
ollama pull qwen3.5:9b && ollama pull gemma4:e4b && ollama pull qwen3.5:4b
cd experiments
python run.py --model qwen3.5:9b --entities 24 --seeds 1 2 3 --budgets 2200 --out ../results/main
python run.py --model qwen3.5:9b --entities 24 --seeds 1 2 --out ../results/main \
    --methods cem_ledger compact1 compact3 compact5 compact10          # 실험 2
python analyze.py --main ../results/main --out ../paper
```
LLM 호출은 `results/cache/`에 캐시되어 재실행 시 GPU 없이 같은 결과를 재생한다.

## 실제 수행한 실험 (2026-10-19)
| 실험 | 모델 | 설정 | 시드 |
|---|---|---|---|
| 실험 1: 2,200자 메모리 통합 (13개 방법) | qwen3.5:9b | E=24, B=2200 | 1–3 (475문항) |
| 실험 1 교차 모델 (10개 방법) | qwen3.5:4b | E=24, B=2200 | 1–3 |
| 예산 변화 | qwen3.5:9b | B=1100, 4400 | 1 |
| 실험 2: 반복 문맥 압축 k=1/3/5/10 + CEM 원장 | qwen3.5:4b | E=24 | 1–3 |
| 실험 2 | qwen3.5:9b | E=24 | 1–2 (3은 추가 실행) |
| 개발 파일럿(보고 제외) | qwen3.5:9b | E=24 | 0 |
취소: gemma4:e4b 교차 모델, E=12/48 규모 변화(시간 부족). 상세 경과는 `docs/progress_log.md`.
