import logging
import os
import subprocess
import sys

from colorama import Fore
from domain_manager.utils.backup import backup_config


# Obtain SSL Certificate
def obtain_certificate(subdomain):
    try:
        subprocess.run([
            'certbot', '--nginx', '-d', subdomain,
            '--redirect', '--agree-tos', '--no-eff-email', '--non-interactive'
        ], check=True)
        print(Fore.GREEN + f"Obtained SSL certificate for {subdomain}")
        logging.info(f"Obtained SSL certificate for {subdomain}")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Failed to obtain SSL certificate for {subdomain}: {e}")
        logging.error(f"Failed to obtain SSL certificate for {subdomain}: {e}")
        sys.exit(1)


# Reload Nginx
def reload_nginx():
    try:
        print("Testing Nginx configuration...")
        subprocess.run(['nginx', '-t'], check=True)
        print("Nginx configuration test successful. Reloading Nginx...")
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        print(Fore.GREEN + "Nginx reloaded successfully.")
        logging.info("Nginx reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Nginx reload failed: {e}")
        logging.error(f"Nginx reload failed: {e}")
        sys.exit(1)
        

def validate_nginx_config():
    try:
        subprocess.run(['nginx', '-t'], check=True)
        print(Fore.GREEN + "Nginx configuration is valid.")
        return True
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Nginx configuration test failed: {e}")
        logging.error(f"Nginx configuration test failed: {e}")
        return False


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
