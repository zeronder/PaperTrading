import logging
import os
import sys

from logging.handlers import TimedRotatingFileHandler


# ============================================================
# Configuration
# ============================================================

LOG_DIR = ".logs"

LOG_FILE = os.path.join(LOG_DIR, "application.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")

# Keep 30 days of old logs
BACKUP_COUNT = 30

# Minimum level shown in terminal
CONSOLE_LEVEL = logging.DEBUG

# Minimum level written to application.log
FILE_LEVEL = logging.DEBUG

# Minimum level written to error.log
ERROR_FILE_LEVEL = logging.ERROR


# ============================================================
# ANSI Colors
# ============================================================

class Colors:

    RESET = "\033[0m"

    DEBUG = "\033[36m"       # Cyan
    INFO = "\033[37m"        # White
    WARNING = "\033[33m"     # Yellow
    ERROR = "\033[31m"       # Red
    CRITICAL = "\033[35m"    # Magenta


# ============================================================
# Colored Formatter
# ============================================================

class ColoredFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: Colors.DEBUG,
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.CRITICAL,
    }

    def format(self, record):

        message = super().format(record)

        color = self.COLORS.get(record.levelno, Colors.RESET)

        return f"{color}{message}{Colors.RESET}"


# ============================================================
# Logger Setup
# ============================================================

_configured = False


def setup_logging():
    """
    Configure the global PaperTrading logging system.

    This function should normally be called once from main.py.
    """

    global _configured

    if _configured:
        return

    # --------------------------------------------------------
    # Create log directory
    # --------------------------------------------------------

    os.makedirs(LOG_DIR, exist_ok=True)

    # --------------------------------------------------------
    # Root logger
    # --------------------------------------------------------

    root_logger = logging.getLogger()

    root_logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if setup_logging()
    # is accidentally called more than once.
    root_logger.handlers.clear()

    # --------------------------------------------------------
    # Format
    # --------------------------------------------------------

    log_format = (
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(funcName)s:%(lineno)d | "
        "%(message)s"
    )

    date_format = "%Y-%m-%d %H:%M:%S"

    # --------------------------------------------------------
    # Console Handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setLevel(CONSOLE_LEVEL)

    console_formatter = ColoredFormatter(
        log_format,
        datefmt=date_format
    )

    console_handler.setFormatter(console_formatter)

    # --------------------------------------------------------
    # Application File Handler
    #
    # New file every day.
    #
    # application.log
    # application.log.2026-08-10
    # application.log.2026-08-11
    # --------------------------------------------------------

    file_handler = TimedRotatingFileHandler(
        filename=LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
        delay=True,
    )

    file_handler.setLevel(FILE_LEVEL)

    file_formatter = logging.Formatter(
        log_format,
        datefmt=date_format
    )

    file_handler.setFormatter(file_formatter)

    # --------------------------------------------------------
    # Error File Handler
    #
    # Only ERROR and CRITICAL messages.
    # --------------------------------------------------------

    error_handler = TimedRotatingFileHandler(
        filename=ERROR_LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
        delay=True,
    )

    error_handler.setLevel(ERROR_FILE_LEVEL)

    error_formatter = logging.Formatter(
        log_format,
        datefmt=date_format
    )

    error_handler.setFormatter(error_formatter)

    # --------------------------------------------------------
    # Add handlers
    # --------------------------------------------------------

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    _configured = True


# ============================================================
# Get Logger
# ============================================================

def get_logger(name=None):
    """
    Return a logger for a module.

    Example:

        logger = get_logger(__name__)
    """

    if not _configured:
        setup_logging()

    return logging.getLogger(name)