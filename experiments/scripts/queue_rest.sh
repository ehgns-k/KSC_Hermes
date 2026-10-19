#!/bin/bash
# After the main 9B grid: (1) compaction seed 1, (2) budget sweep seed 1, (3) compaction seed 2, (4) E=12.
cd /home/dh/Projects/KSC_Hermes/experiments
while pgrep -f "[m]odel qwen3.5:9b --entities 24 --seeds 1 2 3 --budgets 2200 " > /dev/null; do sleep 15; done
PY=../.venv/bin/python
CM="cem_ledger compact1 compact3 compact5 compact10"
$PY run.py --model qwen3.5:9b --entities 24 --seeds 1 --budgets 2200 --out ../results/main --workers 3 --methods $CM >> ../results/compact_9b.log 2>&1
$PY run.py --model qwen3.5:9b --entities 24 --seeds 1 --budgets 1100 4400 --out ../results/main --workers 3 \
   --methods cem cem_oracle recency bm25 summary struct hermes cem_nohist cem_noscope >> ../results/sweep.log 2>&1
$PY run.py --model qwen3.5:9b --entities 24 --seeds 2 --budgets 2200 --out ../results/main --workers 3 --methods $CM >> ../results/compact_9b.log 2>&1
$PY run.py --model qwen3.5:9b --entities 12 --seeds 1 --budgets 2200 --out ../results/main --workers 3 \
   --methods cem cem_oracle full recency bm25 summary struct hermes >> ../results/sweep.log 2>&1
