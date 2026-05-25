.PHONY: all build test clean install lint cross-compile

BINARIES := ata-orchestrator ata-soul-agent ata-city-agent ata-decision-agent
BUILD_DIR := build
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
LDFLAGS := -ldflags "-s -w -X main.version=$(VERSION)"

all: build

build:
	@echo "==> Building all agents..."
	@mkdir -p $(BUILD_DIR)
	@for bin in $(BINARIES); do \
		echo "    $$bin"; \
		go build $(LDFLAGS) -o $(BUILD_DIR)/$$bin ./cmd/$$bin/; \
	done
	@echo "==> Done. Binaries in $(BUILD_DIR)/"

test:
	@echo "==> Running tests..."
	go test ./internal/... -v -race -count=1
	go test ./test/... -v -race -count=1 -timeout 60s

lint:
	@echo "==> Running vet..."
	go vet ./...

cross-compile:
	@echo "==> Cross-compiling for Linux amd64..."
	@mkdir -p $(BUILD_DIR)/linux-amd64
	@for bin in $(BINARIES); do \
		echo "    $$bin"; \
		GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/linux-amd64/$$bin ./cmd/$$bin/; \
	done
	@echo "==> Done. Binaries in $(BUILD_DIR)/linux-amd64/"

clean:
	rm -rf $(BUILD_DIR)

install: cross-compile
	@echo "==> Run deploy/install.sh on target Linux machine"
