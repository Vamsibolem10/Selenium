import sys
from loguru import logger
import os

def setup_logger():

    logger.remove()
    
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

    os.makedirs("logs", exist_ok=True)
    logger.add("logs/test_run.log", rotation="10 MB", retention="10 days", compression="zip")
    
    return logger

log = setup_logger()
