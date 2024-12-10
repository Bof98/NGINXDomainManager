# domain_manager/utils/reset_configs.py

import logging
import os
import shutil
import subprocess
from colorama import Fore, Style
from datetime import datetime

from domain_manager.utils.domain import list_subdomains, obtain_certificate, reload_nginx

def reset_all_configurations(config, logger):
    """
    Reset all Nginx configurations by backing up existing configs, removing them,
    and recreating based on the current subdomains in the configuration.
    
    Args:
        config (dict): Configuration dictionary.
        logger (logging.Logger): Logger instance.
    """
    logger.info("Initiating reset of all Nginx configurations.")
    print(Fore.YELLOW + "Initiating reset of all Nginx configurations...")

    # Define paths
    sites_enabled_dir = "/etc/nginx/sites-enabled/"
    sites_available_dir = "/etc/nginx/sites-available/"
    backup_dir = f"/etc/nginx/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Step 1: Backup Existing Configurations
    try:
        shutil.copytree(sites_enabled_dir, backup_dir)
        logger.info(f"Backed up existing Nginx configurations to {backup_dir}.")
        print(Fore.GREEN + f"Backed up existing Nginx configurations to {backup_dir}.")
    except Exception as e:
        logger.error(f"Failed to backup Nginx configurations: {e}")
        print(Fore.RED + f"Failed to backup Nginx configurations: {e}")
        return

    # Step 2: Remove Current Configurations
    try:
        for config_file in os.listdir(sites_enabled_dir):
            config_path = os.path.join(sites_enabled_dir, config_file)
            if os.path.isfile(config_path):
                os.remove(config_path)
                logger.info(f"Removed configuration file {config_path}.")
        print(Fore.GREEN + "All existing Nginx configurations have been removed.")
    except Exception as e:
        logger.error(f"Failed to remove Nginx configurations: {e}")
        print(Fore.RED + f"Failed to remove Nginx configurations: {e}")
        return

    # Step 3: Recreate Configurations Based on Current Settings
    subdomains = config.get('subdomains', {})
    if not subdomains:
        print(Fore.YELLOW + "No subdomains found in configuration to recreate.")
        logger.info("No subdomains found in configuration to recreate.")
    else:
        for subdomain, details in subdomains.items():
            target_ip = details.get('target_ip')
            target_port = details.get('target_port')
            custom_options = details.get('custom_options', [])

            # Define configuration content
            config_content = generate_nginx_config(subdomain, target_ip, target_port, custom_options)

            # Write to sites-available
            available_config_path = os.path.join(sites_available_dir, f"{subdomain}.conf")
            try:
                with open(available_config_path, 'w') as f:
                    f.write(config_content)
                logger.info(f"Created Nginx configuration for {subdomain} at {available_config_path}.")
                print(Fore.GREEN + f"Created Nginx configuration for {subdomain}.")
            except Exception as e:
                logger.error(f"Failed to create Nginx configuration for {subdomain}: {e}")
                print(Fore.RED + f"Failed to create Nginx configuration for {subdomain}: {e}")
                continue

            # Create symlink in sites-enabled
            enabled_config_path = os.path.join(sites_enabled_dir, f"{subdomain}.conf")
            try:
                if not os.path.exists(enabled_config_path):
                    os.symlink(available_config_path, enabled_config_path)
                    logger.info(f"Enabled Nginx configuration for {subdomain}.")
                    print(Fore.GREEN + f"Enabled Nginx configuration for {subdomain}.")
            except Exception as e:
                logger.error(f"Failed to enable Nginx configuration for {subdomain}: {e}")
                print(Fore.RED + f"Failed to enable Nginx configuration for {subdomain}: {e}")
                continue

            # Obtain SSL Certificate
            cert_success = obtain_certificate(subdomain)
            if cert_success:
                logger.info(f"Obtained SSL certificate for {subdomain}.")
                print(Fore.GREEN + f"Obtained SSL certificate for {subdomain}.")
            else:
                logger.error(f"Failed to obtain SSL certificate for {subdomain}.")
                print(Fore.RED + f"Failed to obtain SSL certificate for {subdomain}.")

        # Step 4: Test Nginx Configuration
        try:
            subprocess.check_call(['nginx', '-t'])
            logger.info("Nginx configuration test passed.")
            print(Fore.GREEN + "Nginx configuration test passed.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Nginx configuration test failed: {e}")
            print(Fore.RED + "Nginx configuration test failed. Please check the log for details.")
            return

        # Step 5: Reload Nginx
        try:
            subprocess.check_call(['systemctl', 'reload', 'nginx'])
            logger.info("Nginx reloaded successfully.")
            print(Fore.GREEN + "Nginx reloaded successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to reload Nginx: {e}")
            print(Fore.RED + "Failed to reload Nginx. Please check the log for details.")
            return

    # Final Message
    print(Fore.GREEN + "Reset of all Nginx configurations completed successfully.")
    logger.info("Reset of all Nginx configurations completed successfully.")

def generate_nginx_config(subdomain, target_ip, target_port, custom_options):
    """
    Generate Nginx configuration content for a subdomain.

    Args:
        subdomain (str): The subdomain (e.g., app.example.com).
        target_ip (str): Internal IP address of the target server.
        target_port (str): Port on which the target service is running.
        custom_options (list): List of custom Nginx directives.

    Returns:
        str: Nginx configuration content.
    """
    config = f"""
server {{
    listen 80;
    listen [::]:80;
    server_name {subdomain};
    
    # Redirect all HTTP requests to HTTPS
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name {subdomain};
    
    ssl_certificate /etc/letsencrypt/live/{subdomain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{subdomain}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    
    location / {{
        proxy_pass http://{target_ip}:{target_port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        {"".join([f'\n        {option}' for option in custom_options])}
    }}
}}
"""
    return config
