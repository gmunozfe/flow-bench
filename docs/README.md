# 📊 Benchmark Results

This section contains detailed benchmark results for the `flow-bench` project.

## Contents

- [Hello Workflow](hello-workflow.md)
- [Order Workflow (3 steps)](order-workflow.md)
- [Order Workflow (20 steps)](order20-workflow.md)
- [Persistence Comparison](persistence-comparison.md)

## Summary

Across all benchmarks:

- **No persistence, Redis, and MVStore** maintain near-baseline performance
- **Redis** provides the best balance of latency and persistence
- **JPA** introduces significant latency and saturates under load

For full details, see the individual sections.
