# Order Workflow (20 Steps)

## 📊 Results

| Mode | Req/s | Avg | Median | p95 | Drops | Stability |
|------|------|-----|--------|-----|------|----------|
| No persistence | ~4980 | 1.04 ms | 0.37 ms | 0.58 ms | 2.3k | Stable |
| Redis | ~4993 | 0.71 ms | 0.44 ms | 0.76 ms | 804 | Stable |
| MVStore | ~4959 | 2.37 ms | 0.46 ms | 0.93 ms | 5.0k | Stable |
| JPA | ~4629 | 25.66 ms | 1.98 ms | 131.97 ms | 44.5k | Saturated |

---

## 🧠 Analysis

### Scaling effect
- Increasing steps → more persistence operations
- Clear separation between persistence strategies

### Redis
- Handles multi-step workflows efficiently
- Maintains low latency despite more writes

### MVStore
- Noticeable increase in avg latency
- Still stable

### JPA
- Severe degradation
- High tail latency (p95 > 130 ms)
- System clearly saturated

---

## 🏁 Conclusion

> As workflow complexity increases, persistence cost becomes dominant.

Redis scales well, while JPA becomes a bottleneck.
