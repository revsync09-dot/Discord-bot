"""
Centralized logging module.
All logs include timestamp, severity, context, and correlation ID support.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import uuid


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def __init__(self):
        super().__init__()
        self.correlation_id: Optional[str] = None
    
    def filter(self, record):
        record.correlation_id = self.correlation_id or "N/A"
        return True


class BotLogger:
    """
    Centralized logger for the bot.
    Provides correlation ID support for tracking related operations.
    """
    
    def __init__(self, name: str, level: str = "INFO", log_format: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        
        # Format
        if log_format is None:
            log_format = "%(asctime)s | %(levelname)-8s | %(name)s | [%(correlation_id)s] | %(message)s"
        
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        
        # Add correlation filter
        self.correlation_filter = CorrelationFilter()
        handler.addFilter(self.correlation_filter)
        
        self.logger.addHandler(handler)
    
    def set_correlation_id(self, correlation_id: Optional[str] = None):
        """Set correlation ID for tracking related operations."""
        self.correlation_filter.correlation_id = correlation_id or str(uuid.uuid4())
    
    def clear_correlation_id(self):
        """Clear correlation ID."""
        self.correlation_filter.correlation_id = None
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info=False, **kwargs):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info=False, **kwargs):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)


# Global logger instances
_loggers: dict[str, BotLogger] = {}


def get_logger(name: str, level: Optional[str] = None, log_format: Optional[str] = None) -> BotLogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name (typically module name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
    
    Returns:
        BotLogger instance
    """
    if name not in _loggers:
        from .config import get_config
        config = get_config()
        
        _loggers[name] = BotLogger(
            name=name,
            level=level or config.log_level,
            log_format=log_format or config.log_format
        )
    
    return _loggers[name]