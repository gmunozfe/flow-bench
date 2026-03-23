# Flow Bench 🚀

This repository contains a performance benchmarking setup for evaluating **Quarkus Flow** under different persistence strategies and workflow complexities.

It is designed to measure how workflow execution behaves under load and how different persistence backends impact performance, latency, and scalability.

---

## 🎯 Purpose

This project benchmarks workflows using [k6](https://k6.io/) to analyze:

* 📈 Throughput (requests/sec)
* ⏱ Latency (avg, p90, p95)
* ⚠️ Dropped iterations (system saturation)
* 💾 Persistence overhead
* 🔁 Recovery capabilities

It helps answer:

* How much does persistence cost?
* What is the impact of workflow complexity?
* How does the system behave under high load?
* Which persistence backend provides the best trade-off?

---

## ⚙️ Workflows

The repository includes **4 workflows**, each representing a different execution pattern.

---

### 1. `HelloWorkflow`

**Description:**

* Minimal workflow with a single step

```json
{ "message": "hello world!" }
```

**Purpose:**

* Baseline performance
* Measures framework overhead without complexity

**Characteristics:**

* ⚡ Extremely fast
* 🧪 Ideal for sanity checks and baseline comparisons

---

### 2. `OrderWorkflow`

**Description:**

* Simple order lifecycle
* Few sequential steps (e.g. RECEIVED → VALIDATED → COMPLETED)

**Purpose:**

* Basic workflow execution with light persistence
* Entry-level performance comparison

---

### 3. `OrderWorkflow20`

**Description:**

* Extended workflow with **20 sequential steps**
* Simulates a realistic business process

**Purpose:**

* Stress test persistence layer
* Measure cost of many state transitions

**Characteristics:**

* 💾 Heavy persistence load
* 🔁 Many intermediate states
* 📊 Ideal for identifying bottlenecks

---

### 4. `OrderEnrichmentWorkflow`

**Description:**

* Workflow with an **external HTTP call**

Steps:

1. Receive order
2. Call enrichment service (`/mock/enrich`)
3. Merge response into workflow state
4. Complete workflow

**Purpose:**

* Measure impact of I/O-bound steps
* Simulate real-world service orchestration

**Characteristics:**

* 🌐 Network latency involved
* 🔄 Data transformation
* ⚖️ Mix of compute + I/O

---

## 🧪 Benchmark Setup

Benchmarks are executed using **k6** with a constant arrival rate:

```bash
k6 run -e RATE=5000 -e DURATION=2m bench/k6-order20.js
```

Parameters:

* `RATE` → target requests per second
* `DURATION` → test duration

---

## 💾 Persistence Modes

The project supports **4 persistence modes**, selectable via Maven profiles.

---

### 1. No Persistence (default)

```bash
mvn clean package
```

**Description:**

* No state is stored
* Everything runs in memory

**Characteristics:**

* ⚡ Lowest latency
* 🚀 Highest throughput
* ❌ No recovery if JVM crashes

---

### 2. Redis

```bash
mvn clean package -Predis -Dquarkus.profile=redis
```

**Description:**

* State stored in Redis
* Each workflow step persisted as a key (`:do/*`)

**Characteristics:**

* ⚡ Very low latency
* 📈 High throughput
* 💾 Durable (in-memory)
* 🔁 Supports recovery

**Important behavior:**

* Each step is persisted individually
* Workflow root key may be deleted after completion
* Step keys remain (no TTL by default)

---

### 3. File (MVStore)

```bash
mvn clean package -Pfile -Dquarkus.profile=file
```

**Description:**

* State stored on disk using MVStore

**Characteristics:**

* ⚖️ Moderate latency
* 💾 Durable
* 🔁 Supports recovery

---

### 4. JPA (PostgreSQL)

```bash
mvn clean package -Pjpa -Dquarkus.profile=jpa
```

**Description:**

* State persisted in a relational database

**Characteristics:**

* 🐢 Highest latency
* 📉 Lower throughput
* 💾 Strong durability
* 🔁 Full recovery support

---

## 🧠 Key Concepts

### Tail Latency

Tail latency (p90, p95) represents the slowest requests.

* Important for user experience
* Often increases significantly under load
* Strongly affected by persistence and I/O

---

### Dropped Iterations

k6 metric:

```text
dropped_iterations
```

Means:

> Requests that were scheduled but never executed because the system was saturated.

---

## 🚀 Running the Project

### Build

With the corresponding profile:
```bash
mvn clean package -Predis -Dquarkus.profile=redis 
```

### Launch

With the corresponding profile:
```bash
java -jar -Dquarkus.profile=redis target/quarkus-app/quarkus-run.jar
```

### Run benchmarks

```bash
k6 run -e RATE=5000 -e DURATION=2m bench/k6-order20.js
```

---

## 📊 What to Compare

When analyzing results, focus on:

* Throughput (`http_reqs`)
* Latency (`avg`, `p90`, `p95`)
* Dropped iterations
* Resource usage

Compare across:

* Different workflows
* Different persistence modes

---

## 📌 Conclusion

* Workflow complexity directly impacts persistence cost
* Redis provides the best balance between speed and persistence (needs to be refined still)
* External calls (enrichment workflow) introduce latency variability
* Persistence strategy must match system requirements
