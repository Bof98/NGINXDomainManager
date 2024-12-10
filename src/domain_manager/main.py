# main.py

"""
DomainManager.py - A Python-based script to manage Nginx subdomains with SSL certificates.
Version: 2.0.9

Requires: Python 3.6+, PyYAML, colorama
"""

# Main Function
import os
import sys
import subprocess
from colorama import init

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from domain_manager.config import load_config
from domain_manager.logger import setup_logging, show_logs, show_changelog
from domain_manager.updater import check_for_updates
from domain_manager.utils.display import display_startup, main_menu
from domain_manager.utils.permissions import check_permissions

# Initialize colorama
init(autoreset=True)


def get_current_version():
    """Fetch the current version from Git tags."""
    try:
        # Run `git describe --tags --abbrev=0` to get the latest tag without commit hash
        version_str = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            universal_newlines=True,
        ).strip()
        return version_str
    except subprocess.CalledProcessError:
        print(Fore.RED + "Unable to determine version from Git. Defaulting to '0.0.0'.")
        return "0.0.0"


# Application version (dynamically fetched)
__version__ = get_current_version()

# Package details
package_name = "NGINXDomainManager"


def main():
    # Ensure the script is run as root/admin
    check_permissions()

    # Load configuration
    config = load_config()
    logger = setup_logging(config['log_file'])

    # Display startup graphic
    display_startup(__version__)

    # Check for updates before proceeding
    check_for_updates()

    # Load configuration again in case it was updated
    config = load_config()

    # Setup logging again in case it was updated
    logger = setup_logging(config['log_file'])

    # Proceed with the main menu
    main_menu(config, __version__)  # Pass both config and __version__


if __name__ == "__main__":
    main()
