from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from database.database import db
from keyboards.main_keyboard import get_main_menu, get_level_selection, get_photo_materials_keyboard
from utils.formatters import format_welcome_message, format_help_message, format_user_stats, get_random_greeting
from utils.math_generator import math_generator
import logging

router = Router()
logger = logging.getLogger(__name__)

class SettingsStates(StatesGroup):
    waiting_time_input = State()
    waiting_problems_input = State()

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()  # Очищаем состояние
    
    # Создаем или получаем пользователя
    user = await db.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Отправляем случайное приветственное сообщение с картинкой
    welcome_text = get_random_greeting(message.from_user.first_name or "друг")
    
    # Отправляем картинку с приветствием
    from aiogram.types import FSInputFile
    import os
    
    greet_photo = FSInputFile(os.path.join("media", "photos", "greet.png"))
    
    await message.answer_photo(
        photo=greet_photo,
        caption=welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def help_command(message: Message):
    """Обработчик команды помощи"""
    help_text = format_help_message()
    
    await message.answer(
        help_text,
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Моя статистика")
async def stats_command(message: Message):
    """Обработчик команды статистики"""
    stats = await db.get_user_stats(message.from_user.id)
    stats_text = format_user_stats(stats)
    
    await message.answer(
        stats_text,
        parse_mode="HTML"
    )

@router.message(F.text == "🧮 Начать обучение")
async def start_learning(message: Message):
    """Обработчик начала обучения"""
    # Получаем информацию о пользователе
    user = await db.get_or_create_user(telegram_id=message.from_user.id)
    
    # Получаем статистику для определения текущего уровня
    stats = await db.get_user_stats(message.from_user.id)
    current_level = stats.get("level", 1) if stats else 1
    
    # Показываем выбор уровня
    keyboard = get_level_selection(current_level)
    
    await message.answer(
        "📚 <b>Выбери уровень для обучения:</b>\n\n"
        "🟢 Легкий • 🟡 Средний • 🟠 Сложный • 🔴 Эксперт\n\n"
        "<i>Выбери доступный уровень или повтори пройденный!</i>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(F.text == "🏆 Достижения")
async def achievements_command(message: Message):
    """Обработчик команды достижений"""
    # Получаем реальные достижения пользователя
    async with db.async_session() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from database.models import User, UserAchievement, Achievement
        
        user_result = await session.execute(
            select(User).options(
                selectinload(User.achievements).selectinload(UserAchievement.achievement)
            ).where(User.telegram_id == message.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        
        if user and user.achievements:
            achievements_data = []
            for user_achievement in user.achievements:
                achievements_data.append({
                    'name': user_achievement.achievement.name,
                    'description': user_achievement.achievement.description,
                    'icon': user_achievement.achievement.icon,
                    'earned_at': user_achievement.earned_at
                })
            
            from utils.formatters import format_achievements_list
            text = format_achievements_list(achievements_data)
        else:
            text = "🏆 <b>Достижения</b>\n\nУ тебя пока нет достижений.\nРеши несколько задач, чтобы получить первые награды! 💪"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🏅 Рейтинг")
async def leaderboard_command(message: Message):
    """Показать общий рейтинг пользователей"""
    user_id = message.from_user.id
    
    # Получаем рейтинг и позицию пользователя
    leaderboard = await db.get_leaderboard(limit=10)
    user_rank = await db.get_user_rank(user_id)
    
    from utils.formatters import format_leaderboard
    leaderboard_text = format_leaderboard(leaderboard, user_rank)
    
    await message.answer(leaderboard_text, parse_mode="HTML")

@router.message(F.text == "⚙️ Настройки")
async def settings_command(message: Message):
    """Обработчик команды настроек"""
    from keyboards.main_keyboard import get_settings_keyboard
    
    await message.answer(
        "⚙️ <b>Настройки бота</b>\n\n"
        "Здесь ты можешь настроить бота под свои предпочтения:",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.delete()
    
    await callback.message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выбери действие:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "level_locked")
async def level_locked(callback: CallbackQuery):
    """Обработчик заблокированного уровня"""
    await callback.answer(
        "🔒 Этот уровень пока недоступен!\nПройди предыдущие уровни, чтобы его разблокировать.",
        show_alert=True
    )

@router.callback_query(F.data.startswith("level_"))
async def select_level(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора уровня"""
    level_str = callback.data.split("_")[1]
    
    try:
        level = int(level_str)
    except ValueError:
        await callback.answer("❌ Ошибка выбора уровня")
        return
    
    # Получаем описание уровня
    description = math_generator.get_level_description(level)
    difficulty = math_generator.get_difficulty_emoji(level)
    
    from utils.formatters import format_level_info
    level_info = format_level_info(level, description, difficulty)
    
    # Сохраняем выбранный уровень в состояние
    await state.update_data(selected_level=level)
    
    from keyboards.main_keyboard import get_confirmation_keyboard
    
    await callback.message.edit_text(
        level_info + "\n<b>Начать тренировку?</b>",
        reply_markup=get_confirmation_keyboard("start_learning"),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "confirm_start_learning")
async def confirm_start_learning(callback: CallbackQuery, state: FSMContext):
    """Подтверждение начала обучения"""
    data = await state.get_data()
    level = data.get("selected_level", 1)
    
    # Переходим к обучению
    from handlers.learning_handlers import start_learning_session
    await start_learning_session(callback, state, level)

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена действия"""
    await callback.message.delete()
    await state.clear()
    
    await callback.message.answer(
        "❌ <b>Действие отменено</b>\n\nВыбери другое действие:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    await callback.answer("Действие отменено")

# Обработчики настроек
@router.callback_query(F.data == "setting_time")
async def setting_time(callback: CallbackQuery, state: FSMContext):
    """Настройка времени на задачу"""
    user_settings = await db.get_user_settings(callback.from_user.id)
    current_time = user_settings.get("time_per_problem", 30)
    
    from config import Config
    
    await callback.message.edit_text(
        f"⏱️ <b>Время на задачу</b>\n\n"
        f"Текущее время: <b>{current_time} секунд</b>\n\n"
        f"Введите новое время на задачу от {Config.MIN_TIME_PER_PROBLEM} до {Config.MAX_TIME_PER_PROBLEM} секунд:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")
        ]])
    )
    
    await state.set_state(SettingsStates.waiting_time_input)
    await callback.answer()

@router.callback_query(F.data == "setting_problems")
async def setting_problems(callback: CallbackQuery, state: FSMContext):
    """Настройка количества задач"""
    user_settings = await db.get_user_settings(callback.from_user.id)
    current_problems = user_settings.get("problems_per_session", 5)
    
    from config import Config
    
    await callback.message.edit_text(
        f"🔢 <b>Количество задач в сессии</b>\n\n"
        f"Текущее количество: <b>{current_problems} задач</b>\n\n"
        f"Введите новое количество задач от {Config.MIN_PROBLEMS_PER_SESSION} до {Config.MAX_PROBLEMS_PER_SESSION}:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_settings")
        ]])
    )
    
    await state.set_state(SettingsStates.waiting_problems_input)
    await callback.answer()

@router.callback_query(F.data == "setting_sounds")
async def setting_sounds(callback: CallbackQuery):
    """Настройка звуков"""
    await callback.answer(
        "🔊 Эта настройка будет доступна в следующих версиях!",
        show_alert=True
    )

@router.callback_query(F.data == "setting_theme")
async def setting_theme(callback: CallbackQuery):
    """Настройка темы"""
    await callback.answer(
        "🌙 Эта настройка будет доступна в следующих версиях!",
        show_alert=True
    )

@router.callback_query(F.data == "setting_difficulty")
async def setting_difficulty(callback: CallbackQuery):
    """Настройка сложности"""
    await callback.answer(
        "📈 Эта настройка будет доступна в следующих версиях!",
        show_alert=True
    )

@router.callback_query(F.data == "reset_progress")
async def reset_progress(callback: CallbackQuery):
    """Сброс прогресса"""
    from keyboards.main_keyboard import get_confirmation_keyboard
    
    await callback.message.edit_text(
        "🔄 <b>Сброс прогресса</b>\n\n"
        "⚠️ <b>Внимание!</b> Это действие удалит:\n"
        "• Весь ваш прогресс по уровням\n"
        "• Статистику решенных задач\n"
        "• Все полученные достижения\n\n"
        "Вы уверены, что хотите продолжить?",
        reply_markup=get_confirmation_keyboard("reset_progress"),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "confirm_reset_progress")
async def confirm_reset_progress(callback: CallbackQuery, state: FSMContext):
    """Подтверждение сброса прогресса"""
    user_id = callback.from_user.id
    
    try:
        # Сбрасываем прогресс пользователя в базе данных
        async with db.async_session() as session:
            from sqlalchemy import update, delete
            from database.models import User, LearningSession, Problem, UserAchievement
            
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user:
                # Удаляем все связанные данные
                await session.execute(
                    delete(Problem).where(Problem.session_id.in_(
                        select(LearningSession.id).where(LearningSession.user_id == user.id)
                    ))
                )
                await session.execute(
                    delete(LearningSession).where(LearningSession.user_id == user.id)
                )
                await session.execute(
                    delete(UserAchievement).where(UserAchievement.user_id == user.id)
                )
                
                # Сбрасываем статистику пользователя
                await session.execute(
                    update(User).where(User.id == user.id).values(
                        current_level=1,
                        total_score=0
                    )
                )
                
                await session.commit()
                
                # Очищаем состояние
                await state.clear()
                
                await callback.message.edit_text(
                    "✅ <b>Прогресс сброшен!</b>\n\n"
                    "Ваш прогресс был успешно удален.\n"
                    "Теперь вы можете начать обучение с самого начала!",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu")
                    ]]),
                    parse_mode="HTML"
                )
                
                logger.info(f"Пользователь {user_id} сбросил свой прогресс")
                
            else:
                await callback.answer("❌ Пользователь не найден", show_alert=True)
                
    except Exception as e:
        logger.error(f"Ошибка сброса прогресса для пользователя {user_id}: {e}")
        await callback.answer("❌ Произошла ошибка при сбросе прогресса", show_alert=True)
    
    await callback.answer()

# Обработчики ввода настроек
@router.message(SettingsStates.waiting_time_input)
async def process_time_input(message: Message, state: FSMContext):
    """Обработка ввода времени на задачу"""
    try:
        new_time = int(message.text.strip())
        
        from config import Config
        
        if not (Config.MIN_TIME_PER_PROBLEM <= new_time <= Config.MAX_TIME_PER_PROBLEM):
            await message.answer(
                f"❌ <b>Неверное время!</b>\n\n"
                f"Время должно быть от {Config.MIN_TIME_PER_PROBLEM} до {Config.MAX_TIME_PER_PROBLEM} секунд.",
                parse_mode="HTML"
            )
            return
        
        # Обновляем настройку
        success = await db.update_user_setting(message.from_user.id, "time_per_problem", new_time)
        
        if success:
            await message.answer(
                f"✅ <b>Время на задачу обновлено!</b>\n\n"
                f"Новое время: <b>{new_time} секунд</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка при обновлении настройки")
        
        # Очищаем состояние и возвращаемся к настройкам
        await state.clear()
        
        # Показываем меню настроек
        from keyboards.main_keyboard import get_settings_keyboard
        await message.answer(
            "⚙️ <b>Настройки бота</b>\n\n"
            "Здесь ты можешь настроить бота под свои предпочтения:",
            reply_markup=get_settings_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ <b>Неверный формат!</b>\n\n"
            "Введите число (количество секунд)",
            parse_mode="HTML"
        )

@router.message(SettingsStates.waiting_problems_input)
async def process_problems_input(message: Message, state: FSMContext):
    """Обработка ввода количества задач"""
    try:
        new_problems = int(message.text.strip())
        
        from config import Config
        
        if not (Config.MIN_PROBLEMS_PER_SESSION <= new_problems <= Config.MAX_PROBLEMS_PER_SESSION):
            await message.answer(
                f"❌ <b>Неверное количество!</b>\n\n"
                f"Количество задач должно быть от {Config.MIN_PROBLEMS_PER_SESSION} до {Config.MAX_PROBLEMS_PER_SESSION}.",
                parse_mode="HTML"
            )
            return
        
        # Обновляем настройку
        success = await db.update_user_setting(message.from_user.id, "problems_per_session", new_problems)
        
        if success:
            await message.answer(
                f"✅ <b>Количество задач обновлено!</b>\n\n"
                f"Новое количество: <b>{new_problems} задач</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка при обновлении настройки")
        
        # Очищаем состояние и возвращаемся к настройкам
        await state.clear()
        
        # Показываем меню настроек
        from keyboards.main_keyboard import get_settings_keyboard
        await message.answer(
            "⚙️ <b>Настройки бота</b>\n\n"
            "Здесь ты можешь настроить бота под свои предпочтения:",
            reply_markup=get_settings_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ <b>Неверный формат!</b>\n\n"
            "Введите число (количество задач)",
            parse_mode="HTML"
        )

@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery, state: FSMContext):
    """Возврат к настройкам"""
    await state.clear()
    
    from keyboards.main_keyboard import get_settings_keyboard
    
    await callback.message.edit_text(
        "⚙️ <b>Настройки бота</b>\n\n"
        "Здесь ты можешь настроить бота под свои предпочтения:",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    
    await callback.answer()

# Обработчики медиа-материалов

@router.message(F.text == "📸 Учебные материалы")
async def photo_materials_menu(message: Message):
    """Меню учебных фото-материалов"""
    await message.answer(
        "📸 <b>Учебные материалы</b>\n\n"
        "Выбери категорию обучающих материалов:\n\n"
        "📚 Здесь ты найдешь схемы, таблицы, правила и примеры "
        "для изучения ментальной арифметики",
        reply_markup=get_photo_materials_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "🎬 Видео-уроки")
async def video_materials_menu(message: Message):
    """Меню выбора видеоуроков"""
    from keyboards.main_keyboard import get_video_lessons_keyboard
    
    await message.answer(
        "🎬 <b>Видео-уроки по ментальной арифметике</b>\n\n"
        "🧮 <b>Счеты Абакус (Соробан)</b> — это древний инструмент для вычислений, "
        "который помогает развить навыки быстрого счета в уме.\n\n"
        "✨ <b>Что дает изучение работы с абакусом:</b>\n"
        "• 🧠 Развитие обоих полушарий мозга\n"
        "• ⚡ Увеличение скорости вычислений\n"
        "• 🎯 Улучшение концентрации внимания\n"
        "• 💡 Развитие логического мышления\n"
        "• 📈 Повышение уверенности в математике\n\n"
        "🎥 <b>Выберите урок для просмотра:</b>\n"
        "Каждый урок содержит пошаговые объяснения и практические упражнения "
        "для освоения техник ментальной арифметики.",
        reply_markup=get_video_lessons_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "📋 Шпаргалки")
async def cheat_sheets_menu(message: Message):
    """Отправка всех шпаргалок одним сообщением"""
    from aiogram.types import InputMediaPhoto, FSInputFile
    import os
    
    # Получаем все изображения basics
    media_group = []
    
    for i in range(1, 11):  # basics_1.jpg до basics_10.jpg
        image_path = f"media/photos/basics_{i}.jpg"
        if os.path.exists(image_path):
            # Добавляем описание только к первому изображению
            caption = None
            if i == 1:
                caption = (
                    "📋 <b>Шпаргалки по ментальной арифметике</b>\n\n"
                    "🧮 Полный набор обучающих материалов:\n"
                    "• Основы ментального счета\n"
                    "• Техники концентрации\n"
                    "• Правила быстрого счета\n"
                    "• Тренировка памяти\n"
                    "• Примеры всех операций\n"
                    "• Позиция рук\n"
                    "• Таблицы и схемы\n"
                    "• Продвинутые техники\n\n"
                    "💡 Сохрани эти изображения для быстрого доступа!"
                )
            
            photo = InputMediaPhoto(
                media=FSInputFile(image_path),
                caption=caption,
                parse_mode="HTML" if caption else None
            )
            media_group.append(photo)
    
    if media_group:
        try:
            await message.answer_media_group(media_group)
            logger.info(f"Отправлены шпаргалки пользователю {message.from_user.id}")
        except Exception as e:
            logger.error(f"Ошибка отправки шпаргалок: {e}")
            await message.answer(
                "❌ <b>Ошибка загрузки шпаргалок</b>\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                parse_mode="HTML"
            )
    else:
        await message.answer(
            "❌ <b>Шпаргалки не найдены</b>\n\n"
            "Материалы временно недоступны.",
            parse_mode="HTML"
        )

# Дополнительные обработчики навигации
@router.callback_query(F.data == "back_to_photo_materials")
async def back_to_photo_materials(callback: CallbackQuery):
    """Возврат к меню фото-материалов"""
    await callback.message.edit_text(
        "📸 <b>Учебные материалы по ментальной арифметике</b>\n\n"
        "📖 <b>Пошаговое обучение</b> - полный курс с изображениями и пояснениями\n\n"
        "Или выберите конкретную категорию материалов:",
        reply_markup=get_photo_materials_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback: CallbackQuery):
    """Возврат в главное меню через callback"""
    await callback.message.delete()
    
    await callback.message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выбери действие:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "start_practice")
async def start_practice_callback(callback: CallbackQuery):
    """Начать тренировку после завершения курса"""
    await callback.message.edit_text(
        "🎯 <b>Тренировка ментальной арифметики</b>\n\n"
        "Выберите уровень для тренировки:",
        reply_markup=get_level_selection(),
        parse_mode="HTML"
    )
    await callback.answer("🚀 Переходим к тренировке!")

# Обработчики видеоуроков
@router.callback_query(F.data.startswith("video_lesson_"))
async def send_video_lesson(callback: CallbackQuery):
    """Отправка конкретного видеоурока"""
    from aiogram.types import FSInputFile
    import os
    
    try:
        # Сначала отвечаем на callback, чтобы избежать timeout
        await callback.answer("📹 Подготавливаем видеоурок...")
        
        # Извлекаем номер урока
        lesson_number = callback.data.split("_")[-1]
        
        # Словарь с описаниями уроков
        lesson_descriptions = {
            "1": "🎯 Знакомство с абакусом, прямой счет\n\n📚 Что такое абакус и правила работы с ним. Учимся показывать числа на счетах и решать примеры.",
            "2": "➕ Сложение в пятерке и десятке\n\n🔢 Секреты сложения на счетах абакус, используя состав чисел 5 и 10.",
            "3": "➕ Прибавляем 1, 2, 3, 4\n\n🧮 Учимся прибавлять цифры 1, 2, 3, 4 и решать примеры с этими цифрами.",
            "4": "➕ Изучаем действие +5\n\n🖐 Как прибавить 5 на счетах абакус и решать примеры с этой цифрой.",
            "5": "➕ Изучаем действие +6\n\n6️⃣ Как прибавить 6 на счетах абакус и решать примеры с этой цифрой.",
            "6": "➕ Изучаем действие +7\n\n7️⃣ Как прибавить 7 на счетах абакус и решать примеры с этой цифрой.",
            "7": "➕ Изучаем действие +8\n\n8️⃣ Как прибавить 8 на счетах абакус и решать примеры с этой цифрой.",
            "8": "➕ Изучаем действие +9\n\n9️⃣ Как прибавить 9 на счетах абакус и решать примеры с этой цифрой.",
            "9": "🧠 Что дает ментальная арифметика детям?\n\n💭 Польза ментальной арифметики для развития детей.",
            "10": "Выпуск 'Лучше всех'"
        }
        
        # Ищем видеофайл
        video_path = f"media/videos/{lesson_number}.mp4"
        
        if os.path.exists(video_path):
            # Проверяем размер файла (Telegram ограничение - 50 МБ)
            file_size = os.path.getsize(video_path)
            max_size = 50 * 1024 * 1024  # 50 МБ в байтах
            
            if file_size > max_size:
                await callback.message.answer(
                    f"❌ <b>Видеоурок {lesson_number} слишком большой</b>\n\n"
                    f"📏 Размер файла: {file_size / (1024*1024):.1f} МБ\n"
                    f"📐 Максимальный размер: 50 МБ\n\n"
                    f"🔗 Пожалуйста, обратитесь к администратору для получения ссылки на видео.",
                    parse_mode="HTML"
                )
                logger.warning(f"Видеоурок {lesson_number} слишком большой: {file_size / (1024*1024):.1f} МБ")
                return
            
            try:
                description = lesson_descriptions.get(lesson_number, f"Урок {lesson_number}")
                
                # Отправляем сообщение о начале загрузки
                loading_msg = await callback.message.answer(
                    f"⏳ <b>Загружаем урок {lesson_number}...</b>\n\n"
                    f"📹 Это может занять несколько секунд",
                    parse_mode="HTML"
                )
                
                video = FSInputFile(video_path)
                await callback.message.answer_video(
                    video=video,
                    caption=f"📹 <b>Урок {lesson_number}</b>\n\n"
                            f"{description}\n\n"
                            f"🎬 Изучайте материал в удобном темпе и практикуйтесь вместе с инструктором!",
                    parse_mode="HTML"
                )
                
                # Удаляем сообщение о загрузке
                await loading_msg.delete()
                
                logger.info(f"Отправлен видеоурок {lesson_number} пользователю {callback.from_user.id}")
                
            except Exception as e:
                logger.error(f"Ошибка отправки видеоурока {lesson_number}: {e}")
                await callback.message.answer(
                    f"❌ <b>Ошибка загрузки урока {lesson_number}</b>\n\n"
                    f"Возможные причины:\n"
                    f"• Файл слишком большой\n" 
                    f"• Проблемы с сетью\n"
                    f"• Временные неполадки сервера\n\n"
                    f"Попробуйте позже или обратитесь к администратору.",
                    parse_mode="HTML"
                )
        else:
            await callback.message.answer(
                f"❌ <b>Видеоурок {lesson_number} не найден</b>\n\n"
                f"📁 Файл отсутствует в системе.\n"
                f"Обратитесь к администратору.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Общая ошибка в обработчике видеоуроков: {e}")
        try:
            await callback.message.answer(
                "❌ <b>Произошла ошибка</b>\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                parse_mode="HTML"
            )
        except:
            # Если и это не работает, просто логируем
            logger.error("Не удалось отправить сообщение об ошибке") 