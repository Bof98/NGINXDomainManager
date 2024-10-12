# logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style


def setup_logging(log_file):
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
    log_file = config.get('log_file', 'nginx_domain_manager.log')
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                print(f.read())
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
                        entry = line.strip()[2:].strip()
                        print(Fore.GREEN + entry)
                        logger.info(f"Changelog entry: {entry}")
                    elif line.strip() == "":
                        continue
                    else:
                        break
    except Exception as e:
        error_message = f"Failed to read changelog: {e}"
        print(Fore.RED + error_message)
        logger.error(error_message)
