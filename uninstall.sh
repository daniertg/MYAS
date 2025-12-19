#!/bin/bash

# ===== Theoryma MySQL Auto User - Uninstaller =====

set -e

SERVICE_NAME="mysql-auto-user"
INSTALL_DIR="/opt/mysql-auto-user"

echo "========================================"
echo "  Theoryma MySQL Auto User Uninstaller"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./uninstall.sh)"
    exit 1
fi

read -p "Yakin ingin uninstall MySQL Auto User? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo "[1/4] Stopping service..."
systemctl stop ${SERVICE_NAME} 2>/dev/null || true
systemctl disable ${SERVICE_NAME} 2>/dev/null || true

echo "[2/4] Removing service file..."
rm -f /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload

echo "[3/4] Removing installation directory..."
rm -rf ${INSTALL_DIR}

echo "[4/4] Done!"
echo ""
echo "MySQL Auto User has been uninstalled."
echo ""
