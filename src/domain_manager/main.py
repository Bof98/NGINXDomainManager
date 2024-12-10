"""
DomainManager.py - A Python-based script to manage Nginx subdomains with SSL certificates.
Version: 2.0.9

Requires: Python 3.6+, PyYAML, colorama
"""

# Main Function
import os
import sys

from colorama import init

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from domain_manager.config import load_config
from domain_manager.logger import setup_logging
from domain_manager.updater import check_for_updates
from domain_manager.utils.display import display_startup, main_menu
from domain_manager.utils.permissions import check_permissions

# Application version
__version__ = "1.0.3"

# Package details
package_name = "NGINXDomainManager"

# Initialize colorama
init(autoreset=True)


def main():
    # Ensure the script is run as root/admin
    check_permissions()

    # Check for updates before proceeding
    check_for_updates()

    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config['log_file'])

    # Display startup graphic
    display_startup(__version__)

    # Proceed with the main menu
    main_menu(config)


if __name__ == "__main__":
    main()
