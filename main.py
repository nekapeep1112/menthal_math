import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database.database import db
from handlers import basic_handlers, learning_handlers, media_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mental_math_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

bot = None
dp = None

async def main():
    """Главная функция запуска бота"""
    try:
        # Проверяем конфигурацию
        Config.validate()
        logger.info("Конфигурация валидна")
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return
    
    # Инициализируем базу данных
    try:
        await db.init_db()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return
    
    # Создаем бота и диспетчер
    global bot, dp
    bot = Bot(
        token=Config.BOT_TOKEN,
        parse_mode=ParseMode.HTML
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутеры
    dp.include_router(basic_handlers.router)
    dp.include_router(learning_handlers.router)
    dp.include_router(media_handlers.router)
    
    logger.info("Роутеры зарегистрированы")
    
    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f"Бот запущен: @{bot_info.username}")
    logger.info("Бот ментальной арифметики готов к работе!")
    
    try:
        # Запускаем поллинг
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения")
    finally:
        # Закрываем соединения
        await bot.session.close()
        await db.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 