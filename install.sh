#!/bin/bash

# ===== Theoryma MySQL Auto User - Installer =====
# By Febrian Dani Ritonga

set -e

echo "========================================"
echo "  Theoryma MySQL Auto User Installer"
echo "  Web Management Tool"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Variables - use current directory
INSTALL_DIR="$(pwd)"
SERVICE_NAME="mysql-auto-user"
PORT=${1:-5000}

echo "[1/6] Installing dependencies..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv

echo "[2/6] Current directory: $INSTALL_DIR"

echo "[3/6] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask

echo "[4/6] Creating systemd service..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Theoryma MySQL Auto User Web Manager
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
Environment=PATH=${INSTALL_DIR}/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[5/6] Enabling and starting service..."
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

echo "[6/6] Setting up firewall (if UFW is active)..."
if command -v ufw &> /dev/null; then
    ufw allow ${PORT}/tcp 2>/dev/null || true
fi

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Installed at: ${INSTALL_DIR}"
echo ""
echo "Access your MySQL Manager at:"
echo "  http://${SERVER_IP}:${PORT}"
echo "  http://localhost:${PORT}"
echo ""
echo "Service commands:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo "  sudo systemctl stop ${SERVICE_NAME}"
echo ""
echo "Logs:"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "========================================"
