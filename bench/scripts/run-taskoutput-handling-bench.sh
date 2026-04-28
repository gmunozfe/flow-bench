#!/bin/bash

set -e

# --- Validate input ---
if [ -z "$1" ]; then
  echo "Usage: ./run-taskoutput-handling-bench.sh <persistence-mode>"
  echo "Example: ./run-taskoutput-handling-bench.sh redis"
  exit 1
fi

MODE=$1
DATE=$(date +"%Y%m%d-%H%M%S")

# --- Output directory ---
OUTDIR="docs/results"
mkdir -p "$OUTDIR"

OUTFILE="${OUTDIR}/results-taskoutput-handling-${MODE}-${DATE}.txt"

# --- Header ---
echo "========================================" | tee -a "$OUTFILE"
echo "🚀 TaskOutput Handling Benchmark Suite" | tee -a "$OUTFILE"
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
  SIZE_KB=$2

  echo "" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"
  echo "RUN: RATE=$RATE | PREBUILT_SIZE_KB=$SIZE_KB" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"

  k6 run \
    -e RATE=$RATE \
    -e DURATION=30s \
    -e PREBUILT_SIZE_KB=$SIZE_KB \
    bench/k6-taskoutput-persistence.js 2>&1 | tee -a "$OUTFILE"

  echo "" | tee -a "$OUTFILE"
  echo "----------------------------------------" | tee -a "$OUTFILE"
}

# =========================
# ZONE 1 — 1 MB
# =========================
echo "===== ZONE 1: 1 MB TASKOUTPUT =====" | tee -a "$OUTFILE"

run 50 1000
run 100 1000
run 200 1000

# =========================
# ZONE 2 — 5 MB
# =========================
echo "===== ZONE 2: 5 MB TASKOUTPUT =====" | tee -a "$OUTFILE"

run 10 5000
run 20 5000
run 30 5000

# =========================
# ZONE 3 — 20 MB
# =========================
echo "===== ZONE 3: 20 MB TASKOUTPUT =====" | tee -a "$OUTFILE"

run 1 20000
run 2 20000
run 5 20000

# --- Footer ---
echo "" | tee -a "$OUTFILE"
echo "Finished at: $(date)" | tee -a "$OUTFILE"
echo "Results saved in: $OUTFILE"
echo "========================================" | tee -a "$OUTFILE"
