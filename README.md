---

# 📘 Quarkus Flow Benchmark

This project benchmarks **Quarkus Flow** performance across different workflow patterns and persistence strategies.

The goal is to understand how different workloads behave and to isolate the cost of:

* Task orchestration
* TaskOutput generation (CPU)
* TaskOutput handling (memory / serialization)
* External calls
* Persistence strategies

This project benchmarks workflows using [k6](https://k6.io/) to analyze:
* 📈 Throughput (requests/sec)
* ⏱ Latency (avg, p90, p95)
* ⚠️ Dropped iterations (system saturation)
* 💾 Persistence overhead


---

# 🧠 Benchmark Model

## Two independent dimensions

### 1. Workflow dimension (what is stressed)

Each benchmark targets a specific aspect of execution:

| Dimension             | Description                                    |
| --------------------- | ---------------------------------------------- |
| Persistence baseline  | Minimal workflow, tiny state                   |
| Task orchestration    | Many tasks, small TaskOutput                   |
| TaskOutput processing | Large TaskOutput generated (CPU-heavy)         |
| TaskOutput handling   | Large TaskOutput reused (memory/serialization) |
| External call         | Workflow dominated by HTTP call                |

---

### 2. Persistence strategy (how state is stored)

Each workflow is executed with different persistence backends:

| Strategy       | Description               |
| -------------- | ------------------------- |
| None           | No persistence            |
| Redis          | Key-Value store    |
| File (MVStore) | Embedded file-based store |
| JPA            | Relational database       |

---

## 🧩 Benchmark matrix

Each workflow is evaluated under each persistence strategy:

```text
                    Persistence Strategy
Workflow        None   Redis   File   JPA
--------------------------------------------
Baseline         ✓      ✓       ✓      ✓
Orchestration    ✓      ✓       ✓      ✓
Processing       ✓      ✓       ✓      ✓
Handling         ✓      ✓       ✓      ✓
External Call    ✓      ✓       ✓      ✓
```

👉 This separates:

* **what the workflow does**
* from
* **how its state is persisted**

---

# 🔬 Benchmark Scenarios

## 1. Persistence baseline

**Purpose:** measure the cost of enabling persistence itself.

* Minimal workflow
* Very small TaskOutput

👉 isolates:

> overhead of persistence infrastructure

---

## 2. Task orchestration

**Workflows:**

* `order20`
* `order50`
* `order100`

**Characteristics:**

* Many tasks
* Small TaskOutput

👉 measures:

* cost per task
* persistence overhead on task-heavy workflows

---

## 3. TaskOutput processing (CPU-bound)

**Workflow:** `json`

**Characteristics:**

* Large TaskOutput generated per request
* Heavy mutations (CPU + GC)

👉 measures:

* CPU cost
* memory allocation
* GC pressure

### Examples

| Mutations | TaskOutput Size |
| --------: | ----------   -: |
|       10k |          ~78 KB |
|       30k |         ~235 KB |
|      100k |         ~780 KB |
|      300k |        ~2.35 MB |
|        1M |         ~7.8 MB |
|        3M |        ~23.5 MB |

---

## 4. TaskOutput handling (memory-bound)

**Workflow:** `taskoutput-persistence`

**Characteristics:**

* Large prebuilt TaskOutput (from 100KB to 20 MB)
* No generation cost

👉 measures:

* serialization
* memory bandwidth
* object graph traversal

---

## 5. External call

**Workflow:** `external-call`

**Characteristics:**

* One HTTP call per request
* Small TaskOutput

👉 measures:

* cost per external call
* interaction with persistence

---

# 📊 Performance Model

## Latency decomposition

```text
Latency
≈ Task orchestration
+ TaskOutput processing
+ TaskOutput handling
+ External call overhead
+ Persistence strategy effect
+ Queueing (under saturation)
```

---

## Throughput model

Each workflow is limited by the subsystem it stresses:

```text
Required throughput (MB/s)
≈ request_rate × TaskOutput_size
```

System is stable while:

```text
required_throughput < subsystem_limit
```

---

# 📈 Measured Limits (example on test machine)

| Component             | Approx. Limit | Description                  |
| --------------------- | ------------- | ---------------------------- |
| TaskOutput processing | ~135 MB/s     | CPU + GC bound               |
| TaskOutput handling   | ~300 MB/s     | memory / serialization bound |

---

## Interpretation

* `json` → CPU-bound
* `taskoutput-persistence` → memory-bound
* Redis/JPA/file → I/O-bound

👉 The bottleneck depends on the workflow shape.

---

# ⚠️ Saturation Behavior

When a subsystem limit is exceeded:

* latency increases sharply
* throughput drops below target
* dropped iterations appear
* VUs increase
* p95/p99 explode

👉 This is caused by **queueing**, not linear cost.

---

# 🎯 Key Insights

* Persistence is **not a standalone cost**
* Its impact depends on:

  * Number of tasks (cost per task)
  * TaskOutput size (cost per byte)
  
* Latency also depends on:

  * Workflow computation (cost per CPU and serialization)
  * Workflow calls (cost per external call)


## Cost per Task across persistence modes

![Cost per Task vs. Latency](docs/images/cost_per_task_20_150_rps.png)
![Cost per Task log scale](docs/images/cost_per_task_150rps_log.png)

- Baseline orchestration cost (without persistence) ≈ **0.045 ms/task**

| Mode | Cost per task |
|------|--------------|
| None / File | ~0.04 ms |
| Redis (stable) | ~0.5–1 ms |
| JPA (stable) | ~2–10 ms |
| Saturated systems | 10–100 ms |

### Cost per Byte across persistence modes

![Cost per KB vs. Latency](docs/images/cost_per_kb_latency.png)
![Cost per KB Payload size vs. time increased](docs/images/cost_per_kb_vs_payload_size.png)

- Baseline TaskOutput cost ≈ **0.025 ms per KB**
- For large TaskOutput:

* CPU limit ≈ 135 MB/s
* Redis limit ≈ 120 MB/s

👉 persistence becomes the bottleneck before CPU, and CPU before internal memory

---

# 🧠 Key Concepts

## Tail Latency

Tail latency (p90, p95) represents the slowest requests.

* Important for user experience
* Often increases significantly under load
* Strongly affected by persistence and I/O

---

## Dropped Iterations

k6 metric:

```text
dropped_iterations
```

Means:

> Requests that were scheduled but never executed because the system was saturated.

---

# 💾 Local persistence services

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

## 🌐 Build app with each profile

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
---

# 🚀 Running Benchmarks

## TaskOutput handling example

```bash
k6 run -e RATE=5 -e DURATION=30s -e PREBUILT_SIZE_KB=50000 bench/k6-taskoutput-persistence.js
```

---

## TaskOutput processing example

```bash
k6 run -e RATE=7 -e DURATION=30s -e ITEMS=10000 -e ITERATIONS=300 bench/k6-json.js
```

---

## External call example

```bash
k6 run -e RATE=20 -e DURATION=30s -e DELAY_MS=100 bench/k6-external-call.js
```

---

# 🧭 How to read results

## Stable system

* achieved rate ≈ configured rate
* latency stable
* no dropped iterations

## Saturated system

* achieved rate < configured rate
* latency grows rapidly
* dropped iterations appear

---

# 🧠 Conclusions

* Quarkus Flow performance depends on both the workflow shape and the persistence strategy.
* Each workflow stresses a different subsystem (CPU, memory, or I/O), and saturation occurs when that subsystem exceeds its throughput limit.
* Workflow complexity directly impacts persistence cost
* Redis provides the best balance between speed and persistence (needs to be refined still)
* External calls (external call workflow) introduce latency variability
* Persistence strategy must match system requirements
* two factors dominate scalability:

  * **state size**
  * **number of tasks**

> The system scales well when **it is stable**, but combining **large payloads + many tasks + high rate + high delays + high CPU use** can saturate it over system limits.


---

