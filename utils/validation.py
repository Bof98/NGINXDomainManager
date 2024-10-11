# Validate Subdomain
import logging

from colorama import Fore


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
