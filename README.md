# ATA — Agent To Agent (Autonomous Virtual Society & Policy Simulator)

[![Build & Test Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](Makefile)
[![Go Version](https://img.shields.io/badge/go-1.22%2B-blue.svg)](go.mod)
[![A2A Protocol Conformance](https://img.shields.io/badge/A2A%20Protocol-v1.0.0-indigo.svg)](https://github.com/a2aproject/A2A)
[![License](https://img.shields.io/badge/license-Apache--2.0-lightgrey.svg)](LICENSE)

**ATA (Agent To Agent)** is a headless, multi-agent virtual society engine and policy optimization platform built on the [A2A protocol standard](https://github.com/a2aproject/A2A) (JSON-RPC 2.0 over HTTP / Server-Sent Events). Four autonomous Go daemons coordinate via standard Agent Cards to generate synthetic populations, simulate virtual city dynamics, evaluate democratic/economic health metrics, and optimize system parameters in a closed feedback loop — with zero human intervention.

---

## 🎯 Definite Use Cases

ATA is designed to address complex, real-world simulation and multi-agent protocol scenarios:

### 1. Synthetic Demographic & Population Dynamics Modeling
- **Digital Soul Generation**: Synthesizes realistic digital citizens ("Souls") combining census demographic distributions, 6 psychological archetypes (*The Stoic Engineer, The Disillusioned Artist, The Community Builder, The Ambitious Entrepreneur, The Cautious Observer, The Idealistic Activist*), life stages, and SHA-256 cryptographic identity hashes.
- **5D Emotional Vectors & Behavioral Profiles**: Models citizen personalities with 5-dimensional emotional vectors (*Trust, Fear, Altruism, Ambition, Curiosity*) and lifestyle patterns (*Routine, Risk-Aversion, Tech-Savviness, Social Engagement, Health Consciousness*).

### 2. Virtual City Simulation & Democratic Health Analytics
- **Autonomous Activity Observation**: Simulates automated sensors/robots observing population daily activities (exercise, work, socializing, eating, driving, gardening).
- **Social Media Sentiment Feed**: Generates synthetic social media post streams (`SNSPost`) anchored to demographic archetypes and emotional states.
- **Democratic Health Index (DHI)**: Computes macro health indicators across cycles:
  - **Democratic Health Index**: Weighted composite of sentiment, social cohesion, economic health, and participation rate.
  - **Collapse Risk**: Inverse vulnerability measure triggering safety hedges.
  - **Social Cohesion & Economic Health**: Quantified community trust and economic vitality.

### 3. Closed-Loop Autonomous Policy Decision & Parameter Optimization
- **Rule Engine Evaluation**: Dynamically evaluates policy rules (e.g. `RULE-001` Low Democratic Index, `RULE-002` High Collapse Risk, `RULE-003` Low Economic Health) to issue policy recommendations, emergency responses, or resource allocations.
- **Self-Tuning Gradient Optimization**: Adjusts trust, altruism, ambition, and fear parameter weights dynamically between simulation cycles to stabilize democratic health without manual tuning.

### 4. Real-Time Time-Series Visualization & Data Pipeline
- **Real-Time Web Dashboard**: Interactive canvas dashboard with real-time Server-Sent Events (SSE) streaming, parameter tuning sliders, live decision feeds, and system console output.
- **Batch Dataset Export**: 1,000-step simulation history generation in both Go (`build/generate-datafile`) and Python (`generate_datafile.py`) outputting structured CSV and JSON datasets.

### 5. Production Reference Architecture for A2A Protocol Infrastructure
- **Agent Card Discovery**: Standardized `/.well-known/agent-card.json` endpoints detailing capabilities and skills.
- **Zero-Trust Security & Task Lifecycle**: Implements HMAC payload verification, Network ACL subnets, IP rate limiting, PII redaction, tool ACL authorization, and async task state transitions (`submitted` → `working` → `completed` / `failed` / `canceled`).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ata-orchestrator (:8080)                              │
│                                                                                 │
│  ┌─────────────────┐      A2A POST      ┌─────────────────┐      A2A POST       │
│  │ ata-soul-agent  │ ─────────────────► │ ata-city-agent  │ ─────────────────┐  │
│  │     :8081       │                    │     :8082       │                  │  │
│  └────────▲────────┘                    └─────────────────┘                  │  │
│           │                                                                  ▼  │
│           │                                                        ┌───────────┐│
│           │               Optimized Parameters                     │ata-decision││
│           └─────────────────────────────────────────────────────── │   agent   ││
│                                                                    │   :8083   ││
│                                                                    └───────────┘│
└─────────────────────────────────────────────────────────────────────────────────┘

                       ┌─────────────────────────────────────┐
                       │   Real-Time SSE Dashboard (:8050)   │
                       │     visualize_server.py + HTML5     │
                       └─────────────────────────────────────┘
```

### Agent Roles & Port Mapping

| Daemon / Service | Port | Endpoint | Primary Responsibility |
|------------------|------|----------|------------------------|
| **`ata-orchestrator`** | `:8080` | `POST /` | Closed-loop master controller triggering soul→city→decision cycles |
| **`ata-soul-agent`** | `:8081` | `POST /` | Generates & persists synthetic Digital Soul population profiles |
| **`ata-city-agent`** | `:8082` | `POST /` | Simulates city activities, posts, and computes Democratic Health Index |
| **`ata-decision-agent`** | `:8083` | `POST /` | Evaluates policy rules, generates decisions, optimizes weight parameters |
| **`visualize_server.py`** | `:8050` | `GET /` | Python Threading HTTP + SSE streaming server for browser dashboard |

---

## 📁 Project Structure

```
.
├── cmd/                        # Go main entrypoints
│   ├── ata-orchestrator/       # Master controller daemon
│   ├── ata-soul-agent/         # Digital Soul generation agent (A2A server)
│   ├── ata-city-agent/         # Virtual city simulation agent (A2A server)
│   ├── ata-decision-agent/     # Decision & parameter optimization agent (A2A server)
│   └── generate-datafile/      # 1,000-step batch dataset generator binary
│
├── internal/                   # Core Go packages
│   ├── a2a/                    # A2A protocol engine (Server, Client, TaskStore, Guardrails, ACL, HMAC)
│   ├── soul/                   # Digital Soul generator, demographics CSV loader, 5D emotional vectors
│   ├── city/                   # Simulator, observation engine, sentiment feed, democratic health metrics
│   ├── decision/               # Decision engine, rule evaluator, parameter gradient optimizer
│   ├── storage/                # Embedded BoltDB persistence abstraction
│   └── observability/          # Structured JSON logger (log/slog)
│
├── web/                        # Real-time web visualization dashboard
│   ├── index.html              # Modern dashboard layout & control panel
│   ├── style.css               # Clean dark-mode CSS with glassmorphism & responsive grid
│   └── app.js                  # High-performance HTML5 canvas time-series renderer & EventSource client
│
├── configs/                    # Production configuration YAML files
├── data/                       # Datasets, BoltDB files, and exported simulation outputs
│   ├── demographics_source.csv # Census source demographic dataset
│   └── social_media_sentiment.csv # SNS post sentiment templates
│
├── deploy/                     # Linux systemd service units & non-root installation script
├── test/                       # Protocol conformance, red-team security, and build strategy QA tests
│   ├── a2a_protocol_test.go    # Protocol specification & RPC conformance tests
│   ├── build_strategy_test.go  # LDFLAGS, version stamping, & systemd security tests
│   ├── closed_loop_test.go     # End-to-end multi-agent cycle test
│   ├── performance_test.go     # Scale benchmark (up to 5,000 souls)
│   ├── redteam_test.go         # Security resilience, prompt injection, PII, rate-limiting tests
│   └── verify_build_strategy.py# Python build strategy verifier script
│
├── Makefile                    # Standardized build, test, cross-compile, clean targets
├── BUILD_STRATEGY.md           # Compilation, security sandboxing, and QA gate specifications
├── generate_datafile.py        # Python simulation data generator engine
└── visualize_server.py         # Real-time dashboard SSE server
```

---

## 🚀 How to Run

### Prerequisites

- **Go**: Version 1.22 or higher
- **Python**: Version 3.9 or higher (optional, for web dashboard and Python data generator)
- **Make**: Standard build tool (`make`)

---

### Option 1: Run Local Multi-Agent Autonomous Loop (Go Daemons)

#### 1. Build All Binaries

```bash
make build
```
*Binaries are output to `./build/` (`ata-orchestrator`, `ata-soul-agent`, `ata-city-agent`, `ata-decision-agent`, `generate-datafile`).*

#### 2. Launch the 4 Daemons (in separate terminal windows or background)

**Terminal 1 — Soul Agent (`:8081`)**
```bash
./build/ata-soul-agent --listen :8081 --db data/souls.db --demographics data/demographics_source.csv
```

**Terminal 2 — City Agent (`:8082`)**
```bash
./build/ata-city-agent --listen :8082 --db data/city.db --souls-db data/souls.db --sentiment data/social_media_sentiment.csv
```

**Terminal 3 — Decision Agent (`:8083`)**
```bash
./build/ata-decision-agent --listen :8083 --db data/decisions.db --city-db data/city.db
```

**Terminal 4 — Orchestrator Master Daemon (`:8080`)**
```bash
./build/ata-orchestrator --listen :8080 --soul-url http://127.0.0.1:8081 --city-url http://127.0.0.1:8082 --decision-url http://127.0.0.1:8083 --cycle-interval 10s
```

*The orchestrator automatically triggers a full `soul → city → decision` simulation cycle every 10 seconds, printing structured JSON log output.*

---

### Option 2: Run Real-Time Interactive SSE Web Dashboard

To visualize simulation dynamics, parameter drift, democratic health indices, and policy recommendations in real-time:

```bash
python3 visualize_server.py
```

Then open your browser to:
👉 **[http://localhost:8050](http://localhost:8050)**

#### Dashboard Features:
- **Real-Time Canvas Time-Series Charts**: Smooth rendering of Democratic Index vs. Collapse Risk, Social Cohesion vs. Economic Health, and Parameter Weight Drift.
- **Interactive Control Panel**: Adjust citizen count (souls), initial parameter weights (Trust, Altruism, Ambition, Curiosity, Fear), optimizer learning rate, and step delay on the fly.
- **Live Policy Decision Feed**: Real-time stream of triggered rule recommendations and emergency responses.
- **Console Log**: Real-time event log tracking stream progress.

---

### Option 3: Generate 1,000-Step Simulation History Datafiles

To generate time-series CSV and JSON datasets (`t1` through `t1000`) for data analysis or ML training:

#### Using Go Binary:
```bash
./build/generate-datafile --steps 1000 --seed 42 --csv data/simulation_history_t1_t1000.csv --json data/simulation_history_t1_t1000.json
```

#### Using Python Engine:
```bash
python3 generate_datafile.py
```

---

### Option 4: Run Automated Verification & Test Suites

The repository enforces 4 distinct QA gates:

```bash
# Run all Go unit, protocol conformance, red-team, and performance tests
make test

# Run Python build strategy compliance verifier
python3 test/verify_build_strategy.py

# Check code formatting and static analysis
make lint
```

---

### Option 5: Deploy to Production Linux (Systemd & Security Sandboxing)

#### 1. Cross-Compile Static Binaries for Linux `amd64`
```bash
make cross-compile
```
*Binaries are created in `./build/linux-amd64/` with `-s -w -extldflags "-static"` flags.*

#### 2. Execute Linux Installer (On Target Machine)
```bash
sudo ./deploy/install.sh
```
*Creates system user `ata`, installs service units into `/etc/systemd/system/`, and enforces `ProtectSystem=strict` and `ReadWritePaths=/var/lib/ata` file system sandboxing.*

#### 3. Monitor Daemons & System Journal
```bash
systemctl status ata-orchestrator
journalctl -u ata-orchestrator -f
curl http://localhost:8080/healthz
```

---

## 📡 A2A Protocol Interface & Usage

### 1. Agent Card Discovery

Each agent advertises its capabilities via spec-compliant Agent Card endpoints:

```bash
curl -s http://localhost:8081/.well-known/agent-card.json | jq .
```

**Example Response:**
```json
{
  "name": "ATA Soul Agent",
  "description": "Generates synthetic Digital Soul populations with cryptographic identities",
  "url": "http://127.0.0.1:8081",
  "version": "dev",
  "protocolVersion": "1.0.0",
  "skills": [
    {
      "id": "generate",
      "name": "Generate Souls",
      "description": "Generate a population of digital souls"
    }
  ]
}
```

### 2. Sending Synchronous A2A JSON-RPC Request

```bash
curl -s -X POST http://localhost:8081 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "generate 50 souls"}]
      }
    },
    "id": 1
  }' | jq .
```

### 3. Querying Task Status

```bash
curl -s -X POST http://localhost:8081 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/get",
    "params": {
      "id": "YOUR_TASK_ID"
    },
    "id": 2
  }' | jq .
```

---

## 🔒 Security & Conformance

- **Non-Root Systemd Units**: Daemons run as restricted system user `ata` with `NoNewPrivileges=true`.
- **Read-Only File System**: Sandboxed via `ProtectSystem=strict` with write access restricted strictly to `/var/lib/ata`.
- **HMAC Signatures**: Payload integrity validation using SHA-256 HMAC headers (`X-A2A-Signature`).
- **Network Access Control List (NACL)**: Restricts inbound RPCs to specified CIDR subnets.
- **IP Rate Limiting**: Automatic token-bucket rate limiting per IP.
- **PII Redaction & Guardrails**: Built-in regex filters for redacting sensitive fields (SSN, credit card, emails) and blocking prompt injections.

---

## 📜 License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for more information.
