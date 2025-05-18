import logging
import sys
import json
import os
from pathlib import Path

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'level': record.levelname,
            'time': self.formatTime(record, self.datefmt),
            'name': record.name,
            'message': record.getMessage(),
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    
    # File handler
    file_handler = logging.FileHandler("logs/ai_tutor.log")
    file_handler.setFormatter(JsonFormatter())
    
    # Configure root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [console_handler, file_handler]

    # Silence overly verbose loggers
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    # Ensure our AI teacher logger is at INFO level
    ai_logger = logging.getLogger("ai_teacher")
    ai_logger.setLevel(logging.INFO)
    
    logging.info("Logging configured - writing to console and logs/ai_tutor.log")

setup_logging() 