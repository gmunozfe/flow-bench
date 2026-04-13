#!/bin/bash

set -euo pipefail

# --- Validate input ---
if [ -z "${1:-}" ]; then
  echo "Usage: ./run-external-call-bench.sh <persistence-mode>"
  echo "Example: ./run-external-call-bench.sh redis"
  exit 1
fi

MODE="$1"
DATE=$(date +"%Y%m%d-%H%M%S")

# --- Output directory ---
OUTDIR="docs/results"
mkdir -p "$OUTDIR"

OUTFILE="${OUTDIR}/results-external-call-${MODE}-${DATE}.txt"

# --- Header ---
echo "========================================" | tee -a "$OUTFILE"
echo "🚀 External Call Benchmark Suite" | tee -a "$OUTFILE"
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

run() {
  RATE=$1
  DELAY_MS=$2

  echo "" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"
  echo "RUN: RATE=$RATE | DELAY_MS=$DELAY_MS" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"

  k6 run \
    -e RATE=$RATE \
    -e DURATION=30s \
    -e DELAY_MS=$DELAY_MS \
    bench/k6-external-call.js 2>&1 | tee -a "$OUTFILE"

  echo "" | tee -a "$OUTFILE"
  echo "----------------------------------------" | tee -a "$OUTFILE"
}

# =========================
# ZONE 1 — LIGHT LOAD
# =========================
echo "===== ZONE 1: LIGHT LOAD (20 req/s) =====" | tee -a "$OUTFILE"

run 20 50
run 20 200
run 20 1000

# =========================
# ZONE 2 — MEDIUM LOAD
# =========================
echo "===== ZONE 2: MEDIUM LOAD (50 req/s) =====" | tee -a "$OUTFILE"

run 50 50
run 50 200
run 50 1000

# =========================
# ZONE 3 — HIGH LOAD / SATURATION
# =========================
echo "===== ZONE 3: HIGH LOAD (150 req/s) =====" | tee -a "$OUTFILE"

run 150 50
run 150 200
run 150 1000

# --- Footer ---
echo "" | tee -a "$OUTFILE"
echo "Finished at: $(date)" | tee -a "$OUTFILE"
echo "Results saved in: $OUTFILE"
echo "========================================" | tee -a "$OUTFILE"
