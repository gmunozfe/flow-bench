# Order Workflow (3 Tasks)

## Overview

Multi-task workflow simulating order processing.

---

## 📊 Summary

### 5000 req/s

| Mode | Req/s | Avg | p95 | Drops |
|------|------|-----|-----|------|
| No persistence | ~4987 | 0.57 ms | 0.51 ms | 1.5k |
| MVStore | ~4995 | 0.59 ms | 0.74 ms | 632 |
| Redis | ~4987 | 0.67 ms | 0.46 ms | 1.6k |
| JPA | ~4782 | 10.9 ms | 34.9 ms | 26k |

---

### 8000 req/s

| Mode | Req/s | Avg | p95 | Drops |
|------|------|-----|-----|------|
| No persistence | ~7997 | 0.21 ms | 0.45 ms | 360 |
| MVStore | ~7990 | 0.45 ms | 0.75 ms | 1.2k |
| Redis | ~7995 | 0.30 ms | 0.38 ms | 577 |
| JPA | ~6900–7060 | 20–23 ms | 50–83 ms | 112k+ |

---

## 🧠 Analysis

### Fast paths (No persistence, Redis, MVStore)
- Stable up to 8000 req/s
- Sub-millisecond latency
- Minimal differences between modes

### Redis
- Best **tail latency**
- Matches or exceeds no persistence

### MVStore
- Slight overhead
- Still stable

### JPA
- System saturates between 5k–8k req/s
- High dropped iterations
- Tail latency unstable → queueing effects

---

## 🏁 Conclusion

> Redis provides the best trade-off between durability and performance.

JPA is not suitable for high-throughput workloads in this setup.
