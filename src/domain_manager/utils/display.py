# domain_manager/utils/display.py

import logging
import os
from colorama import Fore, Style
from domain_manager.logger import show_logs, show_changelog, setup_logging
from domain_manager.config import configure_settings
from domain_manager.utils.domain import list_subdomains, get_subdomain_details, delete_subdomain, \
    obtain_certificate, reload_nginx
from domain_manager.utils.validation import validate_subdomain, validate_ip, validate_port
from domain_manager.utils.fix_nginx import fix_nginx_configuration
from domain_manager.utils.reset_configs import reset_all_configurations
from domain_manager.updater import check_for_updates

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
            subdomain = input("Enter your subdomain (e.g., app.example.com): ").strip()
            target_ip = input("Enter the internal IP address of the target server (e.g., 192.168.0.215): ").strip()
            target_port = input("Enter the port the target service is running on (e.g., 8080): ").strip()

            if not validate_subdomain(subdomain) or not validate_ip(target_ip) or not validate_port(target_port):
                continue

            # Fetch custom options if any
            custom_options = []
            add_custom = input("Do you want to add custom Nginx options for this subdomain? (y/n): ").strip().lower()
            while add_custom == 'y':
                option = input("Enter custom Nginx directive (leave blank to stop): ").strip()
                if option:
                    custom_options.append(option)
                else:
                    break
                add_custom = input("Add another custom option? (y/n): ").strip().lower()

            # Update config.yaml
            config['subdomains'][subdomain] = {
                'target_ip': target_ip,
                'target_port': target_port,
                'custom_options': custom_options
            }
            with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'w') as f:
                import yaml
                yaml.dump(config, f)

            # Create Nginx config
            create_nginx_config(subdomain, target_ip, target_port, custom_options, logger)

            # Obtain SSL certificate
            success = obtain_certificate(subdomain)
            if success:
                logger.info(f"SSL certificate obtained for {subdomain}.")
                print(Fore.GREEN + f"SSL certificate obtained for {subdomain}.")
            else:
                logger.error(f"Failed to obtain SSL certificate for {subdomain}.")
                print(Fore.RED + f"Failed to obtain SSL certificate for {subdomain}.")

            # Reload Nginx
            reload_nginx()

            print(Fore.GREEN + f"Nginx configuration and SSL setup for {subdomain} complete!")
            logger.info(f"Nginx configuration and SSL setup for {subdomain} complete!")

        elif choice == '2':
            # Edit an existing subdomain
            subdomains = list_subdomains(config)
            if not subdomains:
                print(Fore.YELLOW + "No subdomains available to edit.")
                continue
            print("\nSelect the subdomain to edit:")
            for idx, sub in enumerate(subdomains, 1):
                print(f"{idx}) {sub}")
            selection = input("Enter the number of the subdomain you want to edit (or 'q' to go back): ").strip()
            if selection.lower() == 'q':
                print(Fore.YELLOW + "Edit cancelled.")
                continue
            try:
                idx = int(selection) - 1
                if idx < 0 or idx >= len(subdomains):
                    raise ValueError
                subdomain = subdomains[idx]
                details = get_subdomain_details(config, idx)
                if not details:
                    print(Fore.RED + "Invalid selection. Please try again.")
                    continue
                current_ip, current_port, custom_options = details
                print(f"\nEditing subdomain: {subdomain}")
                new_ip = input(f"Enter the new internal IP address [{current_ip}]: ").strip() or current_ip
                new_port = input(f"Enter the new port [{current_port}]: ").strip() or current_port

                # Update custom options
                update_custom = input("Do you want to update custom Nginx options? (y/n): ").strip().lower()
                if update_custom == 'y':
                    custom_options = []
                    add_custom = input("Enter custom Nginx directive (leave blank to stop): ").strip()
                    while add_custom:
                        custom_options.append(add_custom)
                        add_custom = input("Enter another custom Nginx directive (leave blank to stop): ").strip()

                # Update config.yaml
                config['subdomains'][subdomain] = {
                    'target_ip': new_ip,
                    'target_port': new_port,
                    'custom_options': custom_options
                }
                with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'w') as f:
                    import yaml
                    yaml.dump(config, f)

                # Recreate Nginx config
                create_nginx_config(subdomain, new_ip, new_port, custom_options, logger)

                # Obtain SSL certificate
                success = obtain_certificate(subdomain)
                if success:
                    logger.info(f"SSL certificate obtained for {subdomain}.")
                    print(Fore.GREEN + f"SSL certificate obtained for {subdomain}.")
                else:
                    logger.error(f"Failed to obtain SSL certificate for {subdomain}.")
                    print(Fore.RED + f"Failed to obtain SSL certificate for {subdomain}.")

                # Reload Nginx
                reload_nginx()

                print(Fore.GREEN + f"Nginx configuration and SSL setup for {subdomain} updated!")
                logger.info(f"Nginx configuration and SSL setup for {subdomain} updated!")

            except (ValueError, IndexError):
                print(Fore.RED + "Invalid selection. Please try again.")

        elif choice == '3':
            # Update existing domains
            print(Fore.YELLOW + "Updating SSL certificates for all existing domains...")
            subdomains = list_subdomains(config)
            if not subdomains:
                print(Fore.YELLOW + "No subdomains available to update.")
                continue
            for sub in subdomains:
                print(f"Updating SSL certificate for {sub}...")
                success = obtain_certificate(sub)
                if success:
                    logger.info(f"SSL certificate updated for {sub}.")
                    print(Fore.GREEN + f"SSL certificate updated for {sub}.")
                else:
                    logger.error(f"Failed to update SSL certificate for {sub}.")
                    print(Fore.RED + f"Failed to update SSL certificate for {sub}.")
            reload_nginx()
            print(Fore.GREEN + "All SSL certificates updated.")
            logger.info("All SSL certificates updated.")

        elif choice == '4':
            # Delete a subdomain
            subdomains = list_subdomains(config)
            if not subdomains:
                print(Fore.YELLOW + "No subdomains available to delete.")
                continue
            print("\nSelect the subdomain to delete:")
            for idx, sub in enumerate(subdomains, 1):
                print(f"{idx}) {sub}")
            selection = input("Enter the number of the subdomain you want to delete (or 'q' to go back): ").strip()
            if selection.lower() == 'q':
                print(Fore.YELLOW + "Deletion cancelled.")
                continue
            try:
                idx = int(selection) - 1
                if idx < 0 or idx >= len(subdomains):
                    raise ValueError
                subdomain = subdomains[idx]
                confirmation = input(
                    f"Are you sure you want to delete the subdomain {subdomain}? This action cannot be undone. (yes/no): ").strip().lower()
                if confirmation != 'yes':
                    print(Fore.YELLOW + "Deletion cancelled.")
                    continue
                # Remove from config.yaml
                del config['subdomains'][subdomain]
                with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'w') as f:
                    import yaml
                    yaml.dump(config, f)
                # Delete Nginx config
                delete_nginx_config(subdomain, logger)
                # Delete SSL certificates
                delete_ssl_certificate(subdomain, logger)
                # Reload Nginx
                reload_nginx()
                print(Fore.GREEN + f"Subdomain {subdomain} deleted successfully.")
                logger.info(f"Subdomain {subdomain} deleted successfully.")
            except (ValueError, IndexError):
                print(Fore.RED + "Invalid selection. Please try again.")

        elif choice == '5':
            # Settings Menu
            while True:
                print("\nSettings Menu:")
                print("1) View logs")
                print("2) View Changelog")
                print("3) Configure settings")
                print("4) Check for updates")
                print("5) Fix Nginx Configuration and SSL Certificates")
                print("6) Reset All Configurations")
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

def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_startup(version):
    """Display the startup banner."""
    banner = f"""
    =========================================
        NGINX Domain Manager - Version {version}
    =========================================
    """
    print(Fore.CYAN + banner)
