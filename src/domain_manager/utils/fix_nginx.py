# domain_manager/utils/fix_nginx.py

import logging
import os
import subprocess
from colorama import Fore, Style

from domain_manager.utils.domain import list_subdomains, obtain_certificate, reload_nginx

def backup_nginx_config(config_path, logger):
    """
    Create a backup of the Nginx configuration file.

    Args:
        config_path (str): Path to the Nginx configuration file.
        logger (logging.Logger): Logger instance.
    """
    backup_path = f"{config_path}.backup"
    try:
        subprocess.check_call(['cp', config_path, backup_path])
        logger.info(f"Backup created for {config_path} at {backup_path}.")
        print(Fore.GREEN + f"Backup created for {config_path}.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create backup for {config_path}: {e}")
        print(Fore.RED + f"Failed to create backup for {config_path}: {e}")

def fix_nginx_configuration(config, logger):
    """
    Fix Nginx configuration by removing redundant listen directives and obtaining missing SSL certificates.

    Args:
        config (dict): Configuration dictionary.
        logger (logging.Logger): Logger instance.
    """
    logger.info("Starting Nginx configuration fix process.")
    print(Fore.YELLOW + "Starting Nginx configuration fix process...")

    # Path to Nginx sites-enabled directory
    sites_enabled_dir = "/etc/nginx/sites-enabled/"

    if not os.path.isdir(sites_enabled_dir):
        logger.error(f"Sites-enabled directory not found at {sites_enabled_dir}.")
        print(Fore.RED + f"Sites-enabled directory not found at {sites_enabled_dir}.")
        return

    # Iterate through all configuration files in sites-enabled
    for config_file in os.listdir(sites_enabled_dir):
        config_path = os.path.join(sites_enabled_dir, config_file)
        if not os.path.isfile(config_path):
            continue

        subdomain = config_file.split('.')[0]  # Assumes config file is named as subdomain.conf or similar
        logger.info(f"Processing configuration for {subdomain}.")

        # Backup the configuration file before making changes
        backup_nginx_config(config_path, logger)

        try:
            with open(config_path, 'r') as file:
                lines = file.readlines()

            new_lines = []
            listen_directives = 0
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("listen 443 ssl;") or stripped_line.startswith("listen [::]:443 ssl;"):
                    listen_directives += 1
                    if listen_directives > 1:
                        # Skip redundant listen directives
                        logger.info(f"Removing redundant listen directive in {config_path}.")
                        continue
                new_lines.append(line)

            with open(config_path, 'w') as file:
                file.writelines(new_lines)

            logger.info(f"Redundant listen directives removed from {config_path}.")
            print(Fore.GREEN + f"Redundant listen directives removed from {subdomain} configuration.")

        except Exception as e:
            logger.error(f"Failed to fix Nginx configuration for {subdomain}: {e}")
            print(Fore.RED + f"Failed to fix Nginx configuration for {subdomain}: {e}")
            continue

    # After fixing configurations, test Nginx configuration
    try:
        subprocess.check_call(['nginx', '-t'])
        logger.info("Nginx configuration test passed.")
        print(Fore.GREEN + "Nginx configuration test passed.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Nginx configuration test failed: {e}")
        print(Fore.RED + "Nginx configuration test failed. Please check the log for details.")
        return

    # Reload Nginx to apply changes
    try:
        subprocess.check_call(['systemctl', 'reload', 'nginx'])
        logger.info("Nginx reloaded successfully.")
        print(Fore.GREEN + "Nginx reloaded successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload Nginx: {e}")
        print(Fore.RED + "Failed to reload Nginx. Please check the log for details.")
        return

    # Handle missing SSL certificates
    subdomains = list_subdomains(config)
    if not subdomains:
        logger.info("No subdomains found to handle SSL certificates.")
        print(Fore.YELLOW + "No subdomains found to handle SSL certificates.")
        return

    for sub in subdomains:
        cert_path = f"/etc/letsencrypt/live/{sub}/fullchain.pem"
        key_path = f"/etc/letsencrypt/live/{sub}/privkey.pem"
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            logger.warning(f"Missing SSL certificates for {sub}. Attempting to obtain certificates.")
            print(Fore.YELLOW + f"Missing SSL certificates for {sub}. Attempting to obtain certificates...")
            success = obtain_certificate(sub)
            if success:
                logger.info(f"SSL certificate obtained for {sub}.")
                print(Fore.GREEN + f"SSL certificate obtained for {sub}.")
            else:
                logger.error(f"Failed to obtain SSL certificate for {sub}.")
                print(Fore.RED + f"Failed to obtain SSL certificate for {sub}.")
        else:
            logger.info(f"SSL certificates already exist for {sub}.")
            print(Fore.GREEN + f"SSL certificates already exist for {sub}.")

    # Final reload to apply any new certificates
    try:
        subprocess.check_call(['systemctl', 'reload', 'nginx'])
        logger.info("Nginx reloaded successfully after SSL certificate updates.")
        print(Fore.GREEN + "Nginx reloaded successfully after SSL certificate updates.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload Nginx after SSL certificate updates: {e}")
        print(Fore.RED + "Failed to reload Nginx after SSL certificate updates. Please check the log for details.")
