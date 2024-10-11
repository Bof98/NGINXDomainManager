import logging
import subprocess
import sys

from colorama import Fore, init

# Initialize colorama
init()

# Setup logging
logging.basicConfig(
    filename='updater.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def update_package(package_name):
    try:
        # Run pip to install the latest version of the package
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name])
        logging.info("Package updated successfully.")
        print(Fore.GREEN + "Package updated successfully.")
        # Optionally, restart the application
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to update the package: {e}")
        print(Fore.RED + "Failed to update the package.")


def check_for_updates(current_version, package_name):
    print(Fore.YELLOW + "Checking for updates...")
    try:
        # Get the latest version from PyPI
        result = subprocess.run([sys.executable, '-m', 'pip', 'search', package_name], capture_output=True, text=True)
        latest_version = None
        for line in result.stdout.splitlines():
            if line.startswith(package_name):
                latest_version = line.split(' ')[1].strip('()')
                break
        if latest_version and latest_version != current_version:
            print(Fore.YELLOW + f"A new version ({latest_version}) is available.")
            choice = input("Do you want to update now? (y/n): ").strip().lower()
            if choice == 'y':
                update_package(package_name)
            else:
                print(Fore.GREEN + "Update canceled.")
        else:
            print(Fore.GREEN + "You are using the latest version.")
    except Exception as e:
        logging.error(f"Failed to check for updates: {e}")
        print(Fore.RED + "Could not check for updates.")