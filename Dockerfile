FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Ставим системные зависимости по минимуму
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV REDIS_URL=redis://redis:6379/0 \
    LOG_LEVEL=INFO \
    SERVICE_NAME=weather_api

EXPOSE 8000

# Старт 
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
