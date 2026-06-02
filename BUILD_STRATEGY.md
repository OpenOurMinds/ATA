# ATA Build Strategy

This document defines the compilation, optimization, security sandboxing, and validation guidelines for building and packaging the ATA multi-agent system.

---

## 1. Compilation & Linker Flag Strategy

To maintain a headless, low-overhead environment, the ATA binaries must be compiled with strict compiler and linker flags.

### production Optimizations
Binaries compiled for production must strip debugging information and symbols to reduce the footprint.
- **`-s`**: Omit the symbol table and debug information.
- **`-w`**: Omit the DWARF generation.

### Static Compilation
To ensure the binaries are zero-dependency and deployable without relying on standard system libraries (e.g., glibc compatibility), static linking must be enabled:
- **`-extldflags "-static"`**: Force static compilation.

### Linker Variable Injection (Stamping)
Version control tags, branch status, and build timestamps must be injected at compilation time using linker flags:
- **`-X main.version=$(VERSION)`**: Binds the Git release tag or hash to the `version` variable in main entrypoints.

### Standard Build Command
```bash
go build -ldflags "-s -w -extldflags '-static' -X main.version=$(VERSION)" -o build/bin ./cmd/...
```

---

## 2. Multi-Platform Strategy

ATA is designed to be cross-compiled from any development host (e.g., macOS or Windows) to the target deployment architecture (Linux amd64).

- **Production Target**: `GOOS=linux GOARCH=amd64`
- **Development Target**: Host-native compilation (automatic when executing `make build`)

The build pipeline maintains a distinct output structure:
- `build/` — Host-native binaries for local testing/development.
- `build/linux-amd64/` — Cross-compiled static binaries for target Linux deployment.

---

## 3. Systemd Sandboxing & Security Guidelines

To enforce a secure runtime, the installation script (`deploy/install.sh`) and service units (`deploy/systemd/*.service`) must comply with the following sandboxing principles:

1. **Non-Root Execution**:
   - Daemons must run under the system user `ata` and group `ata`.
   - Privilege escalation must be disabled: `NoNewPrivileges=true`.
2. **File System Isolation**:
   - The root file system must be mounted read-only for the process: `ProtectSystem=strict`.
   - Write permissions must be strictly isolated to the database storage directory: `ReadWritePaths=/var/lib/ata`.
3. **Process Lifecycle**:
   - Units must configure automatic restarts on failure (`Restart=on-failure`, `RestartSec=5`).
   - Logging must flow to the system journal: `StandardOutput=journal` and `StandardError=journal`.

---

## 4. Containerization (Docker) Strategy

When containerizing agents, a multi-stage Docker build must be used to minimize target image sizes and reduce the attack surface.

### Multi-stage Dockerfile Blueprint
```dockerfile
# Stage 1: Build
FROM golang:1.22-alpine AS builder
RUN apk add --no-cache git make
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags "-s -w -extldflags '-static' -X main.version=$(git describe --tags --always)" \
    -o /app/bin/ata-orchestrator ./cmd/ata-orchestrator

# Stage 2: Distribute
FROM scratch
COPY --from=builder /app/bin/ata-orchestrator /ata-orchestrator
ENTRYPOINT ["/ata-orchestrator"]
```

---

## 5. QA Gates & Automated Validation

Before any build is considered a release candidate, it must satisfy four distinct validation gates:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Unit Tests  │ ──► │  A2A Scenarios │ ──► │   Red-Team   │ ──► │Build Strategy│
│  (go test)   │     │ (conformance)│     │ (resilience) │     │ (conformance)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **Unit & Race Tests**: Verify logical correctness with race detection (`go test -race ./internal/...`).
2. **Protocol Conformance**: Verify that the A2A API conforms to version `1.0.0` (`go test ./test/...`).
3. **Resilience scenarios**: Run scenario tests simulating client timeout, server down, and data corruption.
4. **Build Strategy Verification**: Check that compilation flags, version-stamping parameters, configuration defaults, and systemd definitions match target specifications.
