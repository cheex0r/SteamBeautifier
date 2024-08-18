#!/usr/bin/env bash

# Function to detect Linux distribution
detect_linux_distribution() {
    if [ -f /etc/os-release ]; then
        # Source the os-release file
        . /etc/os-release
        if [ -n "$ID" ]; then
            echo "$ID"
        elif [ -n "$DISTRIB_ID" ]; then
            echo "$DISTRIB_ID"
        fi
    fi
}

# Install Python 3 based on the detected distribution
install_python() {
    local distribution=$(detect_linux_distribution)
    case "$distribution" in
        debian|ubuntu|linuxmint)
            echo "Installing Python 3 for Debian-based systems"
            sudo apt-get update
            sudo apt-get install -y python3
            ;;
        centos|rhel)
            echo "Installing Python 3 for Red Hat-based systems"
            sudo yum update
            sudo yum install -y python3
            ;;
        fedora)
            echo "Installing Python 3 for Fedora-based systems"
            sudo dnf update
            sudo dnf install -y python3
            ;;
        *)
            echo "Unsupported distribution: $distribution"
            exit 1
            ;;
    esac
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3"
    install_python
fi

# Create a virtual environment if it doesn't already exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

python3 src/main.py

# Deactivate the virtual environment when done
deactivate
