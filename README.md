# ATA — Agent To Agent

A headless, multi-agent system built on the [A2A protocol](https://github.com/a2aproject/A2A) (JSON-RPC 2.0 over HTTP). Four autonomous daemons coordinate via standard Agent Cards to simulate synthetic populations, run virtual city dynamics, and optimize system parameters in a closed loop — with zero human interface.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 ata-orchestrator (:8080)             │
│                                                     │
│  ┌──────────┐   A2A    ┌──────────┐  A2A  ┌──────┐ │
│  │  soul    │ ───────► │  city    │ ────► │ dec. │ │
│  │  agent   │          │  agent   │       │ agent│ │
│  │  :8081   │          │  :8082   │       │ :8083│ │
│  └────▲─────┘          └──────────┘       └──┬───┘ │
│       │                                      │     │
│       └──── optimized parameters ────────────┘     │
└─────────────────────────────────────────────────────┘
```

**Each agent** exposes:
- `/.well-known/agent-card.json` — Agent Card (identity, capabilities, protocol version)
- `POST /` — JSON-RPC 2.0 endpoint (`message/send`, `message/stream`, `tasks/get`, `tasks/cancel`)
- `GET /healthz` — Health check

## Language: Go

| Criterion | Why Go |
|-----------|--------|
| No human interface | Single static binary — no runtime, no dependencies |
| Concurrency | Goroutines handle thousands of concurrent agents |
| A2A Protocol | Official `a2a-go` SDK; `net/http` is production-grade |
| Linux daemon | First-class systemd integration |
| Cross-compile | `GOOS=linux GOARCH=amd64 go build` → deploy anywhere |

## Project Structure

```
cmd/                    # 4 agent binaries
  ata-orchestrator/     # Master daemon: closed-loop controller
  ata-soul-agent/       # Digital Soul generator (A2A server)
  ata-city-agent/       # City simulation engine (A2A server)
  ata-decision-agent/   # Decision engine + optimizer (A2A server)

internal/               # Private packages
  a2a/                  # A2A protocol: Agent Card, JSON-RPC, Task lifecycle
  soul/                 # Soul generation, archetypes, emotional vectors
  city/                 # Simulation: observe → generate posts → analyze health
  decision/             # Rule engine, parameter optimization
  storage/              # BoltDB embedded persistence
  observability/        # Structured JSON logging (log/slog)

configs/                # YAML configuration files
deploy/                 # systemd units + Linux installer
test/                   # Protocol conformance + integration tests
```

## Quick Start

### Build

```bash
make build           # Build all 4 binaries
make cross-compile   # Cross-compile for Linux amd64
make test            # Run all tests
```

### Run Locally (Development)

```bash
# Terminal 1: Soul Agent
./build/ata-soul-agent --listen :8081 --db data/souls.db

# Terminal 2: City Agent
./build/ata-city-agent --listen :8082 --db data/city.db --souls-db data/souls.db

# Terminal 3: Decision Agent
./build/ata-decision-agent --listen :8083 --db data/decisions.db --city-db data/city.db

# Terminal 4: Orchestrator (starts autonomous loop)
./build/ata-orchestrator --cycle-interval 10s
```

### Verify Agent Cards

```bash
curl http://localhost:8080/.well-known/agent-card.json | jq .
curl http://localhost:8081/.well-known/agent-card.json | jq .
curl http://localhost:8082/.well-known/agent-card.json | jq .
curl http://localhost:8083/.well-known/agent-card.json | jq .
```

### Send A2A Request

```bash
curl -X POST http://localhost:8081 \
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
  }'
```

## Deploy to Linux

```bash
# On build machine (macOS or Linux):
make cross-compile

# Copy build/linux-amd64/ to target, then:
sudo ./deploy/install.sh

# Verify:
systemctl status ata-orchestrator
journalctl -u ata-orchestrator -f
curl http://localhost:8080/healthz
```

## A2A Protocol Compliance

| Feature | Status |
|---------|--------|
| Agent Card at `/.well-known/agent-card.json` | ✅ |
| Protocol version negotiation (`protocolVersion`) | ✅ |
| Provider metadata | ✅ |
| JSON-RPC 2.0 transport | ✅ |
| Task lifecycle (submitted → working → completed/failed) | ✅ |
| `message/send` (synchronous) | ✅ |
| `message/stream` (SSE streaming) | ✅ |
| `tasks/get` | ✅ |
| `tasks/cancel` | ✅ |
| `tasks/pushNotificationConfig/set` | ✅ |
| `tasks/pushNotificationConfig/get` | ✅ |
| State transition history | ✅ |
| Session ID tracking (multi-turn context) | ✅ |
| `auth-required` state | ✅ |
| `input-required` state (human-in-the-loop) | ✅ |
| Auth middleware hook (OAuth 2.0 ready) | ✅ |
| Structured error codes | ✅ |

## Data Persistence

All data is stored in embedded [BoltDB](https://github.com/etcd-io/bbolt) databases:
- `/var/lib/ata/souls.db` — Digital Soul profiles
- `/var/lib/ata/city.db` — Simulation results & metrics
- `/var/lib/ata/decisions.db` — Decision history & parameters

## License

See [LICENSE](LICENSE) file.
