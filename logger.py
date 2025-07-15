from loguru import logger
import sys

# Remove default handler (so you control formatting)
logger.remove()

# Add console handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>"
)

# Optionally, add file handler
logger.add(
    "logs/app.log",
    level="DEBUG",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,  # safe for multi-process
    backtrace=True,
    diagnose=True
)
