import logging
import os
import subprocess
import sys
import requests
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(
    filename='updater.log',
    level=logging.DEBUG,  # Set to DEBUG to capture detailed information
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# GitHub repository details
REPO_URL = "https://github.com/Bof98/NGINXDomainManager.git"
LOCAL_REPO_DIR = os.path.expanduser("~/NGINXDomainManager")


def clear_terminal():
    """Clear the terminal screen."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')


def get_latest_version_from_github():
    """Fetch the latest version tag from the GitHub repository."""
    try:
        url = "https://api.github.com/repos/Bof98/NGINXDomainManager/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        latest_version = response.json()['tag_name']
        logging.debug(f"Latest version on GitHub: {latest_version}")
        return latest_version
    except Exception as e:
        logging.error(f"Failed to fetch the latest version from GitHub: {e}")
        return None

def get_latest_release_details():
    """Fetch the latest release details from GitHub."""
    import requests
    try:
        url = "https://api.github.com/repos/Bof98/NGINXDomainManager/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        release_data = response.json()
        latest_version = release_data.get('tag_name', 'Unknown')
        changelog = release_data.get('body', 'No changelog provided.')
        return latest_version, changelog
    except Exception as e:
        logging.error(f"Failed to fetch release details from GitHub: {e}")
        return "Unknown", "Could not fetch changelog."


def get_current_version():
    """Read the current version from the repository (e.g., version file)."""
    try:
        version_file = os.path.join(LOCAL_REPO_DIR, 'VERSION')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                current_version = f.read().strip()
                logging.debug(f"Current installed version: {current_version}")
                return current_version
        else:
            logging.warning("VERSION file not found, assuming version is unknown.")
            return "0.0.0"
    except Exception as e:
        logging.error(f"Failed to read the current version: {e}")
        return "0.0.0"


def update_from_github():
    """Clone or pull the latest code from GitHub."""
    try:
        if not os.path.exists(LOCAL_REPO_DIR):
            logging.info(f"Cloning repository from {REPO_URL}...")
            subprocess.check_call(['git', 'clone', REPO_URL, LOCAL_REPO_DIR])
        else:
            logging.info(f"Pulling latest changes into {LOCAL_REPO_DIR}...")
            subprocess.check_call(['git', '-C', LOCAL_REPO_DIR, 'pull'])
        logging.info("Repository updated successfully.")
        print(Fore.GREEN + "Repository updated successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to update the repository: {e}")
        print(Fore.RED + "Failed to update the repository.")
        sys.exit(1)


def restart_application():
    """Restart the application."""
    logging.info("Restarting application...")
    print(Fore.YELLOW + "Restarting application...")
    clear_terminal()
    os.execv(sys.executable, [sys.executable] + sys.argv)


def check_for_updates():
    """Check for updates and display changes."""
    print(Fore.YELLOW + "Checking for updates...")
    logging.info("Checking for updates...")
    try:
        latest_version, changelog = get_latest_release_details()
        current_version = get_current_version()
        if latest_version != "Unknown":
            logging.info(f"Latest version: {latest_version}, Current version: {current_version}")
            if latest_version > current_version:
                print(Fore.YELLOW + f"A new version ({latest_version}) is available.")
                print(Fore.CYAN + f"Changelog:\n{changelog}\n")
                logging.info(f"A new version ({latest_version}) is available.")
                choice = input("Do you want to update now? (y/n): ").strip().lower()
                if choice == 'y':
                    update_from_github()
                    updated_version = get_current_version()
                    if updated_version == latest_version:
                        logging.info(f"Update successful: now running version {updated_version}.")
                        print(Fore.GREEN + f"Update successful: now running version {updated_version}.")
                        restart_application()
                    else:
                        logging.error("Update failed: version mismatch after update.")
                        print(Fore.RED + "Update failed: version mismatch. Please try again.")
                        sys.exit(1)
                else:
                    print(Fore.GREEN + "Update canceled.")
                    logging.info("Update canceled by the user.")
            else:
                print(Fore.GREEN + "You are using the latest version.")
                logging.info("You are using the latest version.")
        else:
            print(Fore.RED + "Could not retrieve the latest version from GitHub.")
            logging.error("Could not retrieve the latest version from GitHub.")
    except Exception as e:
        logging.error(f"Failed to check for updates: {e}")
        print(Fore.RED + "Could not check for updates.")


if __name__ == "__main__":
    check_for_updates()
