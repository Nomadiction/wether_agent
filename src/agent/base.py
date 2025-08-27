from abc import ABC, abstractmethod

class BaseAgent(ABC):
    # Базовый интерфейс агента

    @abstractmethod
    def ask(self, text: str) -> str:
        # Точка входа, возвращает ответ на текстовый запрос
        raise NotImplementedError
