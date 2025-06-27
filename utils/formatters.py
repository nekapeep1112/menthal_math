from typing import Dict, List
from datetime import datetime, timedelta

def format_welcome_message(name: str) -> str:
    """Форматирование приветственного сообщения"""
    return f"""
🧮 <b>Добро пожаловать в Ментальную Арифметику!</b>

Привет, <b>{name}</b>! 👋

Я помогу тебе развить навыки быстрого счёта в уме. 
Здесь ты найдёшь:

🎯 <b>10 уровней сложности</b> - от простого к сложному
⚡ <b>Быстрые задачи</b> - развивай скорость мышления
🏆 <b>Достижения</b> - собирай награды за успехи
📊 <b>Статистика</b> - отслеживай свой прогресс

<i>Готов начать тренировку?</i> 💪
"""

def get_random_greeting(name: str) -> str:
    """Случайное приветствие из 15 вариантов"""
    import random
    
    greetings = [
        f"🌟 Привет-привет, {name}! Готов покорить мир математики?",
        f"🎉 Салют, {name}! Давай тренировать мозг вместе!",
        f"🚀 Здорово, {name}! Время для математических приключений!",
        f"⭐ Отлично, {name}! Бот ментальной арифметики к твоим услугам!",
        f"🎯 Привет, {name}! Готов стать мастером быстрого счета?",
        f"🌈 Классно, {name}! Математика ждет тебя!",
        f"💪 Здравствуй, {name}! Прокачаем математические навыки?",
        f"🎊 Хей, {name}! Добро пожаловать в увлекательный мир чисел!",
        f"🔥 Превосходно, {name}! Готов к математическим вызовам?",
        f"🌸 Добро пожаловать, {name}! Начнем математическое путешествие!",
        f"⚡ Супер, {name}! Твой мозг готов к тренировке?",
        f"🎈 Ура, {name}! Самое время заняться ментальной арифметикой!",
        f"✨ Замечательно, {name}! Погрузимся в мир быстрого счета!",
        f"🏆 Браво, {name}! Стань чемпионом математики!",
        f"🎪 Фантастика, {name}! Математический цирк начинается!"
    ]
    
    selected_greeting = random.choice(greetings)
    
    return f"""
{selected_greeting}

🧮 <b>Обучающий бот ментальной арифметики</b>

🎯 <b>Возможности бота:</b>
• 📚 10 уровней сложности
• 🧮 Интерактивные задачи  
• 📊 Подробная статистика
• 🏆 Система достижений
• 🏅 Общий рейтинг
• 📸 Обучающие материалы
• 🎬 Видео-уроки
• ⚙️ Персональные настройки

🚀 <b>Выбери действие из меню!</b> 👇
"""

def format_level_info(level: int, description: str, difficulty: str) -> str:
    """Форматирование информации об уровне"""
    return f"""
📚 <b>Уровень {level}</b> {difficulty}

{description}

<i>Выбери этот уровень, чтобы начать обучение!</i>
"""

def format_problem(problem_text: str, problem_num: int, total_problems: int, time_left: int) -> str:
    """Форматирование задачи"""
    progress_bar = get_progress_bar(problem_num, total_problems)
    
    return f"""
🧮 <b>Задача {problem_num}/{total_problems}</b>

{progress_bar}

<b>{problem_text}</b>

⏱️ Времени осталось: <b>{time_left}с</b>

<i>Выбери правильный ответ:</i>
"""

def format_user_stats(stats: Dict) -> str:
    """Форматирование статистики пользователя"""
    if not stats:
        return "📊 <b>Статистика недоступна</b>\n\nНачни решать задачи, чтобы увидеть свою статистику!"
    
    accuracy_emoji = get_accuracy_emoji(stats["accuracy"])
    level_emoji = get_level_emoji(stats["level"])
    
    return f"""
📊 <b>Твоя статистика</b>

{level_emoji} <b>Текущий уровень:</b> {stats["level"]}
🎯 <b>Общий счёт:</b> {stats["total_score"]} очков

📈 <b>Обучение:</b>
├ 🎮 Всего сессий: {stats["total_sessions"]}
├ ✅ Завершено: {stats["completed_sessions"]}
├ 🧮 Решено задач: {stats["total_problems"]}
└ 🎯 Правильных ответов: {stats["correct_answers"]}

{accuracy_emoji} <b>Точность:</b> {stats["accuracy"]}%
🏆 <b>Достижения:</b> {stats["achievements_count"]}

<i>Продолжай тренироваться!</i> 💪
"""

def format_session_result(correct: int, total: int, time_taken: float, level: int, 
                         last_answer_correct: bool = None, last_correct_answer: int = None, 
                         new_record: bool = False) -> str:
    """Форматирование результатов сессии"""
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0
    accuracy_emoji = get_accuracy_emoji(accuracy)
    
    avg_time = round(time_taken / total, 1) if total > 0 else 0
    
    result_emoji = "🎉" if accuracy >= 80 else "👍" if accuracy >= 60 else "💪"
    record_text = "\n🏆 <b>Новый рекорд!</b>" if new_record else ""
    
    # Добавляем результат последнего ответа если он передан
    last_answer_text = ""
    if last_answer_correct is not None:
        if last_answer_correct:
            last_answer_text = "✅ <b>Последний ответ: Правильно!</b>\n\n"
        else:
            last_answer_text = f"❌ <b>Последний ответ: Неправильно!</b>\nПравильный ответ: <b>{last_correct_answer}</b>\n\n"
    
    return f"""
{last_answer_text}{result_emoji} <b>Сессия завершена!</b>

📚 <b>Уровень:</b> {level}
🎯 <b>Результат:</b> {correct}/{total} правильных
{accuracy_emoji} <b>Точность:</b> {accuracy}%
⏱️ <b>Среднее время:</b> {avg_time}с на задачу
🕐 <b>Общее время:</b> {format_time(time_taken)}
{record_text}

{get_result_message(accuracy)}
"""

def format_achievement_earned(achievement_name: str, achievement_desc: str, achievement_icon: str) -> str:
    """Форматирование сообщения о получении достижения"""
    return f"""
🎉 <b>Новое достижение!</b>

{achievement_icon} <b>{achievement_name}</b>
<i>{achievement_desc}</i>

Поздравляем! 🎊
"""

def format_achievements_list(achievements: List[Dict]) -> str:
    """Форматирование списка достижений"""
    if not achievements:
        return "🏆 <b>Достижения</b>\n\nУ тебя пока нет достижений.\nРеши несколько задач, чтобы получить первые награды! 💪"
    
    text = "🏆 <b>Твои достижения</b>\n\n"
    
    for achievement in achievements:
        earned_date = achievement.get("earned_at", "")
        if earned_date:
            earned_date = f" ({earned_date.strftime('%d.%m.%Y')})"
        
        text += f"{achievement['icon']} <b>{achievement['name']}</b>{earned_date}\n"
        text += f"<i>{achievement['description']}</i>\n\n"
    
    return text

def get_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Создание прогресс-бара"""
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {current}/{total}"

def get_accuracy_emoji(accuracy: float) -> str:
    """Получение эмодзи для точности"""
    if accuracy >= 95:
        return "🌟"
    elif accuracy >= 85:
        return "⭐"
    elif accuracy >= 75:
        return "🎯"
    elif accuracy >= 60:
        return "📈"
    else:
        return "💪"

def get_level_emoji(level: int) -> str:
    """Получение эмодзи для уровня"""
    if level >= 10:
        return "👑"
    elif level >= 8:
        return "💎"
    elif level >= 6:
        return "🏆"
    elif level >= 4:
        return "🥇"
    elif level >= 2:
        return "🥈"
    else:
        return "🥉"

def get_result_message(accuracy: float) -> str:
    """Получение мотивационного сообщения по результатам"""
    if accuracy >= 90:
        return "<i>Отличный результат! Ты настоящий математический гений! 🌟</i>"
    elif accuracy >= 80:
        return "<i>Очень хорошо! Продолжай в том же духе! ⭐</i>"
    elif accuracy >= 70:
        return "<i>Хороший результат! Есть куда расти! 📈</i>"
    elif accuracy >= 50:
        return "<i>Неплохо! Больше практики и будет лучше! 💪</i>"
    else:
        return "<i>Не расстраивайся! Каждый мастер когда-то был новичком! 🎯</i>"

def format_time(seconds: float) -> str:
    """Форматирование времени"""
    if seconds < 60:
        return f"{int(seconds)}с"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}м {secs}с"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}ч {minutes}м"

def format_help_message() -> str:
    """Форматирование сообщения помощи"""
    return """
❓ <b>Справка</b>

<b>Как пользоваться ботом:</b>

🧮 <b>Начать обучение</b> - выбери уровень и решай задачи
📊 <b>Моя статистика</b> - посмотри свой прогресс
🏆 <b>Достижения</b> - собирай награды за успехи
⚙️ <b>Настройки</b> - настрой бота под себя

<b>Уровни сложности:</b>
🟢 1-2: Простые задачи на сложение/вычитание
🟡 3-5: Средняя сложность с большими числами
🟠 6-8: Сложные задачи и умножение
🔴 9-10: Экспертный уровень

<b>Советы:</b>
• Решай задачи каждый день для лучшего результата
• Не торопись - точность важнее скорости
• Используй техники ментальной арифметики
• Следи за своим прогрессом в статистике

<i>Удачи в обучении! 🍀</i>
"""

def format_leaderboard(leaderboard: List[Dict], user_rank: Dict = None) -> str:
    """Форматирование рейтинга пользователей"""
    if not leaderboard:
        return """
🏆 <b>Общий рейтинг</b>

Рейтинг пока пуст.
Начни решать задачи, чтобы попасть в топ! 💪
"""
    
    text = "🏆 <b>Общий рейтинг</b>\n\n"
    
    # Добавляем топ пользователей
    for user in leaderboard:
        position = user['position']
        name = user['name']
        score = user['score']
        level = user['level']
        
        # Эмодзи для позиций
        if position == 1:
            emoji = "🥇"
        elif position == 2:
            emoji = "🥈"
        elif position == 3:
            emoji = "🥉"
        else:
            emoji = f"{position}."
        
        # Эмодзи для уровня
        level_emoji = get_level_emoji(level)
        
        text += f"{emoji} <b>{name}</b>\n"
        text += f"    💎 {score} очков {level_emoji} ур.{level}\n\n"
    
    # Добавляем информацию о позиции текущего пользователя
    if user_rank and user_rank.get('position'):
        position = user_rank['position']
        total = user_rank['total_users']
        score = user_rank['score']
        level = user_rank['level']
        
        text += "─" * 25 + "\n"
        text += f"📍 <b>Твоя позиция:</b> {position}/{total}\n"
        text += f"💎 <b>Твои очки:</b> {score}\n"
        text += f"{get_level_emoji(level)} <b>Твой уровень:</b> {level}"
    
    return text 