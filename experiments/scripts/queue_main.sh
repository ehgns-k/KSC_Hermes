#!/bin/bash
cd /home/dh/Projects/KSC_Hermes/experiments
while pgrep -f "run.py --model qwen3.5:9b --entities 24 --seeds 0 " > /dev/null; do sleep 10; done
../.venv/bin/python run.py --model qwen3.5:9b --entities 24 --seeds 1 2 3 --budgets 2200 --out ../results/main --workers 3 > ../results/main.log 2>&1
