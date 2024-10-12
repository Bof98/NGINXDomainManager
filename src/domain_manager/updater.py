import logging
import os
import subprocess
import sys

import requests
from colorama import Fore, init
from packaging import version

try:
    from importlib.metadata import version as get_installed_version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version as get_installed_version, PackageNotFoundError

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(
    filename='updater.log',
    level=logging.DEBUG,  # Set to DEBUG to capture detailed information
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_current_version(package_name):
    try:
        current_version = get_installed_version(package_name)
        logging.debug(f"Current installed version of '{package_name}': {current_version}")
        return current_version
    except PackageNotFoundError:
        logging.error(f"Package '{package_name}' is not installed.")
        print(Fore.RED + f"Package '{package_name}' is not installed.")
        sys.exit(1)


def get_latest_version_from_pypi(package_name):
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_version = data['info']['version']
        logging.debug(f"Latest version on PyPI for '{package_name}': {latest_version}")
        return latest_version
    except Exception as e:
        logging.error(f"Failed to get latest version from PyPI: {e}")
        return None

def update_package(package_name):
    try:
        # Run pip to install the latest version of the package
        logging.info(f"Updating package '{package_name}'...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', package_name]
        )
        logging.info("Package updated successfully.")
        print(Fore.GREEN + "Package updated successfully.")

        # Restart the application
        logging.info("Restarting application...")
        print(Fore.YELLOW + "Restarting application...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to update the package: {e}")
        print(Fore.RED + "Failed to update the package.")

def check_for_updates(current_version, package_name):
    print(Fore.YELLOW + "Checking for updates...")
    logging.info(f"Checking for updates for package '{package_name}'...")
    try:
        latest_version = get_latest_version_from_pypi(package_name)
        if latest_version:
            logging.info(f"Latest available version of '{package_name}': {latest_version}")
            if version.parse(latest_version) > version.parse(current_version):
                print(Fore.YELLOW + f"A new version ({latest_version}) is available.")
                logging.info(f"A new version ({latest_version}) is available.")
                choice = input("Do you want to update now? (y/n): ").strip().lower()
                if choice == 'y':
                    update_package(package_name)
                else:
                    print(Fore.GREEN + "Update canceled.")
                    logging.info("Update canceled by the user.")
            else:
                print(Fore.GREEN + "You are using the latest version.")
                logging.info("You are using the latest version.")
        else:
            print(Fore.RED + "Could not retrieve the latest version from PyPI.")
            logging.error("Could not retrieve the latest version from PyPI.")
    except Exception as e:
        logging.error(f"Failed to check for updates: {e}")
        print(Fore.RED + "Could not check for updates.")


if __name__ == "__main__":
    package_name = 'NGINXDomainManager'  # Replace with your package's name
    current_version = get_current_version(package_name)
    check_for_updates(current_version, package_name)
