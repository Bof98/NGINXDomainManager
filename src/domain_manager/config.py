# domain_manager/config.py

import yaml
import os

def load_config():
    """Load the configuration from config.yaml."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_path):
        # Create a default config if not present
        default_config = {
            'log_file': '/var/log/nginx_domain_manager.log',
            'subdomains': {}
        }
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
        return default_config
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def configure_settings(config):
    """Allow user to configure settings."""
    import logging
    logger = logging.getLogger('NGINXDomainManager')
    
    print("\nConfigure Settings:")
    print("1) Add a new subdomain")
    print("2) Remove a subdomain")
    print("3) Update a subdomain")
    print("4) Go back to Settings Menu")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        subdomain = input("Enter your subdomain (e.g., app.example.com): ").strip()
        target_ip = input("Enter the internal IP address of the target server (e.g., 192.168.0.215): ").strip()
        target_port = input("Enter the port the target service is running on (e.g., 8080): ").strip()
        
        custom_options = []
        add_custom = input("Do you want to add custom Nginx options for this subdomain? (y/n): ").strip().lower()
        while add_custom == 'y':
            option = input("Enter custom Nginx directive (leave blank to stop): ").strip()
            if option:
                custom_options.append(option)
            else:
                break
            add_custom = input("Add another custom option? (y/n): ").strip().lower()
        
        config['subdomains'][subdomain] = {
            'target_ip': target_ip,
            'target_port': target_port,
            'custom_options': custom_options
        }
        with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
            yaml.dump(config, f)
        print(Fore.GREEN + f"Subdomain {subdomain} added successfully.")
        logger.info(f"Subdomain {subdomain} added successfully.")
    
    elif choice == '2':
        subdomains = list_subdomains(config)
        if not subdomains:
            print(Fore.YELLOW + "No subdomains to remove.")
            return
        print("\nSelect the subdomain to remove:")
        for idx, sub in enumerate(subdomains, 1):
            print(f"{idx}) {sub}")
        selection = input("Enter the number of the subdomain to remove (or 'q' to cancel): ").strip()
        if selection.lower() == 'q':
            print(Fore.YELLOW + "Operation cancelled.")
            return
        try:
            idx = int(selection) - 1
            if idx < 0 or idx >= len(subdomains):
                raise ValueError
            subdomain = subdomains[idx]
            del config['subdomains'][subdomain]
            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
                yaml.dump(config, f)
            print(Fore.GREEN + f"Subdomain {subdomain} removed successfully.")
            logger.info(f"Subdomain {subdomain} removed successfully.")
        except (ValueError, IndexError):
            print(Fore.RED + "Invalid selection.")
    
    elif choice == '3':
        subdomains = list_subdomains(config)
        if not subdomains:
            print(Fore.YELLOW + "No subdomains to update.")
            return
        print("\nSelect the subdomain to update:")
        for idx, sub in enumerate(subdomains, 1):
            print(f"{idx}) {sub}")
        selection = input("Enter the number of the subdomain to update (or 'q' to cancel): ").strip()
        if selection.lower() == 'q':
            print(Fore.YELLOW + "Operation cancelled.")
            return
        try:
            idx = int(selection) - 1
            if idx < 0 or idx >= len(subdomains):
                raise ValueError
            subdomain = subdomains[idx]
            print(f"\nUpdating subdomain: {subdomain}")
            target_ip = input(f"Enter the new internal IP address [{config['subdomains'][subdomain]['target_ip']}]: ").strip() or config['subdomains'][subdomain]['target_ip']
            target_port = input(f"Enter the new port [{config['subdomains'][subdomain]['target_port']}]: ").strip() or config['subdomains'][subdomain]['target_port']
            
            custom_options = config['subdomains'][subdomain].get('custom_options', [])
            update_custom = input("Do you want to update custom Nginx options? (y/n): ").strip().lower()
            if update_custom == 'y':
                custom_options = []
                add_custom = input("Enter custom Nginx directive (leave blank to stop): ").strip()
                while add_custom:
                    custom_options.append(add_custom)
                    add_custom = input("Enter another custom Nginx directive (leave blank to stop): ").strip()
            
            config['subdomains'][subdomain] = {
                'target_ip': target_ip,
                'target_port': target_port,
                'custom_options': custom_options
            }
            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as f:
                yaml.dump(config, f)
            print(Fore.GREEN + f"Subdomain {subdomain} updated successfully.")
            logger.info(f"Subdomain {subdomain} updated successfully.")
        except (ValueError, IndexError):
            print(Fore.RED + "Invalid selection.")
    
    elif choice == '4':
        # Go back to Settings Menu
        return
    
    else:
        print(Fore.RED + "Invalid option. Returning to Settings Menu.")
