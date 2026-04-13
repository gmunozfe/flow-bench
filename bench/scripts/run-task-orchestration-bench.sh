#!/bin/bash

set -e

# --- Validate input ---
if [ -z "$1" ]; then
  echo "Usage: ./run-task-orchestration-bench.sh <persistence-mode>"
  echo "Example: ./run-task-orchestration-bench.sh redis"
  exit 1
fi

MODE=$1
DATE=$(date +"%Y%m%d-%H%M%S")

# --- Output directory ---
OUTDIR="docs/results"
mkdir -p "$OUTDIR"

OUTFILE="${OUTDIR}/results-task-orchestration-${MODE}-${DATE}.txt"

# --- Header ---
echo "========================================" | tee -a "$OUTFILE"
echo "🚀 Task Orchestration Benchmark Suite" | tee -a "$OUTFILE"
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

run 20 k6-order20.js
run 20 k6-order50.js
run 20 k6-order100.js

# =========================
# ZONE 2 — MEDIUM LOAD
# =========================
echo "===== ZONE 2: MEDIUM LOAD =====" | tee -a "$OUTFILE"

run 80 k6-order20.js
run 80 k6-order50.js
run 80 k6-order100.js

# =========================
# ZONE 3 — HIGH LOAD / SATURATION
# =========================
echo "===== ZONE 3: HIGH LOAD =====" | tee -a "$OUTFILE"

run 150 k6-order20.js
run 150 k6-order50.js
run 150 k6-order100.js

# --- Footer ---
echo "" | tee -a "$OUTFILE"
echo "Finished at: $(date)" | tee -a "$OUTFILE"
echo "Results saved in: $OUTFILE"
echo "========================================" | tee -a "$OUTFILE"
