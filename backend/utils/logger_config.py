import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Base configuration
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),  # Console
            RotatingFileHandler(
                "logs/app.log", 
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5
            )
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    
    logger = logging.getLogger("ChatWithRepo")
    logger.info("Logging system initialized")
    return logger
