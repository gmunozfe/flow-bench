# Hello Workflow Benchmark

## Overview

The **Hello Workflow** is the simplest workflow in this benchmark suite.  
It consists of a single step that produces a static message:

This workflow is used to measure:

- Baseline performance of the Flow engine  
- Overhead introduced by different persistence modes  
- Maximum achievable throughput under minimal processing  

---

## Setup

- **Tool:** k6  
- **Scenario:** constant arrival rate  
- **Duration:** 2 minutes  
- **Rates tested:** 5000 req/s, 8000 req/s  
- **Max VUs:** 500  

---

## Results

### Summary Table (5000 req/s)

| Mode            | Throughput (req/s) | Avg Latency | p95 Latency     | Dropped Iterations |
|-----------------|--------------------|-------------|------------------|---------------------|
| No persistence  | ~5000              | ~sub-ms     | ~sub-ms          | ~0                  |
| Redis           | ~5000              | ~sub-ms     | ~sub-ms          | very low            |
| MVStore         | ~5000              | ~1–2 ms     | ~sub-ms–1ms      | low                 |
| JPA             | ~4500–4800         | ~10–20 ms   | ~50+ ms          | noticeable          |

---

## Analysis

### Throughput

- All modes except JPA reach near the target rate (5000 req/s)  
- JPA shows reduced throughput due to database overhead  

### Latency

- No persistence achieves the lowest latency (sub-millisecond)  
- Redis remains very close to in-memory performance  
- MVStore introduces small disk-related overhead  
- JPA significantly increases latency due to database roundtrips  

### Dropped Iterations

- Minimal in No persistence and Redis modes  
- Slight increase in MVStore  
- Higher in JPA due to resource contention and slower operations  

### Tail Latency

- Redis and No persistence show very tight latency distribution  
- MVStore slightly increases tail latency  
- JPA exhibits higher variability and long tail (p95 much higher than average)  

---

## Conclusion

The Hello Workflow highlights the baseline performance characteristics of the system:

- The Flow engine introduces minimal overhead  
- Persistence choice is the primary factor affecting performance  
- Redis provides near in-memory performance  
- JPA introduces significant latency and variability  

This workflow serves as a reference point for understanding the cost of persistence in more complex workflows.
