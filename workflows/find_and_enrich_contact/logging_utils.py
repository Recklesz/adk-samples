"""
Logging utilities for the enrichment pipeline.
Provides functions to set up properly structured logs.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# Constants
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def ensure_log_directories():
    """
    Create log directories if they don't exist.
    
    Structure:
    - logs/
      - pipeline/    # Main enrichment pipeline logs
      - agents/      # Logs for individual agent runs
    """
    # Determine base path
    workflow_dir = Path(__file__).parent
    log_dir = workflow_dir / "logs"
    
    # Create directories
    (log_dir / "pipeline").mkdir(parents=True, exist_ok=True)
    (log_dir / "agents").mkdir(parents=True, exist_ok=True)
    
    return log_dir

def get_pipeline_logger(name: str = "enrichment", console_level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger for the main enrichment pipeline.
    
    Args:
        name: Logger name
        console_level: Logging level for console output
        
    Returns:
        Configured logger
    """
    log_dir = ensure_log_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / "pipeline" / f"{name}_{timestamp}.log"
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Remove existing handlers if present
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configure logger
    logger.setLevel(logging.DEBUG)  # Log everything to file
    
    # File handler - detailed logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(file_handler)
    
    # Console handler - less verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)
    
    logger.info(f"Pipeline logging initialized. Log file: {log_file}")
    return logger

def get_agent_logger(domain: str) -> logging.Logger:
    """
    Get a domain-specific logger for agent interactions.
    
    Args:
        domain: The domain being enriched
        
    Returns:
        Configured logger that logs to a domain-specific file
    """
    log_dir = ensure_log_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_domain = domain.replace(".", "_").replace("/", "_")
    log_file = log_dir / "agents" / f"{sanitized_domain}_{timestamp}.log"
    
    # Create a unique logger for this specific domain run
    # Use a timestamp to ensure uniqueness even for the same domain
    run_id = f"{datetime.now().microsecond:06d}"
    logger_name = f"agent_{sanitized_domain}_{run_id}"
    logger = logging.getLogger(logger_name)
    
    # Reset logger (remove existing handlers and reset settings)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configure logger
    logger.setLevel(logging.DEBUG)
    
    # File handler only - everything goes to the domain-specific file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(file_handler)
    
    # Add minimal console handler for critical errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)  # Only critical errors to console
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)
    
    # Don't propagate to parent loggers to avoid duplicate console output
    logger.propagate = False
    
    # Log the initialization
    logger.info(f"Domain-specific logger initialized for {domain}. Log file: {log_file}")
    
    return logger

# Configure root logger - make sure uncaught logs have a sensible default
def configure_root_logger(console_level: int = logging.WARNING):
    """Configure the root logger with sensible defaults."""
    root_logger = logging.getLogger()
    
    # Remove existing handlers if present
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set reasonable level
    root_logger.setLevel(logging.WARNING)
    
    # Create log directory if it doesn't exist
    log_dir = ensure_log_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / "pipeline" / f"root_logger_{timestamp}.log"
    
    # File handler for root logger
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Capture everything in the file
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(console_handler)

# Initialize default logging on import
configure_root_logger()
