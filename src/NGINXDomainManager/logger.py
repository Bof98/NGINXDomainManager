import logging
import os
import subprocess

from colorama import Fore


# Setup Logging
def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)


# Show Logs
def show_logs(config):
    log_file = config['log_file']
    if os.path.exists(log_file):
        try:
            subprocess.run(['less', log_file])
        except Exception as e:
            print(Fore.RED + f"Failed to open log file: {e}")
            logging.error(f"Failed to open log file {log_file}: {e}")
    else:
        print(Fore.RED + f"Log file not found at {log_file}")
        logging.error(f"Log file not found at {log_file}")


# Show Changelog
def show_changelog():
    script_path = os.path.realpath(__file__)
    changelog_started = False
    print("Changelog:")
    try:
        with open(script_path, 'r') as f:
            for line in f:
                if line.strip().startswith("# Changelog:"):
                    changelog_started = True
                    continue
                if changelog_started:
                    if line.strip().startswith("# -"):
                        print(Fore.GREEN + line.strip()[2:])
                    elif line.strip() == "":
                        continue
                    else:
                        break
    except Exception as e:
        print(Fore.RED + f"Failed to read changelog: {e}")
        logging.error(f"Failed to read changelog: {e}")
