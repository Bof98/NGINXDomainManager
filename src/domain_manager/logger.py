# logger.py

import logging
import os
from logging.handlers import RotatingFileHandler
import requests
from colorama import Fore, Style, init


def setup_logging(log_file):
    """
    Setup logging with both console and rotating file handlers.

    Args:
        log_file (str): Path to the log file.
    
    Returns:
        logger (logging.Logger): Configured logger instance.
    """
    logger = logging.getLogger('NGINXDomainManager')
    logger.setLevel(logging.DEBUG)

    # Rotating File Handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Define color mapping for different log levels
    LOG_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    class ColorFormatter(logging.Formatter):
        def format(self, record):
            log_color = LOG_COLORS.get(record.levelno, Fore.WHITE)
            formatted_message = super().format(record)
            return f"{log_color}{formatted_message}{Style.RESET_ALL}"

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_formatter = ColorFormatter('%(levelname)s - %(message)s')

    # Add formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def show_logs(config, logger):
    """
    Display the contents of the log file.

    Args:
        config (dict): Configuration dictionary containing log file path.
        logger (logging.Logger): Logger instance.
    """
    log_file = config.get('log_file', 'nginx_domain_manager.log')
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                print(Fore.WHITE + f.read())
            logger.info(f"Displayed logs from {log_file}")
        except Exception as e:
            error_message = f"Failed to read log file {log_file}: {e}"
            print(Fore.RED + f"Failed to read log file: {e}")
            logger.error(error_message)
    else:
        error_message = f"Log file not found at {log_file}"
        print(Fore.RED + error_message)
        logger.error(error_message)


def show_changelog(logger):
    """
    Fetch and display the latest changelog from GitHub releases.

    Args:
        logger (logging.Logger): Logger instance.
    """
    logger.info("Fetching latest changelog from GitHub...")
    print(Fore.YELLOW + "Fetching latest changelog from GitHub...")
    try:
        # GitHub API endpoint for the latest release
        REPO_API_URL = "https://api.github.com/repos/Bof98/NGINXDomainManager/releases/latest"
        response = requests.get(REPO_API_URL, timeout=10)
        response.raise_for_status()
        release_data = response.json()

        latest_version = release_data.get('tag_name', 'Unknown')
        changelog = release_data.get('body', 'No changelog provided.')

        if latest_version != 'Unknown':
            print(Fore.CYAN + f"Latest Version: {latest_version}\n")
            print(Fore.GREEN + "Changelog:\n" + Fore.WHITE + changelog + "\n")
            logger.info(f"Displayed changelog for version {latest_version}")
        else:
            print(Fore.RED + "Could not retrieve the latest version from GitHub.\n")
            logger.error("Could not retrieve the latest version from GitHub.")
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch changelog from GitHub: {e}"
        print(Fore.RED + error_message)
        logger.error(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred while fetching changelog: {e}"
        print(Fore.RED + error_message)
        logger.error(error_message)
