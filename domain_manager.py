#!/usr/bin/env python3
"""
DomainManager.py - A Python-based script to manage Nginx subdomains with SSL certificates.
Version: 1.0.3

Changelog:
- 1.0.3: Added configuration menu and ability to view logs
- 1.0.2: Enhanced startup graphic and renamed script to "NGINX Domain Manager"
- 1.0.1: Embedded Nginx configuration template within the script

Requires: Python 3.6+, PyYAML, colorama
"""

import os
import sys
import subprocess
import yaml
import logging
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Constants
CONFIG_FILE = "config.yaml"


# Load Configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"{Fore.RED}Configuration file '{CONFIG_FILE}' not found.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            print(f"{Fore.RED}Error parsing the configuration file: {e}")
            sys.exit(1)


# Save Configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)


# Setup Logging
def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)


# Display Startup Graphic
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


# Validate Subdomain
def validate_subdomain(subdomain):
    import re
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if not re.match(pattern, subdomain):
        print(Fore.RED + "Invalid subdomain format.")
        logging.error(f"Invalid subdomain format: {subdomain}")
        return False
    return True


# Validate IP Address
def validate_ip(ip):
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        print(Fore.RED + "Invalid IP address format.")
        logging.error(f"Invalid IP address format: {ip}")
        return False


# Validate Port
def validate_port(port):
    if not port.isdigit() or not (1 <= int(port) <= 65535):
        print(Fore.RED + "Invalid port number.")
        logging.error(f"Invalid port number: {port}")
        return False
    return True


# Create Nginx Configuration
def create_nginx_config(config, subdomain, target_ip, target_port):
    config_path = os.path.join(config['sites_available'], subdomain)

    # Backup existing config if exists
    if os.path.isfile(config_path):
        backup_config(config, config_path)

    # Replace placeholders in template
    nginx_config = config['nginx_template'].replace('{{SUBDOMAIN}}', subdomain) \
        .replace('{{TARGET_IP}}', target_ip) \
        .replace('{{TARGET_PORT}}', target_port)

    # Write to config file
    try:
        with open(config_path, 'w') as f:
            f.write(nginx_config)
        logging.info(f"Nginx configuration created for {subdomain}")
    except Exception as e:
        print(Fore.RED + f"Failed to write Nginx configuration: {e}")
        logging.error(f"Failed to write Nginx configuration for {subdomain}: {e}")
        sys.exit(1)

    # Enable the configuration
    enabled_path = os.path.join(config['sites_enabled'], subdomain)
    try:
        subprocess.run(['ln', '-sf', config_path, enabled_path], check=True)
        logging.info(f"Nginx configuration enabled for {subdomain}")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Failed to enable Nginx configuration: {e}")
        logging.error(f"Failed to enable Nginx configuration for {subdomain}: {e}")
        sys.exit(1)


# Backup Configuration
def backup_config(config, config_path):
    backup_dir = config['backup_dir']
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(backup_dir, f"{os.path.basename(config_path)}.{timestamp}.bak")
    try:
        subprocess.run(['cp', config_path, backup_file], check=True)
        logging.info(f"Backup created at {backup_file}")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Failed to create backup: {e}")
        logging.error(f"Failed to create backup for {config_path}: {e}")
        sys.exit(1)


# Obtain SSL Certificate
def obtain_certificate(subdomain):
    try:
        subprocess.run([
            'certbot', '--nginx', '-d', subdomain,
            '--redirect', '--agree-tos', '--no-eff-email', '--non-interactive'
        ], check=True)
        print(Fore.GREEN + f"Obtained SSL certificate for {subdomain}")
        logging.info(f"Obtained SSL certificate for {subdomain}")
    except subprocess.CalledProcessError:
        print(Fore.RED + f"Failed to obtain SSL certificate for {subdomain}")
        logging.error(f"Failed to obtain SSL certificate for {subdomain}")
        sys.exit(1)


# Reload Nginx
def reload_nginx():
    try:
        subprocess.run(['nginx', '-t'], check=True)
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        print(Fore.GREEN + "Nginx reloaded successfully.")
        logging.info("Nginx reloaded successfully.")
    except subprocess.CalledProcessError:
        print(Fore.RED + "Nginx configuration test failed. Please check the configuration.")
        logging.error("Nginx configuration test failed.")
        sys.exit(1)


# List Subdomains
def list_subdomains(config):
    sites_available = config['sites_available']
    subdomains = []
    for entry in os.listdir(sites_available):
        config_path = os.path.join(sites_available, entry)
        if os.path.isfile(config_path):
            subdomains.append(entry)
    if not subdomains:
        print(Fore.YELLOW + "No subdomains found.")
        return []
    print("Available subdomains:")
    for idx, sub in enumerate(subdomains, 1):
        target_ip, target_port = extract_ip_port(config, sub)
        print(f"{idx}) Subdomain: {sub}, IP: {target_ip}, Port: {target_port}")
    return subdomains


# Extract IP and Port from Nginx Config
def extract_ip_port(config, subdomain):
    config_path = os.path.join(config['sites_available'], subdomain)
    target_ip = "Not found"
    target_port = "Not found"
    try:
        with open(config_path, 'r') as f:
            for line in f:
                if 'proxy_pass' in line:
                    # Example: proxy_pass http://192.168.0.215:8080;
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        url = parts[1].replace(';', '')
                        if url.startswith('http://'):
                            url = url.replace('http://', '')
                        ip_port = url.split(':')
                        if len(ip_port) == 2:
                            target_ip, target_port = ip_port
    except Exception as e:
        logging.error(f"Error reading Nginx config for {subdomain}: {e}")
    return target_ip, target_port


# Get Subdomain Details
def get_subdomain_details(config, selection):
    subdomains = list_subdomains(config)
    if not subdomains:
        return None
    try:
        index = int(selection) - 1
        if index < 0 or index >= len(subdomains):
            return None
        sub = subdomains[index]
        target_ip, target_port = extract_ip_port(config, sub)
        return sub, target_ip, target_port
    except (ValueError, IndexError):
        return None


# Delete Subdomain
def delete_subdomain(config, subdomain):
    config_path = os.path.join(config['sites_available'], subdomain)
    enabled_path = os.path.join(config['sites_enabled'], subdomain)

    # Backup before deletion
    backup_config(config, config_path)

    # Remove config files
    try:
        os.remove(config_path)
        if os.path.islink(enabled_path):
            os.remove(enabled_path)
        logging.info(f"Removed Nginx configuration for {subdomain}")
    except Exception as e:
        print(Fore.RED + f"Failed to remove Nginx configuration: {e}")
        logging.error(f"Failed to remove Nginx configuration for {subdomain}: {e}")
        sys.exit(1)

    # Remove SSL certificates
    try:
        certbot_output = subprocess.getoutput(['certbot', 'certificates'])
        if f"Domains: {subdomain}" in certbot_output:
            subprocess.run(['certbot', 'delete', '--cert-name', subdomain, '--non-interactive'], check=True)
            logging.info(f"Deleted SSL certificate for {subdomain}")
            print(Fore.GREEN + f"Deleted SSL certificate for {subdomain}")
        else:
            print(Fore.YELLOW + f"No SSL certificate found for {subdomain}.")
            logging.info(f"No SSL certificate found for {subdomain}.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Failed to delete SSL certificate for {subdomain}: {e}")
        logging.error(f"Failed to delete SSL certificate for {subdomain}: {e}")

    # Reload Nginx
    reload_nginx()
    print(Fore.GREEN + f"Subdomain {subdomain} has been deleted.")
    logging.info(f"Subdomain {subdomain} has been deleted.")


# Show Logs
def show_logs(config):
    log_file = config['log_file']
    if os.path.exists(log_file):
        try:
            subprocess.run(['less', log_file])
        except Exception as e:
            print(Fore.RED + f"Failed to open log file: {e}")
            logging.error(f"Failed to open log file {log_file}: {e}")
    else:
        print(Fore.RED + f"Log file not found at {log_file}")
        logging.error(f"Log file not found at {log_file}")


# Show Changelog
def show_changelog():
    script_path = os.path.realpath(__file__)
    changelog_started = False
    print("Changelog:")
    try:
        with open(script_path, 'r') as f:
            for line in f:
                if line.strip().startswith("# Changelog:"):
                    changelog_started = True
                    continue
                if changelog_started:
                    if line.strip().startswith("# -"):
                        print(Fore.GREEN + line.strip()[2:])
                    elif line.strip() == "":
                        continue
                    else:
                        break
    except Exception as e:
        print(Fore.RED + f"Failed to read changelog: {e}")
        logging.error(f"Failed to read changelog: {e}")


# Configure Settings
def configure_settings(config):
    while True:
        print("\nCurrent Settings:")
        print("1) Nginx Configuration Directory:", config['nginx_conf_dir'])
        print("2) Nginx Sites Available Directory:", config['sites_available'])
        print("3) Nginx Sites Enabled Directory:", config['sites_enabled'])
        print("4) Backup Directory:", config['backup_dir'])
        print("5) Log File:", config['log_file'])
        print("6) Nginx Configuration Template")
        print("7) Back to Main Menu")

        choice = input("Select the number of the setting you want to change: ").strip()

        if choice == '1':
            new_value = input(f"Enter new Nginx Configuration Directory [{config['nginx_conf_dir']}]: ").strip()
            if new_value:
                config['nginx_conf_dir'] = new_value
                config['sites_available'] = os.path.join(new_value, 'sites-available')
                config['sites_enabled'] = os.path.join(new_value, 'sites-enabled')
                print(Fore.GREEN + f"Nginx Configuration Directory set to {new_value}")
                logging.info(f"Nginx Configuration Directory updated to {new_value}")
        elif choice == '2':
            new_value = input(f"Enter new Nginx Sites Available Directory [{config['sites_available']}]: ").strip()
            if new_value:
                config['sites_available'] = new_value
                print(Fore.GREEN + f"Nginx Sites Available Directory set to {new_value}")
                logging.info(f"Nginx Sites Available Directory updated to {new_value}")
        elif choice == '3':
            new_value = input(f"Enter new Nginx Sites Enabled Directory [{config['sites_enabled']}]: ").strip()
            if new_value:
                config['sites_enabled'] = new_value
                print(Fore.GREEN + f"Nginx Sites Enabled Directory set to {new_value}")
                logging.info(f"Nginx Sites Enabled Directory updated to {new_value}")
        elif choice == '4':
            new_value = input(f"Enter new Backup Directory [{config['backup_dir']}]: ").strip()
            if new_value:
                config['backup_dir'] = new_value
                print(Fore.GREEN + f"Backup Directory set to {new_value}")
                logging.info(f"Backup Directory updated to {new_value}")
        elif choice == '5':
            new_value = input(f"Enter new Log File Location [{config['log_file']}]: ").strip()
            if new_value:
                config['log_file'] = new_value
                setup_logging(new_value)  # Reconfigure logging
                print(Fore.GREEN + f"Log File set to {new_value}")
                logging.info(f"Log File updated to {new_value}")
        elif choice == '6':
            print("\nCurrent Nginx Configuration Template:")
            print(config['nginx_template'])
            print("\nEnter new Nginx Configuration Template (end with an empty line):")
            new_template_lines = []
            while True:
                line = input()
                if line == "":
                    break
                new_template_lines.append(line)
            if new_template_lines:
                config['nginx_template'] = "\n".join(new_template_lines)
                print(Fore.GREEN + "Nginx Configuration Template updated.")
                logging.info("Nginx Configuration Template updated.")
        elif choice == '7':
            break
        else:
            print(Fore.RED + "Invalid selection. Please try again.")
            continue

        # Save the updated configuration
        save_config(config)


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


# Main Function
def main():
    # Ensure the script is run as root
    if os.geteuid() != 0:
        print(Fore.RED + "Please run this script as root or with sudo.")
        sys.exit(1)

    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config['log_file'])

    # Display startup graphic
    display_startup(config.get('version', '1.0.3'))

    # Main menu
    main_menu(config)


if __name__ == "__main__":
    main()
