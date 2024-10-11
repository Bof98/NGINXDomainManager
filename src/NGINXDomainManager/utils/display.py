# Display Startup Graphic
import logging
import sys

from colorama import Fore

from src.NGINXDomainManager.config import configure_settings, create_nginx_config
from src.NGINXDomainManager.logger import show_logs, show_changelog
from src.NGINXDomainManager.utils.domain import list_subdomains, get_subdomain_details, delete_subdomain, \
    obtain_certificate, reload_nginx
from src.NGINXDomainManager.utils.validation import validate_subdomain, validate_ip, validate_port


def display_startup(version):
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
    print(f"Version: {version}\n")


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


# Main Menu
def main_menu(config):
    while True:
        print("\nWhat would you like to do?")
        print("1) Create a new subdomain")
        print("2) Edit an existing subdomain")
        print("3) Update existing domains")
        print("4) Delete a subdomain")
        print("5) View logs")
        print("6) View changelog")
        print("7) Configure settings")
        print("8) Exit")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == '1':
            # Create a new subdomain
            subdomain = input("Enter your subdomain (e.g., app.example.com): ").strip()
            target_ip = input("Enter the internal IP address of the target server (e.g., 192.168.0.215): ").strip()
            target_port = input("Enter the port the target service is running on (e.g., 8080): ").strip()

            if not validate_subdomain(subdomain) or not validate_ip(target_ip) or not validate_port(target_port):
                continue

            create_nginx_config(config, subdomain, target_ip, target_port)
            obtain_certificate(subdomain)
            reload_nginx()

            print(Fore.GREEN + f"Nginx configuration and SSL setup for {subdomain} complete!")
            logging.info(f"Nginx configuration and SSL setup for {subdomain} complete!")

        elif choice == '2':
            # Edit an existing subdomain
            subdomains = list_subdomains(config)
            if not subdomains:
                continue
            selection = input("Select the number of the subdomain you want to edit: ").strip()
            details = get_subdomain_details(config, selection)
            if not details:
                print(Fore.RED + "Invalid selection. Please check the number and try again.")
                continue
            subdomain, current_ip, current_port = details
            print(f"Editing subdomain: {subdomain} (Current IP: {current_ip}, Current Port: {current_port})")
            new_ip = input(f"Enter the new internal IP address for {subdomain} [{current_ip}]: ").strip() or current_ip
            new_port = input(f"Enter the new port for {subdomain} [{current_port}]: ").strip() or current_port

            if not validate_ip(new_ip) or not validate_port(new_port):
                continue

            create_nginx_config(config, subdomain, new_ip, new_port)
            obtain_certificate(subdomain)
            reload_nginx()

            print(Fore.GREEN + f"Nginx configuration and SSL setup for {subdomain} updated!")
            logging.info(f"Nginx configuration and SSL setup for {subdomain} updated!")

        elif choice == '3':
            # Update existing domains
            print("Updating SSL certificates for all existing domains...")
            subdomains = list_subdomains(config)
            if not subdomains:
                continue
            for sub in subdomains:
                print(f"Updating SSL certificate for {sub}...")
                obtain_certificate(sub)
            reload_nginx()
            print(Fore.GREEN + "All domains updated.")
            logging.info("All domains updated.")

        elif choice == '4':
            # Delete a subdomain
            subdomains = list_subdomains(config)
            if not subdomains:
                continue
            selection = input("Select the number of the subdomain you want to delete: ").strip()
            details = get_subdomain_details(config, selection)
            if not details:
                print(Fore.RED + "Invalid selection. Please check the number and try again.")
                continue
            subdomain = details[0]
            confirmation = input(
                f"Are you sure you want to delete the subdomain {subdomain}? This action cannot be undone. (yes/no): ").strip().lower()
            if confirmation != 'yes':
                print(Fore.YELLOW + "Deletion cancelled.")
                continue
            delete_subdomain(config, subdomain)

        elif choice == '5':
            # View logs
            show_logs(config)

        elif choice == '6':
            # View changelog
            show_changelog()

        elif choice == '7':
            # Configure settings
            configure_settings(config)

        elif choice == '8':
            # Exit
            print(Fore.CYAN + "Goodbye!")
            sys.exit(0)

        else:
            print(Fore.RED + "Invalid option. Try again.")
            continue

        # Wait for user to press Enter before returning to the menu
        input("Press Enter to return to the main menu...")
