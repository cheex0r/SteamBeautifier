#!/usr/bin/env bash

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

START_SCRIPT_PATH="$SCRIPT_DIR/start_steambeautifier_linux.sh"

# Create systemd service unit file
cat <<EOF | sudo tee /etc/systemd/system/steambeautifier.service >/dev/null
[Unit]
Description=Steam Beautifier
After=network.target

[Service]
Type=forking
ExecStart=$START_SCRIPT_PATH

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable steambeautifier.service
sudo systemctl start steambeautifier.service

# Verify status
sudo systemctl status steambeautifier.service
