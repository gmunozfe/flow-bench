#!/bin/bash

set -euo pipefail

# --- Validate input ---
if [ -z "${1:-}" ]; then
  echo "Usage: ./run-subflow-orchestration-bench.sh <persistence-mode>"
  echo "Example: ./run-subflow-orchestration-bench.sh redis"
  exit 1
fi

MODE="$1"
DATE=$(date +"%Y%m%d-%H%M%S")

# --- Output directory ---
OUTDIR="docs/results"
mkdir -p "$OUTDIR"

OUTFILE="${OUTDIR}/results-subflow-orchestration-${MODE}-${DATE}.txt"

# --- Header ---
echo "========================================" | tee -a "$OUTFILE"
echo "🚀 Subflow Orchestration Benchmark Suite" | tee -a "$OUTFILE"
echo "========================================" | tee -a "$OUTFILE"
echo "Mode: $MODE" | tee -a "$OUTFILE"
echo "Started at: $(date)" | tee -a "$OUTFILE"
echo "" | tee -a "$OUTFILE"

# --- System info ---
echo "----- SYSTEM INFO -----" | tee -a "$OUTFILE"
uname -a | tee -a "$OUTFILE"
echo "" | tee -a "$OUTFILE"

echo "CPU:" | tee -a "$OUTFILE"
lscpu | grep "Model name" | tee -a "$OUTFILE" || true
echo "" | tee -a "$OUTFILE"

echo "Memory:" | tee -a "$OUTFILE"
free -h | tee -a "$OUTFILE"
echo "" | tee -a "$OUTFILE"

echo "-----------------------" | tee -a "$OUTFILE"
echo "" | tee -a "$OUTFILE"

# --- Run function ---
run() {
  RATE=$1
  SCRIPT=$2

  echo "" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"
  echo "RUN: RATE=$RATE | SCRIPT=$SCRIPT" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"

  k6 run \
    -e RATE=$RATE \
    -e DURATION=30s \
    bench/$SCRIPT 2>&1 | tee -a "$OUTFILE"

  echo "" | tee -a "$OUTFILE"
  echo "----------------------------------------" | tee -a "$OUTFILE"
}

# =========================
# ZONE 1 — LOW LOAD
# =========================
echo "===== ZONE 1: LOW LOAD =====" | tee -a "$OUTFILE"

run 100 k6-fork3.js
run 100 k6-fork5.js
run 100 k6-fork10.js

# =========================
# ZONE 2 — MEDIUM LOAD
# =========================
echo "===== ZONE 2: MEDIUM LOAD =====" | tee -a "$OUTFILE"

run 200 k6-fork3.js
run 200 k6-fork5.js
run 200 k6-fork10.js

# =========================
# ZONE 3 — HIGH LOAD
# =========================
echo "===== ZONE 3: HIGH LOAD =====" | tee -a "$OUTFILE"

run 300 k6-fork3.js
run 300 k6-fork5.js
run 300 k6-fork10.js

# --- Footer ---
echo "" | tee -a "$OUTFILE"
echo "Finished at: $(date)" | tee -a "$OUTFILE"
echo "Results saved in: $OUTFILE"
echo "========================================" | tee -a "$OUTFILE"
