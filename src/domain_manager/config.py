import logging
import os
import subprocess
import sys

import domain_manager.logger
import yaml
from colorama import Fore

from utils.backup import backup_config

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
                domain_manager.logger.setup_logging(new_value)  # Reconfigure logging
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
