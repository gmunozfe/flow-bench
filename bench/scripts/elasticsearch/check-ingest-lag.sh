#!/usr/bin/env bash
set -euo pipefail

ES_URL="${ES_URL:-http://localhost:9200}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: '$1' is required but not installed or not in PATH" >&2
    exit 1
  fi
}

require_command curl
require_command jq
require_command awk

for index in "workflow-events-*" "task-events-*"; do
  echo
  echo "=== ${index} raw ingest lag per minute ==="
  printf "%-30s %10s %12s %12s %12s %12s\n" \
    "insert_minute" "events" "avg_lag_ms" "p50_lag_ms" "p95_lag_ms" "max_lag_ms"

  response=$(curl -s "${ES_URL}/${index}/_search" \
    -H "Content-Type: application/json" \
    -d '{
      "size": 0,
      "runtime_mappings": {
        "lag_ms": {
          "type": "double",
          "script": {
            "source": "if (params._source.timestamp != null && doc[\"@timestamp\"].size() != 0) { double ts = ((Number)params._source.timestamp).doubleValue(); double eventMs = ts < 1000000000000L ? ts * 1000.0 : ts; emit(doc[\"@timestamp\"].value.toInstant().toEpochMilli() - eventMs); }"
          }
        }
      },
      "aggs": {
        "per_minute": {
          "date_histogram": {
            "field": "@timestamp",
            "fixed_interval": "1m",
            "min_doc_count": 1
          },
          "aggs": {
            "avg_lag_ms": {
              "avg": {
                "field": "lag_ms"
              }
            },
            "p50_lag_ms": {
              "percentiles": {
                "field": "lag_ms",
                "percents": [50]
              }
            },
            "p95_lag_ms": {
              "percentiles": {
                "field": "lag_ms",
                "percents": [95]
              }
            },
            "max_lag_ms": {
              "max": {
                "field": "lag_ms"
              }
            }
          }
        }
      }
    }')

  if echo "$response" | jq -e '.error' >/dev/null 2>&1; then
    echo "ERROR querying index pattern ${index}:"
    echo "$response" | jq '.error'
    continue
  fi

  bucket_count=$(echo "$response" | jq '.aggregations.per_minute.buckets | length // 0')

  if [[ "$bucket_count" -eq 0 ]]; then
    echo "No data found for ${index}"
    continue
  fi

  echo "$response" | jq -r '
    .aggregations.per_minute.buckets[]
    | [
        .key_as_string,
        .doc_count,
        ((.avg_lag_ms.value // 0) | round),
        ((.p50_lag_ms.values["50.0"] // 0) | round),
        ((.p95_lag_ms.values["95.0"] // 0) | round),
        ((.max_lag_ms.value // 0) | round)
      ]
    | @tsv
  ' | awk -F'\t' '{printf "%-30s %10s %12s %12s %12s %12s\n", $1, $2, $3, $4, $5, $6}'
done
