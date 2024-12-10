import logging
import os
import subprocess
import sys
import requests
from colorama import Fore, init
from packaging import version

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


def get_latest_release_details():
    """Fetch the latest release details from GitHub."""
    try:
        url = "https://api.github.com/repos/Bof98/NGINXDomainManager/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        release_data = response.json()
        latest_version = release_data.get('tag_name', 'Unknown')
        changelog = release_data.get('body', 'No changelog provided.')
        return latest_version, changelog
    except Exception as e:
        logging.error(f"Failed to fetch release details from GitHub: {e}")
        return "Unknown", "Could not fetch changelog."


def get_current_version():
    """Fetch the current version from Git tags."""
    try:
        # Run `git describe --tags --abbrev=0` to get the latest tag without commit hash
        version_str = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=LOCAL_REPO_DIR,
            universal_newlines=True,
        ).strip()
        logging.debug(f"Current installed version: {version_str}")
        return version_str
    except subprocess.CalledProcessError:
        logging.error("Unable to determine current version from Git.")
        return "0.0.0"


def update_from_github():
    """Clone or pull the latest code from GitHub."""
    try:
        if not os.path.exists(LOCAL_REPO_DIR):
            logging.info(f"Cloning repository from {REPO_URL}...")
            subprocess.check_call(['git', 'clone', REPO_URL, LOCAL_REPO_DIR])
        else:
            logging.info(f"Fetching latest tags and pulling changes into {LOCAL_REPO_DIR}...")
            subprocess.check_call(['git', '-C', LOCAL_REPO_DIR, 'fetch', '--tags'])
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
    """Check if there are updates available and update if needed."""
    print(Fore.YELLOW + "Checking for updates...")
    logging.info("Checking for updates...")
    try:
        latest_version, changelog = get_latest_release_details()
        current_version = get_current_version()

        if latest_version == "Unknown":
            print(Fore.RED + "Could not retrieve the latest version from GitHub.")
            logging.error("Could not retrieve the latest version from GitHub.")
            return

        # Compare versions using packaging.version
        if version.parse(latest_version) > version.parse(current_version):
            print(Fore.YELLOW + f"A new version ({latest_version}) is available.")
            print(Fore.CYAN + f"Changelog:\n{changelog}\n")
            logging.info(f"A new version ({latest_version}) is available.")

            choice = input("Do you want to update now? (y/n): ").strip().lower()
            if choice == 'y':
                update_from_github()
                # Fetch the new version after update
                updated_version = get_current_version()
                if version.parse(updated_version) == version.parse(latest_version):
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
    except Exception as e:
        logging.error(f"Failed to check for updates: {e}")
        print(Fore.RED + "Could not check for updates.")


if __name__ == "__main__":
    check_for_updates()
