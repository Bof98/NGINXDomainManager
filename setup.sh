#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Define variables
REPO_DIR=$(pwd)
VENV_DIR="$REPO_DIR/venv"
CONFIG_FILE="$REPO_DIR/config.yaml"

echo "Starting setup for NGINX Domain Manager..."

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

# Update system and install dependencies
echo "Updating system and installing dependencies..."
apt update
apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r "$REPO_DIR/requirements.txt"

# Configure NGINX Domain Manager
echo "Configuring NGINX Domain Manager..."
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Configuration file not found! Please ensure $CONFIG_FILE exists."
    exit 1
fi

# Ensure NGINX service is running
echo "Starting and enabling NGINX..."
systemctl enable nginx
systemctl start nginx

# Test NGINX configuration
echo "Testing NGINX configuration..."
if ! nginx -t; then
    echo "NGINX configuration test failed. Please check your NGINX setup."
    exit 1
fi

# Final message
echo "Setup complete! You can now run the NGINX Domain Manager:"
echo "    sudo python3 domain_manager.py"
