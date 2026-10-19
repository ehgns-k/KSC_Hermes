#!/bin/bash
# gemma4:e4b cross-model run (seed 1 only, reduced methods), after the qwen3.5:4b runs finish.
cd /home/dh/Projects/KSC_Hermes/experiments
while pgrep -f "[m]odel qwen3.5:4b" > /dev/null; do sleep 20; done
../.venv/bin/python run.py --model gemma4:e4b --entities 24 --seeds 1 --budgets 2200 --out ../results/main --workers 2 --num-ctx 8192 \
  --methods full recency summary struct hermes bm25 cem cem_oracle >> ../results/xmodel_gemma.log 2>&1
