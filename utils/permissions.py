import os
import sys

from colorama import Fore


# Cross-platform admin check
def is_admin():
    if os.name == 'nt':
        # Windows
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        # Unix/Linux/Mac
        return os.geteuid() == 0


# Ensure the script is run with appropriate permissions
def check_permissions():
    if not is_admin():
        if os.name == 'nt':
            print(Fore.RED + "Please run this script as an administrator.")
        else:
            print(Fore.RED + "Please run this script as root or with sudo.")
        sys.exit(1)
