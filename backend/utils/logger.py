"""Logging Configuration with JSON Formatter"""
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from backend.config import settings

def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s %(levelname)s %(name)s %(message)s'
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # File handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    
    # JSON formatter for structured logging
    if settings.LOG_FORMAT == 'json':
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d',
            rename_fields={'levelname': 'severity', 'asctime': 'timestamp'}
        )
    else:
        formatter = logging.Formatter(log_format)
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)