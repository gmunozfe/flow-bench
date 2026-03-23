# Persistence Comparison

## 🧾 Summary Across All Workflows

| Mode | Performance | Latency | Scalability | Notes |
|------|------------|--------|------------|------|
| No persistence | ⭐⭐⭐⭐⭐ | Lowest | Excellent | Baseline |
| Redis | ⭐⭐⭐⭐⭐ | Very low | Excellent | Best trade-off |
| MVStore | ⭐⭐⭐⭐ | Low | Good | Slight overhead |
| JPA | ⭐⭐ | High | Poor | Saturates |

---

## 🧠 Key Insights

### 1. Redis ≈ No persistence
- Near-identical latency
- Excellent throughput

### 2. MVStore is acceptable
- Small overhead
- Good for local persistence

### 3. JPA is the bottleneck
- High latency
- Queue saturation
- Large drop rate

---

## 📌 Recommendation

- Use **Redis** for production high-throughput workflows
- Use **MVStore** for simple/local setups
- Avoid **JPA** for high-load scenarios
