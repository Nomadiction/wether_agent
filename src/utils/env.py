import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_url() -> str:
    # Возвращаем URL или пустую строку, чтобы позволить локальный запуск без Redis
    url = os.getenv("REDIS_URL", "").strip()
    return url

def get_log_level(default: str = "INFO") -> str:
    lvl = os.getenv("LOG_LEVEL", default).upper()
    return lvl if lvl in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else default

def get_service_name() -> str:
    return os.getenv("SERVICE_NAME", "weather_api")
