# updater.py

import logging
import os
import shutil
import subprocess
import sys

import requests
from packaging import version

# Setup logging
logging.basicConfig(
    filename='updater.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_latest_release(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data['tag_name'].lstrip('v')  # Remove 'v' prefix if present
        assets = data['assets']
        download_url = None
        for asset in assets:
            if asset['name'].endswith('.exe'):
                download_url = asset['browser_download_url']
                break
        return latest_version, download_url
    else:
        logging.error(f"Failed to fetch latest release info: {response.status_code}")
        return None, None


def is_newer_version(current_version, latest_version):
    return version.parse(latest_version) > version.parse(current_version)


def download_executable(download_url, destination_path):
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info("Download completed successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to download the executable: {e}")
        return False


def apply_update():
    current_exe = sys.executable
    temp_exe = "temp_update.exe"  # Temporary path for the new executable
    if os.path.exists(temp_exe):
        try:
            # Backup current executable
            backup_path = "backup.exe"
            shutil.copy(current_exe, backup_path)
            logging.info("Backup of current executable created.")

            # Replace the executable
            shutil.move(temp_exe, current_exe)
            logging.info("Application updated successfully.")
            print(Fore.GREEN + "Application updated successfully.")

            # Optionally, restart the application
            subprocess.Popen([current_exe])
            sys.exit(0)
        except Exception as e:
            logging.error(f"Failed to apply update: {e}")
            print(Fore.RED + "Failed to apply update.")


def update_application(latest_version, download_url):
    print(Fore.YELLOW + f"A new version ({latest_version}) is available.")
    choice = input("Do you want to update now? (y/n): ").strip().lower()
    if choice == 'y':
        temp_path = "temp_update.exe"
        success = download_executable(download_url, temp_path)
        if success:
            print(Fore.YELLOW + "Updating the application...")
            logging.info("Updating the application...")
            try:
                # Start the new executable
                subprocess.Popen([temp_path])
                # Exit the current script
                sys.exit(0)
            except Exception as e:
                logging.error(f"Failed to launch the new executable: {e}")
                print(Fore.RED + "Failed to launch the updated application.")
        else:
            print(Fore.RED + "Update failed. Please try again later.")
    else:
        print(Fore.GREEN + "Update canceled.")


def check_for_updates(version):
    repo_owner = "Bof98"  # Replace with your GitHub username
    repo_name = "NGINXDomainManager"  # Replace with your repository name
    latest_version, download_url = get_latest_release(repo_owner, repo_name)
    if latest_version and download_url:
        if is_newer_version(version, latest_version):
            update_application(latest_version, download_url)
        else:
            print(Fore.GREEN + "You are using the latest version.")
    else:
        print(Fore.RED + "Could not check for updates.")
