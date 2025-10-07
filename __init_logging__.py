import logging

rotating_file_handler = logging.handlers.RotatingFileHandler(
    filename="yapple.log",
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=2,         # Keep up to 2 backup files
    encoding="utf-8"
)
# Set up logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt= "%Y-%m-%d %H:%M:%S",
                    handlers=[rotating_file_handler, logging.StreamHandler()])
logger = logging.getLogger(__name__)
