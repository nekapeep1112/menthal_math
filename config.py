import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация для Telegram бота ментальной арифметики"""
    
    # Основные настройки бота
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///mental_math_bot.db")
    
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Настройки обучения
    MAX_LEVEL = 10
    PROBLEMS_PER_LEVEL = 5
    
    

    DEFAULT_TIME_PER_PROBLEM = 30  # секунд
    DEFAULT_PROBLEMS_PER_SESSION = 5  # количество задач
    MIN_TIME_PER_PROBLEM = 10  # минимум секунд
    MAX_TIME_PER_PROBLEM = 120  # максимум секунд
    MIN_PROBLEMS_PER_SESSION = 3  # минимум задач
    MAX_PROBLEMS_PER_SESSION = 20  # максимум задач
    
    @classmethod
    def validate(cls):
        """Проверка корректности конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в переменных окружения!")
        if not cls.ADMIN_ID:
            raise ValueError("ADMIN_ID не установлен в переменных окружения!")
        return True 