#!/bin/bash

set -e

# --- Validate input ---
if [ -z "$1" ]; then
  echo "Usage: ./run-json-bench.sh <persistence-mode>"
  echo "Example: ./run-json-bench.sh redis"
  exit 1
fi

MODE=$1
DATE=$(date +"%Y%m%d-%H%M%S")

# --- Output directory ---
OUTDIR="docs/results"
mkdir -p "$OUTDIR"

OUTFILE="${OUTDIR}/results-json-${MODE}-${DATE}.txt"

# --- Header ---
echo "========================================" | tee -a "$OUTFILE"
echo "🚀 JSON Benchmark Suite" | tee -a "$OUTFILE"
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
  ITEMS=$2
  ITER=$3

  echo "" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"
  echo "RUN: RATE=$RATE | ITEMS=$ITEMS | ITERATIONS=$ITER" | tee -a "$OUTFILE"
  echo "========================================" | tee -a "$OUTFILE"

  k6 run \
    -e RATE=$RATE \
    -e DURATION=30s \
    -e ITEMS=$ITEMS \
    -e ITERATIONS=$ITER \
    bench/k6-json.js 2>&1 | tee -a "$OUTFILE"

  echo "" | tee -a "$OUTFILE"
  echo "----------------------------------------" | tee -a "$OUTFILE"
}

# --- Zone 1 (light load) ---
run 20 1000 10
run 20 1000 100
run 20 1000 300

# --- Zone 2 (high throughput) ---
run 150 1000 10
run 150 1000 30
run 150 1000 60
run 150 1000 80
run 150 1000 100

# --- Zone 3 (heavy processing) ---
run 5 1000 300
run 5 1000 600
run 5 1000 1000
run 1 10000 300

# --- Footer ---
echo "" | tee -a "$OUTFILE"
echo "Finished at: $(date)" | tee -a "$OUTFILE"
echo "Results saved in: $OUTFILE"
echo "========================================" | tee -a "$OUTFILE"
