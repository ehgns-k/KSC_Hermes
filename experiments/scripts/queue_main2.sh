#!/bin/bash
# Main 9B grid (seeds 1-3, E=24, B=2200), CEM code paths first so bugs surface early.
cd /home/dh/Projects/KSC_Hermes/experiments
# wait until the dev pilot has produced its hermes_ic result (or exited), then stop it
while pgrep -f "[s]eeds 0 --budgets" > /dev/null && ! grep -q " hermes_ic " ../results/dev_pilot.log; do sleep 10; done
pkill -f "[s]eeds 0 --budgets"; sleep 3
../.venv/bin/python run.py --model qwen3.5:9b --entities 24 --seeds 1 2 3 --budgets 2200 --out ../results/main --workers 3 \
  --methods cem cem_nohist cem_noscope cem_oracle cem_llmmerge full recency reject bm25 summary struct hermes hermes_ic \
  > ../results/main.log 2>&1
