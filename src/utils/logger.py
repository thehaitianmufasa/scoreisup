import logging
import logging.config
from src.utils.config import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    """
    return logging.getLogger(name)

def log_error(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log an error with context information
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" Context: {context}"
    logger.error(error_msg, exc_info=True)

def log_info(logger: logging.Logger, message: str, context: dict = None):
    """
    Log an info message with context information
    """
    if context:
        message += f" Context: {context}"
    logger.info(message)

def log_warning(logger: logging.Logger, message: str, context: dict = None):
    """
    Log a warning message with context information
    """
    if context:
        message += f" Context: {context}"
    logger.warning(message)

def log_debug(logger: logging.Logger, message: str, context: dict = None):
    """
    Log a debug message with context information
    """
    if context:
        message += f" Context: {context}"
    logger.debug(message) 