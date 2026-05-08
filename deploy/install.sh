#!/usr/bin/env bash
# ATA Linux Installer
# Installs ATA agent binaries and systemd services.
# Run as root on the target Linux machine.
set -euo pipefail

BINARY_DIR="/usr/local/bin"
DATA_DIR="/var/lib/ata"
CONFIG_DIR="/etc/ata"
SERVICE_DIR="/etc/systemd/system"
BINARIES=(ata-orchestrator ata-soul-agent ata-city-agent ata-decision-agent)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/../build/linux-amd64"

echo "==> ATA Linux Installer"
echo ""

# Check root.
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root."
    exit 1
fi

# Check binaries exist.
for bin in "${BINARIES[@]}"; do
    if [ ! -f "${BUILD_DIR}/${bin}" ]; then
        echo "ERROR: Binary not found: ${BUILD_DIR}/${bin}"
        echo "       Run 'make cross-compile' first."
        exit 1
    fi
done

# Create ata user/group.
echo "==> Creating ata user..."
if ! id -u ata &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin ata
fi

# Create directories.
echo "==> Creating directories..."
mkdir -p "${DATA_DIR}"
mkdir -p "${CONFIG_DIR}"
chown ata:ata "${DATA_DIR}"

# Copy binaries.
echo "==> Installing binaries to ${BINARY_DIR}..."
for bin in "${BINARIES[@]}"; do
    cp "${BUILD_DIR}/${bin}" "${BINARY_DIR}/${bin}"
    chmod 755 "${BINARY_DIR}/${bin}"
    echo "    ${bin}"
done

# Copy configs.
echo "==> Installing configs to ${CONFIG_DIR}..."
cp "${SCRIPT_DIR}/../configs/"*.yaml "${CONFIG_DIR}/" 2>/dev/null || true

# Install systemd services.
echo "==> Installing systemd services..."
for svc in "${SCRIPT_DIR}/systemd/"*.service; do
    cp "${svc}" "${SERVICE_DIR}/"
    echo "    $(basename "${svc}")"
done

# Reload systemd.
systemctl daemon-reload

# Enable services.
echo "==> Enabling services..."
for bin in "${BINARIES[@]}"; do
    systemctl enable "${bin}.service"
done

# Start services.
echo "==> Starting services..."
systemctl start ata-soul-agent
sleep 1
systemctl start ata-city-agent
sleep 1
systemctl start ata-decision-agent
sleep 1
systemctl start ata-orchestrator

echo ""
echo "==> ATA installed successfully!"
echo ""
echo "    Check status:  systemctl status ata-orchestrator"
echo "    View logs:     journalctl -u ata-orchestrator -f"
echo "    Agent Cards:   curl http://localhost:8080/.well-known/agent.json"
echo "    Health check:  curl http://localhost:8080/healthz"
echo ""
