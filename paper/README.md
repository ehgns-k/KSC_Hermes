# 논문 작성용 자료 안내

이 폴더 하나에 논문 작성에 필요한 본문 초안, 표, 그림을 모았다. 숫자는 모두 `experiments/analyze.py`가
`results/`의 원자료(저장된 답변을 최신 채점기로 오프라인 재채점)에서 자동 생성했으며, 다시 실행하면 같은 값이 나온다.

## 구성 (실험 1 = Hermes 2,200자 메모리 통합, 실험 2 = Hermes 반복 문맥 압축)

| 파일 | 내용 | 논문 내 위치(권장) |
|---|---|---|
| `manuscript_submission.md` | **투고용 축약판**(2~3쪽 분량, 본문 약 3,600자) — 그대로 양식에 옮겨 쓰기 좋음 | 전체 |
| `manuscript.md` | 전체판(모든 근거·정의·한계·참고문헌 12편) — 축약판에서 필요한 문장을 골라 보강 | 전체 |
| `figures/fig1_method_overview.*` | Hermes 기본 방식 vs CEM 개념도 | 그림 1 (3장, 두 단 폭) |
| `tables/main_table1_compact.md` | **표 1 후보**: 방법별 현재·직전·예외·전체 정확도, 오답률, 질의 토큰 (9B, 3시드) | 표 1 |
| `tables/main_table2_ablation.md` | 제거 실험(이전값·범위키·결정적 병합·Oracle) | 표 2 또는 본문 |
| `tables/main_accuracy.md` | 전체 상세표(7개 유형, 매크로[95% CI], 오답률, 응답 정밀도, 글자 수, 압축비, 압축 비용) | 부록/본문 인용 |
| `figures/main_error_breakdown.*`, `tables/main_errors.md` | 오류 유형 분해(누락/버전/범위/기각값…) | 그림 2 |
| `figures/main_online_retention.*`, `tables/main_online_retention.md` | 세션 진행에 따른 유효 사실 보존율(Hermes 붕괴 vs CEM) | 그림 3 (한 단 폭) |
| `figures/main_type_heatmap.*` | 유형별 정확도 히트맵 | 표 1 대체 가능 |
| `tables/main_decomposition.md` | 저장 손실 vs 읽기 손실 분해 | 본문 인용 |
| `tables/main_significance.md` | CEM vs 각 방법 McNemar(Holm 보정) + 매크로 차이 95% CI | 본문 인용 |
| `tables/main_hermes_ops.md` | Hermes 실제 memory 도구 구동 통계(호출·실패·용량 초과·세션당 최대 손실) | 본문 인용 |
| `tables/main_cem_extraction.md` | CEM 추출 품질(값 재현율·범위 일치율·기각값 유입) | 본문 인용 |
| `tables/main_by_family.md` | 메모 계열별(동의어·기각·되돌림) 정확도 → 한계(동의어) 근거 | 본문 인용 |
| `tables/llmmerge_posthoc.md` | LLM 병합 vs 결정적 병합: 예산 절단 전/후 보존율과 글자 수 | 본문 인용 (5.3) |
| `tables/xmodel_accuracy*.md` | 모델별(9B/4B) 정확도 | 본문 인용 |
| `tables/compaction_k.md`, `figures/compaction_k.*` | **실험 2**: 압축 횟수 k=1/3/5/10에 따른 정확도·토큰(요약본 재압축 vs 원본 참조 vs CEM) | 그림 4 (한 단 폭) |
| `tables/info_types_qwen3.5_9b.md`, `..._4b.md` | **정보 유형별**(현재 설정값/변경 이력/예외 조건/결정/교훈·명령 메모, 수치/식별자/시각) 정답률·보존율 | 표 3 또는 본문 |
| `tables/sweep_budget.*`, `figures/sweep_budget.*` | 예산 B = 1100/2200/4400 (9B, 시드 1) | 그림 5 / 5.5 본문 |
| `tables/data_stats.md` | 합성 데이터 통계 | 4장 |

양식 메모: 그림 캡션은 그림 **아래** "그림 1 …", 표 캡션은 표 **위** "표 1 …". PNG는 300dpi, PDF는 벡터.
2~3쪽 제한이므로 권장 구성: 그림 1(두 단) + 표 1(두 단 또는 한 단 축약) + 그림 3·그림 4(각 한 단) + 표 2/3은 핵심 행만.

## 그림 범례 용어 ↔ 본문 용어
그림은 Matplotlib 기본 스타일, 영문 라벨로 그렸다(제목은 그림 안에 넣지 않고 캡션으로 쓴다).

| 그림 라벨 | 본문 용어 |
|---|---|
| Full context / BM25 | 무압축 원문 / BM25 검색(원문을 보관하는 참조선) |
| Recency / Hermes, no consolidation | 최신 노트 유지 / Hermes 무통합(초과 시 거부) |
| Summary / Structured summary | LLM 요약 / 구조화 요약 |
| Hermes agent / Hermes agent (JSON) | Hermes 에이전트(도구 호출) / Hermes 에이전트(JSON 강제) |
| CEM, CEM (oracle) | CEM(제안), CEM-Oracle(정답 추출) |
| CEM w/o history / w/o scope / w/ LLM merge | 제거 실험: 이전값 보존 제거 / 범위 키 제거 / LLM 병합 |
| Hermes rolling / From source (= k=1) / CEM ledger (no limit) | 요약본 재압축 / 원본 참조 재압축(k=1 결과를 기준선으로 표시) / CEM 사실 원장(글자 제한 없음) |
| Current, Stable, Previous, Exception, No exception, Note, Abstain | 현재값, 불변값, 직전값, 예외값, 예외 없음, 교훈 메모, 모름 |
| Omission / Wrong version / Wrong scope / Other | 누락 / 버전 혼동 / 범위 혼동 / 기타(속성·엔티티 혼동, 기각값, 근거 없는 값, 모름 질문에 값 생성) |
| Valid facts retained / Sessions processed | 유효 사실 보존율 / 진행된 세션 비율(첫 세션 이후부터) |

그림 다시 그리기: `cd experiments && ../.venv/bin/python analyze.py --figures-only` (그림 1은 `scripts/make_diagram.py`).
