"""
Centralized logging system for Contact Manager Pro.
Outputs structured timestamped logs to console and rotating log file.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from config.settings import AppConfig

_initialized = False

def setup_logger(log_file=None, level=logging.INFO):
    """Configure application-wide logger."""
    global _initialized
    if _initialized:
        return logging.getLogger("ContactManager")
        
    logger = logging.getLogger("ContactManager")
    logger.setLevel(level)
    logger.propagate = False
    
    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Stream Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Rotating File Handler (5 MB max, 5 backups)
    if log_file is None:
        log_file = AppConfig.LOG_FILE
    
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not initialize file logger: {e}")
        
    _initialized = True
    return logger

def get_logger(name=None):
    """Retrieve logger instance."""
    setup_logger()
    if name:
        return logging.getLogger(f"ContactManager.{name}")
    return logging.getLogger("ContactManager")
