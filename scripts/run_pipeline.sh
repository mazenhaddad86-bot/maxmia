#!/usr/bin/env bash
# Cron-Eintrag (Mac/Linux) — startet eine Pipeline-Iteration.
# Beispiel-Crontab (zwei Mal täglich):
#   0 8 * * *  /pfad/zu/video-automation/scripts/run_pipeline.sh
#   30 18 * * * /pfad/zu/video-automation/scripts/run_pipeline.sh
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
python -m src.main >> pipeline.log 2>&1
