from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="🧮 Начать обучение"),
        KeyboardButton(text="📊 Моя статистика")
    )
    builder.row(
        KeyboardButton(text="🏆 Достижения"),
        KeyboardButton(text="🏅 Рейтинг")
    )
    builder.row(
        KeyboardButton(text="📸 Учебные материалы"),
        KeyboardButton(text="🎬 Видео-уроки")
    )
    builder.row(
        KeyboardButton(text="📋 Шпаргалки"),
        KeyboardButton(text="⚙️ Настройки")
    )
    builder.row(
        KeyboardButton(text="❓ Помощь")
    )
    
    return builder.as_markup(resize_keyboard=True, persistent=True)

def get_level_selection(current_level: int = 1, max_level: int = 10) -> InlineKeyboardMarkup:
    """Клавиатура выбора уровня"""
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки уровней по 3 в ряд
    for level in range(1, max_level + 1):
        if level <= current_level:
            # Доступные уровни
            text = f"📚 Уровень {level}"
            if level == current_level:
                text = f"⭐ Уровень {level}"
        else:
            # Заблокированные уровни
            text = f"🔒 Уровень {level}"
        
        builder.button(
            text=text,
            callback_data=f"level_{level}" if level <= current_level else "level_locked"
        )
    
    builder.adjust(3)  # 3 кнопки в ряд
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def get_learning_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура во время обучения"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="❌ Завершить", callback_data="stop_learning"),
        InlineKeyboardButton(text="⏸️ Пауза", callback_data="pause_learning")
    )
    
    return builder.as_markup()

def get_answer_keyboard(answer: int) -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов"""
    builder = InlineKeyboardBuilder()
    
    # Генерируем 4 варианта ответа: правильный + 3 неправильных
    import random
    answers = [answer]
    
    # Добавляем неправильные варианты
    while len(answers) < 4:
        wrong_answer = answer + random.randint(-10, 10)
        if wrong_answer not in answers and wrong_answer >= 0:
            answers.append(wrong_answer)
    
    # Перемешиваем варианты
    random.shuffle(answers)
    
    # Создаем кнопки
    for ans in answers:
        builder.button(
            text=str(ans),
            callback_data=f"answer_{ans}"
        )
    
    builder.adjust(2)  # 2 кнопки в ряд
    
    # Кнопка ввода своего ответа
    builder.row(
        InlineKeyboardButton(text="✏️ Ввести свой ответ", callback_data="custom_answer")
    )
    
    return builder.as_markup()

def get_session_results_keyboard(session_successful: bool = True, is_max_level: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура результатов сессии"""
    builder = InlineKeyboardBuilder()
    
    # Первый ряд - повторить уровень и следующий уровень (если доступен)
    if session_successful and not is_max_level:
        builder.row(
            InlineKeyboardButton(text="🔄 Повторить уровень", callback_data="repeat_level"),
            InlineKeyboardButton(text="➡️ Следующий уровень", callback_data="next_level")
        )
    else:
        # Если сессия не пройдена успешно или это максимальный уровень - только повторить
        builder.row(
            InlineKeyboardButton(text="🔄 Повторить уровень", callback_data="repeat_level")
        )
    
    builder.row(
        InlineKeyboardButton(text="📊 Подробная статистика", callback_data="detailed_stats"),
        InlineKeyboardButton(text="🏅 Рейтинг", callback_data="show_leaderboard")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏱️ Время на задачу", callback_data="setting_time"),
        InlineKeyboardButton(text="🔢 Количество задач", callback_data="setting_problems")
    )
    builder.row(
        InlineKeyboardButton(text="🔊 Звуки", callback_data="setting_sounds"),
        InlineKeyboardButton(text="🌙 Темный режим", callback_data="setting_theme")
    )
    builder.row(
        InlineKeyboardButton(text="📈 Сложность", callback_data="setting_difficulty"),
        InlineKeyboardButton(text="🔄 Сбросить прогресс", callback_data="reset_progress")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
    )
    
    return builder.as_markup()

def get_photo_materials_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора фото-материалов"""
    builder = InlineKeyboardBuilder()
    
    # Пошаговое обучение (выделяем отдельно)
    builder.row(
        InlineKeyboardButton(text="📖 Пошаговое обучение", callback_data="start_step_learning")
    )
    
    # Основные категории учебных материалов
    materials = [
        ("🔢 Основы счета", "photo_basics"),
        ("➕ Сложение", "photo_addition"),
        ("➖ Вычитание", "photo_subtraction"),
        ("✖️ Умножение", "photo_multiplication"),
        ("➗ Деление", "photo_division"),
        ("🧮 Ментальная арифметика", "photo_mental")
    ]
    
    for text, callback in materials:
        builder.button(text=text, callback_data=callback)
    
    builder.adjust(2)  # 2 кнопки в ряд
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def get_video_lessons_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора видеоуроков"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки уроков по 2 в ряд (1-10 уроков)
    for i in range(1, 11):
        builder.button(
            text=f"📹 Урок {i}",
            callback_data=f"video_lesson_{i}"
        )
    
    builder.adjust(2)  # 2 кнопки в ряд
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    )
    
    return builder.as_markup()



