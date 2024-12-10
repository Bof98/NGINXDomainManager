#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Define variables
REPO_DIR=$(pwd)
VENV_DIR="$REPO_DIR/venv"
CONFIG_FILE="$REPO_DIR/src/domain_manager/config.yaml"
EXECUTABLE="/usr/local/bin/NGINXDomainManager"

# Function to execute a step and overwrite the line dynamically
run_step() {
    local -r msg="$1"
    local -r cmd="$2"
    printf "%-50s" "$msg..."
    {
        eval "$cmd" >/dev/null 2>&1
        printf "\r%-50s✔\n" "$msg"
    } || {
        printf "\r%-50s✖\n" "$msg"
        echo "Error occurred during: $msg"
        exit 1
    }
}

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    echo -e "\e[31mError: Please run this script as root.\e[0m"
    exit 1
fi

# Display the setup header
echo "NGINX Domain Manager Setup"
echo "=========================="

# Step 1: Update system and install dependencies
run_step "Updating system and installing dependencies" \
    "apt update && apt install -y nginx python3 python3-pip python3-venv certbot python3-certbot-nginx"

# Step 2: Set up Python virtual environment
run_step "Setting up Python virtual environment" \
    "[ ! -d \"$VENV_DIR\" ] && python3 -m venv \"$VENV_DIR\""
source "$VENV_DIR/bin/activate"

# Step 3: Install Python dependencies
run_step "Installing Python dependencies" \
    "pip install -r \"$REPO_DIR/requirements.txt\""

# Step 4: Verify configuration file
run_step "Verifying configuration file" \
    "[ -f \"$CONFIG_FILE\" ] || (echo \"Configuration file not found! Please ensure it exists.\" && exit 1)"

# Step 5: Start and enable NGINX service
run_step "Starting and enabling NGINX service" \
    "systemctl enable nginx && systemctl start nginx"

# Step 6: Test NGINX configuration
run_step "Testing NGINX configuration" \
    "nginx -t"

# Step 7: Create an executable script in /usr/local/bin
run_step "Creating NGINXDomainManager command" \
    "echo '#!/bin/bash
export PYTHONPATH=\"$REPO_DIR/src:\$PYTHONPATH\"
source $VENV_DIR/bin/activate
python3 $REPO_DIR/src/domain_manager/main.py \"\$@\"' > $EXECUTABLE && chmod +x $EXECUTABLE"

# Final message
echo "=========================="
echo -e "\e[32mSetup complete!\e[0m"
echo "You can now run the NGINX Domain Manager using the command:"
echo "    sudo NGINXDomainManager"
