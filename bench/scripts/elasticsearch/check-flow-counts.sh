#!/usr/bin/env bash
set -euo pipefail

ES_URL="${ES_URL:-http://localhost:9200}"
LOG_PATTERN="${LOG_PATTERN:-target/quarkus-flow-events.log*}"

workflow_log_count=$(
  { grep -h '"eventType":"io.serverlessworkflow.workflow' ${LOG_PATTERN} 2>/dev/null || true; } | wc -l
)

task_log_count=$(
  { grep -h '"eventType":"io.serverlessworkflow.task' ${LOG_PATTERN} 2>/dev/null || true; } | wc -l
)

workflow_db_count=$(curl -s "${ES_URL}/workflow-events-*/_count" \
  -H "Content-Type: application/json" \
  -d '{"query":{"prefix":{"eventType":"io.serverlessworkflow.workflow"}}}' \
  | jq -r '.count // 0')

task_db_count=$(curl -s "${ES_URL}/task-events-*/_count" \
  -H "Content-Type: application/json" \
  -d '{"query":{"prefix":{"eventType":"io.serverlessworkflow.task"}}}' \
  | jq -r '.count // 0')

workflow_instances=$(curl -s "${ES_URL}/workflow-instances/_count" \
  | jq -r '.count // 0')

task_instances=$(curl -s "${ES_URL}/task-executions/_count" \
  | jq -r '.count // 0')

echo "workflow_log_count=${workflow_log_count}"
echo "workflow_db_count=${workflow_db_count}"
echo "workflow_event_diff=$((workflow_log_count - workflow_db_count))"

echo "task_log_count=${task_log_count}"
echo "task_db_count=${task_db_count}"
echo "task_event_diff=$((task_log_count - task_db_count))"

echo "workflow_instances=${workflow_instances}"
echo "task_instances=${task_instances}"
