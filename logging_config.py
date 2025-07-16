from loguru import logger
from datetime import datetime


def setup_loguru():
    """
        Configures Loguru logger to output logs to both the console and a file.
        Log file name includes current date and time.
        Console output is colorized. File output supports rotation and UTF-8 encoding.
    """
    logger.remove()

    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    logfile = f"revcontent_{now}.log"

    logger.add(
        logfile,
        level="INFO",
        encoding="utf-8",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    logger.info(f"Loguru logging started. Log file: {logfile}")
