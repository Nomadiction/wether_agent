# Маршрутизация + память через LangChain RedisChatMessageHistory

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from .base import BaseAgent
from src.tools.weather_tool import get_weather
from src.utils.env import get_redis_url

class WeatherAgentLC(BaseAgent):
    # Агент погоды: инструмент get_weather + Redis-память диалога

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.redis_url = get_redis_url()

        if self.redis_url:
            chat_history = RedisChatMessageHistory(session_id=session_id, url=self.redis_url)
        else:
            chat_history = ChatMessageHistory()
        self.chat_history = chat_history

    def _extract_city(self, text: str) -> str:
        if not text.strip():
            return ""
        low = text.lower()
        if "погод" in low or "weather" in low:
            parts = text.replace("?", " ").replace(".", " ").split()
            city = ""
            for i, w in enumerate(parts):
                wl = w.lower()
                if wl in ("в", "in") and i + 1 < len(parts):
                    city = parts[i + 1].strip()
                    break
            # Не пытаемся угадывать по последнему слову
            return city
        if len(text.split()) == 1:
            return text.strip()
        return ""

    def ask(self, text: str) -> str:
        # Сохраняем вход в память
        self.chat_history.add_user_message(text)

        if not text.strip():
            reply = "Enter a request, for example: Weather in Berlin"
            self.chat_history.add_ai_message(reply)
            return reply

        city = self._extract_city(text)
        if city:
            reply = get_weather(city)
            self.chat_history.add_ai_message(reply)
            return reply

        reply = "Format: 'Weather in Berlin' or just 'Berlin'."
        self.chat_history.add_ai_message(reply)
        return reply
