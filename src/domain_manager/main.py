"""
DomainManager.py - A Python-based script to manage Nginx subdomains with SSL certificates.
Version: 1.0.3

Requires: Python 3.6+, PyYAML, colorama
"""

# Main Function
from colorama import init

from config import load_config
from logger import setup_logging
from updater import check_for_updates, apply_update
from utils.display import display_startup, main_menu
from utils.permissions import check_permissions

# Version Variable
__version__ = "1.6.0"

# Initialize colorama
init(autoreset=True)


def main():
    # Apply any pending updates
    apply_update()

    # Ensure the script is run as root/admin
    check_permissions()

    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config['log_file'])

    # Display startup graphic
    display_startup(__version__)

    # Check for updates
    check_for_updates(__version__)

    # Proceed with the main menu
    main_menu(config)


if __name__ == "__main__":
    main()
