# Погодный Агент с LangChain

### Установка
```bash
git clone https://github.com/your-username/weather-agent.git
cd weather-agent
pip install -r requirements.txt
```

### Запуск локально
1. Запустите Redis в контейнере:
   ```bash
   docker run -d --name redis -p 6379:6379 redis
   ```
2. Подключитесь к Redis: 
   ```bash
   docker exec -it redis redis-cli ping
   ```
3. Запустите FastAPI сервер:
   ```bash
   uvicorn src.api.main:app --reload
   ```
3. Доступ к эндпоинту: [http://localhost:8000/docs](http://localhost:8000/docs)

## Мониторинг
- Логи сохраняются в директории `/logs`  
- Простая панель мониторинга на CSV + Pandas может использоваться для анализа производительности

