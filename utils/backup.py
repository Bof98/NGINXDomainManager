import logging
import os
import subprocess
import sys
from datetime import datetime

from colorama import Fore


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
