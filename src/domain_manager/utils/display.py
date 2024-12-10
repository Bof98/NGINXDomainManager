# Display Startup Graphic
import logging
import os
from colorama import Fore
from domain_manager.logger import show_logs, show_changelog, setup_logging
from domain_manager.utils.domain import list_subdomains, get_subdomain_details, delete_subdomain, \
    obtain_certificate, reload_nginx
from domain_manager.utils.validation import validate_subdomain, validate_ip, validate_port
from domain_manager.utils.fix_nginx import fix_nginx_configuration
from domain_manager.utils.reset_configs import reset_all_configurations

package_name = "NGINXDomainManager"


def get_github_version():
    """Fetch the latest version tag from GitHub."""
    import requests
    try:
        url = "https://api.github.com/repos/Bof98/NGINXDomainManager/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        latest_version = response.json().get('tag_name', 'Unknown')
        return latest_version
    except Exception as e:
        logging.error(f"Failed to fetch the latest version from GitHub: {e}")
        return "Unknown"

def display_startup(version):
    """Display the startup graphic with the current version and GitHub version."""
    github_version = get_github_version()
    startup_graphic = f"""
######################################################################################
#   _____                        _         __  __                                    #
#  |  __ \\                      (_)       |  \\/  |                                   #
#  | |  | | ___  _ __ ___   __ _ _ _ __   | \\  / | __ _ _ __   __ _  __ _  ___ _ __  #
#  | |  | |/ _ \\| '_ ` _ \\ / _` | | '_ \\  | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__| #
#  | |__| | (_) | | | | | | (_| | | | | | | |  | | (_| | | | | (_| | (_| |  __/ |    #
#  |_____/ \\___/|_| |_| |_|\\__,_|_|_| |_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|    #
#                                                                    __/ |           #
#                                                                   |___/            #
######################################################################################
    """
    print(Fore.CYAN + startup_graphic)
    print(f"Current Version: {version}")
    print(f"GitHub Latest Version: {github_version}\n")

# Display Help
def display_help():
    help_text = """
NGINX Domain Manager - Manage Nginx subdomains with SSL certificates.

Usage:
    sudo python3 domain_manager.py

Options:
    1) Create a new subdomain
    2) Edit an existing subdomain
    3) Update existing domains
    4) Delete a subdomain
    5) View logs
    6) View changelog
    7) Configure settings
    8) Exit
    """
    print(help_text)


def clear_terminal():
    """Clear the terminal screen."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

# Main Menu
def main_menu(config, version):
    logger = setup_logging(config['log_file'])
    while True:
        print("\nWhat would you like to do?")
        print("1) Create a new subdomain")
        print("2) Edit an existing subdomain")
        print("3) Update existing domains")
        print("4) Delete a subdomain")
        print("5) Settings")
        print("6) Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            # Create a new subdomain
            # ... existing code ...

        elif choice == '2':
            # Edit an existing subdomain
            # ... existing code ...

        elif choice == '3':
            # Update existing domains
            # ... existing code ...

        elif choice == '4':
            # Delete a subdomain
            # ... existing code ...

        elif choice == '5':
            while True:
                print("\nSettings Menu:")
                print("1) View logs")
                print("2) View Changelog")
                print("3) Configure settings")
                print("4) Check for updates")
                print("5) Fix Nginx Configuration and SSL Certificates")
                print("6) Reset All Configurations")  # New Option
                print("7) Go back to the main menu")

                sub_choice = input("Enter your choice (1-7): ").strip()

                if sub_choice == '1':
                    # View logs
                    show_logs(config, logger)

                elif sub_choice == '2':
                    # View changelog
                    show_changelog(logger)

                elif sub_choice == '3':
                    # Configure settings
                    configure_settings(config)

                elif sub_choice == '4':
                    # Check for updates
                    check_for_updates()
                    break

                elif sub_choice == '5':
                    # Fix Nginx Configuration and SSL Certificates
                    print("Fixing Nginx configuration and handling SSL certificate issues...")
                    fix_nginx_configuration(config, logger)
                    print(Fore.GREEN + "Nginx configuration and SSL certificates fixed.")
                    logger.info("Nginx configuration and SSL certificates fixed.")

                elif sub_choice == '6':
                    # Reset All Configurations
                    confirm = input(Fore.RED + "Are you sure you want to reset all Nginx configurations? This will delete all existing configurations and recreate them based on the current settings. (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        reset_all_configurations(config, logger)
                        print(Fore.GREEN + "All Nginx configurations have been reset.")
                        logger.info("All Nginx configurations have been reset.")
                    else:
                        print(Fore.YELLOW + "Reset operation cancelled.")

                elif sub_choice == '7':
                    # Go back to the main menu
                    break

                else:
                    print(Fore.RED + "Invalid option. Try again.")
                    continue

        elif choice == '6':
            # Exit
            print("Goodbye!")
            break

        else:
            print(Fore.RED + "Invalid option. Try again.")
            continue

        # Wait for user to press Enter before returning to the menu
        input("Press Enter to return to the main menu...")
        clear_terminal()
        display_startup(version)
