import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import datetime
from config.config import LOG_DIR, LOG_LEVEL

# Define log file name with timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d")
LOG_FILE = LOG_DIR / f"ehr_app_{timestamp}.log"

# Configure logging
def setup_logger(name, log_file=LOG_FILE, level=LOG_LEVEL):
    """Set up a logger with file and console handlers."""
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create a default logger
default_logger = setup_logger('ehr_app')