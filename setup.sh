#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Define variables
REPO_DIR=$(pwd)
VENV_DIR="$REPO_DIR/venv"
CONFIG_FILE="$REPO_DIR/src/domain_manager/config.yaml"

# Function to show a progress bar
show_progress() {
    local -r msg="$1"
    local -r delay="${2:-0.2}"
    local -r spinner="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    while true; do
        for (( i=0; i<${#spinner}; i++ )); do
            printf "\r%s %s" "${spinner:$i:1}" "$msg"
            sleep "$delay"
        done
    done
}

# Step function to run a task with a progress bar
run_step() {
    local -r msg="$1"
    local -r cmd="$2"
    show_progress "$msg" &
    local pid=$!
    {
        eval "$cmd" >/dev/null 2>&1
        kill -9 "$pid"
    } & wait "$!" 2>/dev/null
    printf "\r✔ %s\n" "$msg"
}

echo "Starting setup for NGINX Domain Manager..."

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

# Step 1: Update system and install dependencies
run_step "Updating system and installing dependencies..." "apt update && apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx"

# Step 2: Create and activate virtual environment
run_step "Setting up Python virtual environment..." "[ ! -d \"$VENV_DIR\" ] && python3 -m venv \"$VENV_DIR\""
source "$VENV_DIR/bin/activate"

# Step 3: Install Python dependencies
run_step "Installing Python dependencies..." "pip install -r \"$REPO_DIR/requirements.txt\""

# Step 4: Check for configuration file
run_step "Checking for configuration file..." "[ -f \"$CONFIG_FILE\" ] || (echo \"Configuration file not found! Please ensure it exists.\" && exit 1)"

# Step 5: Ensure NGINX service is running
run_step "Starting and enabling NGINX..." "systemctl enable nginx && systemctl start nginx"

# Step 6: Test NGINX configuration
run_step "Testing NGINX configuration..." "nginx -t"

# Final message
echo "Setup complete! You can now run the NGINX Domain Manager:"
echo "    sudo python3 domain_manager.py"
