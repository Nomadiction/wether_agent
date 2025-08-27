import logging
from datetime import datetime
from pathlib import Path
from .env import get_log_level, get_service_name

def setup_logger(name: str | None = None) -> logging.Logger:
    # В файл дня + в консоль
    service = name or get_service_name()
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(service)
    logger.setLevel(get_log_level())
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_dir / f"{service}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler.setLevel(get_log_level())
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(get_log_level())
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
