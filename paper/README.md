# 논문 작성용 자료 안내

이 폴더에 논문 작성에 필요한 본문 초안, 표, 그림을 모았다. 숫자는 모두 `experiments/analyze.py`가 `results/`의 원자료(저장된 답변을 최신 채점기로 오프라인 재채점)에서 자동 생성했으며, 다시 실행하면 같은 값이 나온다.

## 원고
- `manuscript.md`: 투고용 원고(2~3쪽, 본문 약 4,000자, 요약 약 460자). 양식에 그대로 옮긴다.

한 문단이 한 줄이다. 그림과 표를 넣을 자리에는 `[그림 N 삽입 | 파일 | 크기]` 표시 줄이 있고, 그 아래 줄이 캡션이다. 표시 줄은 옮기지 않는다.

## 본문 그림·표 (파일명 = 논문 번호)

| 논문 번호 | 파일 | 내용 | 크기 | 위치 |
|---|---|---|---|---|
| 그림 1 | `figures/fig1_method_overview.*` | Hermes 기본 방식과 CEM 개념도 | 두 단 폭 | 3장 끝 또는 2쪽 위 |
| 표 1 | 원고 안의 표를 옮긴다(원자료 `tables/table1_main.md` + `tables/table1_ablation.md`, CEM 행 중복 제외) | 방법별 현재·직전·예외·전체·매크로 정확도, 오답률, 질의 토큰(9B, 시드 1~3)과 제거 실험 | 두 단 폭 | 5.1절 |
| 그림 2 | `figures/fig2_retention.*` | 세션 진행에 따른 유효 사실 보존율 | 한 단 폭 | 5.2절 |
| 그림 3 | `figures/fig3_compaction.*` | 압축 횟수 k에 따른 전체 정확도(실험 2) | 한 단 폭 | 5.4절 |

## 원고에 쓰지 않은 보조 그림·표
원고에서는 인용하지 않는다. 넣으려면 본문에서 처음 언급하는 순서대로 그림 4, 표 2부터 번호를 매기고 캡션을 새로 쓴다.

| 번호 | 파일 | 내용 |
|---|---|---|
| 그림 A | `figures/figA_error_breakdown.*`, `tables/main_errors.md` | 방법별 오류 유형 분포 |
| 그림 B | `figures/figB_budget_sweep.*`, `tables/sweep_budget.md` | 예산 B = 1100/2200/4400 (9B, 시드 1) |
| 그림 C | `figures/figC_type_heatmap.*` | 질문 유형별 정확도 히트맵(오답률·질의 토큰이 없어 표 1을 대신하지는 못함) |

## 본문 수치의 근거 표
| 파일 | 내용 | 해당 절 |
|---|---|---|
| `tables/main_accuracy.md` | 전체 상세표(7개 유형, 매크로[95% CI], 오답률, 응답 정밀도, 글자 수, 압축비, 압축 비용) | 5.1 |
| `tables/main_significance.md` | CEM 대비 McNemar(Holm 보정)와 매크로 차이 95% CI | 5.1 |
| `tables/xmodel_accuracy*.md` | 모델별(9B/4B) 정확도 | 5.1 |
| `tables/main_decomposition.md` | 저장 손실과 읽기 손실 분해 | 참고 |
| `tables/main_online_retention.md` | 그림 2의 수치 | 5.2 |
| `tables/main_hermes_ops.md` | Hermes memory 도구 구동 통계(호출, 실패, 용량 초과, 세션당 최대 삭제) | 5.2 |
| `tables/llmmerge_posthoc.md` | LLM 병합과 결정적 병합의 예산 절단 전후 보존율, 글자 수 | 5.3 |
| `tables/main_cem_extraction.md` | CEM 추출 품질(값 재현율, 범위 일치율, 기각값 유입) | 5.3 |
| `tables/main_by_family.md` | 메모 계열별(동의어, 기각, 되돌림) 정확도 | 5.3, 한계 |
| `tables/compaction_k.md` | 그림 3의 수치와 토큰 비용 | 5.4 |
| `tables/tableA_info_types_9b.md`, `tables/tableB_info_types_4b.md` | 정보 유형별 정확도(예외 조건 74.4%에서 24.4%, 현재 설정값 80.6%에서 41.8%) | 5.4 |
| `tables/data_stats.md` | 합성 데이터 통계 | 4.1 |

## 양식 메모 (KSC 2026 주니어)
- 참고문헌 포함 2~3쪽, A4(여백 위 30, 아래 20, 좌우 10mm). 제목, 영문 제목, 요약은 1단이고 본문은 2단, 글자는 9pt 이상.
- 그림 캡션은 그림 아래 "그림 1", 표 캡션은 표 위 "표 1". 그림은 PDF(벡터)를 쓰고 PNG(300dpi)는 예비용.
- 심사용 원고에는 저자 정보와 사사를 쓰지 않는다. PDF 5MB 이하, 접수 마감 2026-10-19 23:59, 접수 폼 제목 앞에 "[주니어논문]".
- 심사 배점: 중요 주제 10, 해결 문제와 방안 40, 신규성과 우월성 30, 과거 연구 비교 20.
- 참고문헌은 인용 순서대로 [1]~[11]이다. [6]~[11]은 2026년 arXiv 공개본이다(2026-10-19 arxiv.org에서 제목과 번호 확인). 투고 직전 저자와 게재처를 다시 대조한다.
- 캡션은 KSC 샘플처럼 번호 뒤에 마침표 없이 "그림 1 …"으로 쓴다.

## 그림 범례 용어와 본문 용어
그림은 Matplotlib 기본 스타일, 영문 라벨로 그렸다. 제목은 그림 안에 넣지 않고 캡션으로 쓴다.

| 그림 라벨 | 본문 용어 |
|---|---|
| Full context / BM25 | 무압축 원문 / BM25 검색(원문을 보관하는 참조 기준) |
| Recency / Hermes, no consolidation | 최신 노트 유지 / Hermes 무통합(한도를 넘게 되는 추가는 거부) |
| Summary / Structured summary | LLM 요약 / 구조화 요약 |
| Hermes agent / Hermes agent (JSON) | Hermes 에이전트(도구 호출) / Hermes 에이전트(JSON 강제) |
| CEM, CEM (oracle) | CEM(제안), CEM 정답 추출(Oracle) |
| CEM w/o history / w/o scope / w/ LLM merge | 제거 실험: 이전값 제거 / 범위 키 제거 / LLM 병합 |
| Hermes rolling / From source (= k=1) / CEM ledger (no limit) | 요약본 재압축 / 원본 참조 재압축(k=1 결과를 기준선으로 표시) / CEM 원장(글자 제한 없음) |
| Current, Stable, Previous, Exception, No exception, Note, Abstain | 현재값, 불변값, 직전값, 예외값, 예외 없음, 자유 메모, 모름 |
| Omission / Wrong version / Wrong scope / Other | 누락 / 버전 혼동 / 범위 혼동 / 기타(속성·엔티티 혼동, 기각값 채택, 근거 없는 값, '모름' 질문에 값을 답한 경우) |
| Valid facts retained / Sessions processed | 유효 사실 보존율 / 진행된 세션 비율(첫 세션 이후부터) |

그림 다시 그리기: `cd experiments && python analyze.py --figures-only` (그림 1은 `python scripts/make_diagram.py`). 파일명은 `analyze.py`의 `FIG_FILES`, `TABLE_FILES`에서 정한다.
