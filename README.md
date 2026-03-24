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
## 💾 Local persistence services

This project can run with:

- **Redis** on `localhost:6379`
- **PostgreSQL (JPA)** on `localhost:5432`, database `flow`, user `flow`, password `flow`
- **MVStore file persistence** at `/tmp/hello-flow.mvstore.db`

### Start Redis and PostgreSQL

Start both containers in the background:

```bash
docker compose up -d
```

Start only Redis:
```bash
docker compose up -d redis
```

Start only PostgreSQL:
```bash
docker compose up -d postgres
```

### Stop containers

Stop and remove containers, but keep persisted data:
```bash
docker compose down
```

### Reset to a fresh instance

Stop and remove containers and delete their volumes:
```bash
docker compose down -v
```

This gives you a brand-new Redis and PostgreSQL state the next time you start them.


### MVStore reset

MVStore is file-based, not container-based. To start with a fresh MVStore database:

```bash
rm -f /tmp/hello-flow.mvstore.db
```

---

## 🚀 Build and Run the app with each profile

No persistence:
```bash
mvn clean package
java -jar target/quarkus-app/quarkus-run.jar
```

File (MVStore):
```bash
rm -f /tmp/hello-flow.mvstore.db
mvn clean package -Pfile -Dquarkus.profile=file
java -jar -Dquarkus.profile=file target/quarkus-app/quarkus-run.jar
```

Redis:
```bash
docker compose up -d redis
mvn clean package -Predis -Dquarkus.profile=redis
java -jar -Dquarkus.profile=redis target/quarkus-app/quarkus-run.jar
```

JPA:
```bash
docker compose up -d postgres
mvn clean package -Pjpa -Dquarkus.profile=jpa
java -jar -Dquarkus.profile=jpa target/quarkus-app/quarkus-run.jar
```

### Run benchmarks

```bash
k6 run -e RATE=5000 -e DURATION=2m bench/k6-order20.js
```

### Previous evaluation

You can check with cURL command that your workflow is ready to run benchmarks

```bash
curl -X GET http://localhost:8080/hello-flow  -H 'content-type: application/json'
curl -X POST http://localhost:8080/bench/order   -H 'Content-Type: application/json'   -d '{"orderId":"1","amount":42.5,"customerId":"cust-1"}'
curl -X POST http://localhost:8080/bench/order20   -H 'Content-Type: application/json'   -d '{"orderId":"1","amount":42.5,"customerId":"cust-1"}'
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
