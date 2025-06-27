from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import time
import logging

from database.database import db
from keyboards.main_keyboard import get_answer_keyboard, get_learning_keyboard, get_session_results_keyboard, get_main_menu
from utils.math_generator import math_generator
from utils.formatters import format_problem, format_session_result
from config import Config

router = Router()
logger = logging.getLogger(__name__)

class LearningStates(StatesGroup):
    solving_problem = State()
    waiting_custom_answer = State()

# Хранение активных сессий обучения
active_sessions = {}

class LearningSession:
    """Класс для управления сессией обучения"""
    
    def __init__(self, user_id: int, level: int, problems_per_session: int = None, time_per_problem: int = None):
        self.user_id = user_id
        self.level = level
        self.current_problem = 0
        self.correct_answers = 0
        self.total_problems = problems_per_session or Config.PROBLEMS_PER_LEVEL
        self.time_per_problem = time_per_problem or Config.TIME_LIMIT_SECONDS
        self.start_time = time.time()
        self.problems_data = []
        self.current_problem_start = None
        self.is_paused = False
        self.timer_task = None  # Для хранения задачи таймера
        
    def next_problem(self):
        """Переход к следующей задаче"""
        self.current_problem += 1
        self.current_problem_start = time.time()
        
    def add_answer(self, user_answer: int, correct_answer: int, time_taken: float, problem_text: str = ""):
        """Добавление ответа"""
        is_correct = user_answer == correct_answer
        if is_correct:
            self.correct_answers += 1
            
        self.problems_data.append({
            'problem_text': problem_text,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'time_taken': time_taken
        })
        
    def get_total_time(self):
        """Получение общего времени сессии"""
        return time.time() - self.start_time
        
    def is_completed(self):
        """Проверка завершения сессии"""
        return self.current_problem >= self.total_problems
    
    def cancel_timer(self):
        """Отмена таймера"""
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
            self.timer_task = None

async def start_timer(session: LearningSession, message: Message):
    """Запуск таймера для задачи"""
    try:
        await asyncio.sleep(session.time_per_problem)
        
        # Проверяем, что сессия все еще активна
        if session.user_id in active_sessions and active_sessions[session.user_id] == session:
            await handle_time_up(session.user_id, message, session)
    except asyncio.CancelledError:
        # Таймер был отменен - это нормально
        pass
    except Exception as e:
        logger.error(f"Ошибка в таймере для пользователя {session.user_id}: {e}")

async def handle_time_up(user_id: int, message: Message, session: LearningSession):
    """Обработка истечения времени на задачу"""
    if user_id not in active_sessions or session != active_sessions[user_id]:
        return  # Сессия уже завершена или изменена
    
    # Записываем неправильный ответ (время истекло)
    time_taken = time.time() - session.current_problem_start if session.current_problem_start else session.time_per_problem
    session.add_answer(-1, session.current_correct_answer, time_taken, session.current_problem_text)
    
    # Проверяем завершение сессии
    if session.is_completed():
        logger.info(f"Сессия завершена для пользователя {user_id} (время истекло)")
        
        # Завершаем сессию (без состояния)
        await finish_learning_session_simple(message, session, False, session.current_correct_answer)
    else:
        # Показываем результат
        try:
            await message.edit_text(
                f"⏰ <b>Время истекло!</b>\n\n"
                f"Правильный ответ: <b>{session.current_correct_answer}</b>",
                parse_mode="HTML"
            )
            await asyncio.sleep(2)  # Показываем результат 2 секунды
        except Exception as e:
            logger.warning(f"Не удалось обновить сообщение: {e}")
        
        # Отправляем следующую задачу
        await send_next_problem(message, session, edit_message=True)

async def finish_learning_session_simple(message: Message, session: LearningSession, 
                                          last_answer_correct: bool = None, last_correct_answer: int = None):
    """Упрощенное завершение сессии обучения (без FSMContext)"""
    user_id = session.user_id
    logger.info(f"Упрощенное завершение сессии для пользователя {user_id}")
    
    # Подготавливаем результаты
    total_time = session.get_total_time()
    accuracy = (session.correct_answers / session.total_problems) * 100
    
    # Сохраняем результаты в базу данных
    success = await db.save_learning_session(
        telegram_id=user_id,
        level=session.level,
        problems_data=session.problems_data,
        total_time=total_time
    )
    
    if success:
        logger.info(f"Сессия сохранена в БД для пользователя {user_id}")
        
        # Проверяем новые достижения
        new_achievements = await db.check_achievements(user_id)
        
        # Уведомляем о новых достижениях
        if new_achievements:
            from utils.formatters import format_achievement_earned
            for achievement in new_achievements:
                achievement_text = format_achievement_earned(
                    achievement.name,
                    achievement.description,
                    achievement.icon
                )
                await message.answer(achievement_text, parse_mode="HTML")
    
    # Отменяем таймер и удаляем сессию из активных
    if user_id in active_sessions:
        session.cancel_timer()
        del active_sessions[user_id]
    
    # Форматируем результат
    from utils.formatters import format_session_result
    result_text = format_session_result(
        session.correct_answers,
        session.total_problems,
        total_time,
        session.level,
        last_answer_correct,
        last_correct_answer
    )
    
    # Отправляем результаты
    from keyboards.main_keyboard import get_session_results_keyboard
    await message.answer(
        result_text,
        reply_markup=get_session_results_keyboard(),
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {user_id} завершил сессию. Результат: {session.correct_answers}/{session.total_problems}")

async def start_learning_session(callback: CallbackQuery, state: FSMContext, level: int):
    """Начало сессии обучения"""
    user_id = callback.from_user.id
    
    # Получаем настройки пользователя
    from database.database import db
    user_settings = await db.get_user_settings(user_id)
    
    # Создаем новую сессию с пользовательскими настройками
    session = LearningSession(
        user_id, 
        level,
        problems_per_session=user_settings.get("problems_per_session"),
        time_per_problem=user_settings.get("time_per_problem")
    )
    active_sessions[user_id] = session
    
    # Устанавливаем состояние
    await state.set_state(LearningStates.solving_problem)
    await state.update_data(level=level)
    
    # Отправляем первую задачу
    await send_next_problem(callback.message, session, edit_message=True)
    
    await callback.answer("🎯 Сессия обучения начата!")
    logger.info(f"Пользователь {user_id} начал сессию на уровне {level}")

async def send_next_problem(message: Message, session: LearningSession, edit_message: bool = False):
    """Отправка следующей задачи"""
    # Отменяем предыдущий таймер
    session.cancel_timer()
    
    session.next_problem()
    
    # Генерируем задачу
    problem_text, correct_answer = math_generator.generate_problem(session.level)
    
    # Сохраняем правильный ответ и текст задачи в сессии
    session.current_correct_answer = correct_answer
    session.current_problem_text = problem_text
    
    # Форматируем сообщение
    formatted_problem = format_problem(
        problem_text,
        session.current_problem,
        session.total_problems,
        session.time_per_problem
    )
    
    # Создаем клавиатуру с вариантами ответов
    answer_keyboard = get_answer_keyboard(correct_answer)
    
    if edit_message:
        await message.edit_text(
            formatted_problem,
            reply_markup=answer_keyboard,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            formatted_problem,
            reply_markup=answer_keyboard,
            parse_mode="HTML"
        )
    
    # Запускаем таймер для автоматического перехода к следующей задаче
    session.timer_task = asyncio.create_task(
        start_timer(session, message)
    )

@router.callback_query(F.data.startswith("answer_"), LearningStates.solving_problem)
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа пользователя"""
    user_id = callback.from_user.id
    
    if user_id not in active_sessions:
        await callback.answer("❌ Сессия не найдена")
        return
    
    session = active_sessions[user_id]
    
    # Отменяем таймер, так как пользователь ответил
    session.cancel_timer()
    
    # Получаем ответ пользователя
    try:
        user_answer = int(callback.data.split("_")[1])
    except ValueError:
        await callback.answer("❌ Неверный ответ")
        return
    
    # Вычисляем время решения
    time_taken = time.time() - session.current_problem_start if session.current_problem_start else 0
    
    # Добавляем ответ в сессию
    session.add_answer(user_answer, session.current_correct_answer, time_taken)
    
    # Проверяем правильность ответа
    is_correct = user_answer == session.current_correct_answer
    
    # Проверяем завершение сессии
    if session.is_completed():
        logger.info(f"Сессия завершена для пользователя {user_id}")
        
        # Удаляем старое сообщение с задачей
        try:
            await callback.message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")
        
        # Завершаем сессию с указанием результата последнего ответа
        logger.info(f"Начинаем завершение сессии для пользователя {user_id}")
        await finish_learning_session(callback.message, session, state, is_correct, session.current_correct_answer)
        await callback.answer()
    else:
        # Показываем результат через popup
        if is_correct:
            await callback.answer("✅ Правильно!", show_alert=False)
        else:
            await callback.answer(
                f"❌ Неправильно! Правильный ответ: {session.current_correct_answer}",
                show_alert=True
            )
        
        # Отправляем следующую задачу
        await send_next_problem(callback.message, session, edit_message=True)

@router.callback_query(F.data == "custom_answer", LearningStates.solving_problem)
async def request_custom_answer(callback: CallbackQuery, state: FSMContext):
    """Запрос ввода собственного ответа"""
    await state.set_state(LearningStates.waiting_custom_answer)
    
    await callback.message.answer(
        "✏️ <b>Введи свой ответ:</b>\n\n"
        "Напиши число и отправь сообщение",
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.message(LearningStates.waiting_custom_answer)
async def process_custom_answer(message: Message, state: FSMContext):
    """Обработка пользовательского ответа"""
    user_id = message.from_user.id
    
    if user_id not in active_sessions:
        await message.answer("❌ Сессия не найдена")
        return
    
    session = active_sessions[user_id]
    
    # Отменяем таймер, так как пользователь ответил
    session.cancel_timer()
    
    try:
        user_answer = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ <b>Некорректный ответ!</b>\n\n"
            "Введи целое число, например: 42",
            parse_mode="HTML"
        )
        return
    
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except:
        pass
    
    # Вычисляем время решения
    time_taken = time.time() - session.current_problem_start if session.current_problem_start else 0
    
    # Добавляем ответ в сессию
    session.add_answer(user_answer, session.current_correct_answer, time_taken)
    
    # Проверяем правильность ответа
    is_correct = user_answer == session.current_correct_answer
    
    # Возвращаемся к состоянию решения задач
    await state.set_state(LearningStates.solving_problem)
    
    # Отправляем уведомление о результате
    if is_correct:
        result_text = "✅ <b>Правильно!</b>"
    else:
        result_text = f"❌ <b>Неправильно!</b>\nПравильный ответ: <b>{session.current_correct_answer}</b>"
    
    # Проверяем завершение сессии
    if session.is_completed():
        await finish_learning_session(message, session, state, is_correct, session.current_correct_answer)
    else:
        # Отправляем уведомление и следующую задачу
        await message.answer(result_text, parse_mode="HTML")
        await send_next_problem(message, session)

async def finish_learning_session(message: Message, session: LearningSession, state: FSMContext, 
                                  last_answer_correct: bool = None, last_correct_answer: int = None):
    """Завершение сессии обучения"""
    user_id = session.user_id
    logger.info(f"Функция finish_learning_session вызвана для пользователя {user_id}")
    
    # Подготавливаем результаты
    total_time = session.get_total_time()
    accuracy = (session.correct_answers / session.total_problems) * 100
    logger.info(f"Подготовлены результаты: время={total_time:.1f}с, точность={accuracy:.1f}%")
    
    # Сохраняем результаты в базу данных
    success = await db.save_learning_session(
        telegram_id=user_id,
        level=session.level,
        problems_data=session.problems_data,
        total_time=total_time
    )
    
    if success:
        logger.info(f"Сессия сохранена в БД для пользователя {user_id}")
        
        # Проверяем новые достижения
        new_achievements = await db.check_achievements(user_id)
        
        # Уведомляем о новых достижениях
        if new_achievements:
            from utils.formatters import format_achievement_earned
            for achievement in new_achievements:
                achievement_text = format_achievement_earned(
                    achievement.name,
                    achievement.description,
                    achievement.icon
                )
                await message.answer(achievement_text, parse_mode="HTML")
    else:
        logger.error(f"Ошибка сохранения сессии для пользователя {user_id}")
    
    # Отменяем таймер и удаляем сессию из активных
    if user_id in active_sessions:
        session.cancel_timer()
        del active_sessions[user_id]
    
    # Сохраняем информацию о завершенной сессии в состоянии для кнопок
    session_successful = accuracy >= 80
    await state.set_data({
        "last_completed_level": session.level,
        "last_session_successful": session_successful,
        "last_session_accuracy": accuracy
    })
    
    # Форматируем результат
    result_text = format_session_result(
        session.correct_answers,
        session.total_problems,
        total_time,
        session.level,
        last_answer_correct,
        last_correct_answer
    )
    
    # Отправляем результаты
    logger.info(f"Отправляем итоги сессии для пользователя {user_id}")
    from config import Config
    is_max_level = session.level >= Config.MAX_LEVEL
    
    await message.answer(
        result_text,
        reply_markup=get_session_results_keyboard(session_successful, is_max_level),
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {user_id} завершил сессию. Результат: {session.correct_answers}/{session.total_problems}")

@router.callback_query(F.data == "stop_learning")
async def stop_learning(callback: CallbackQuery, state: FSMContext):
    """Остановка обучения"""
    user_id = callback.from_user.id
    
    if user_id in active_sessions:
        session = active_sessions[user_id]
        # Отменяем таймер перед завершением
        session.cancel_timer()
        await finish_learning_session(callback.message, session, state)
    else:
        await state.clear()
        await callback.message.edit_text(
            "❌ <b>Обучение остановлено</b>",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    
    await callback.answer("Обучение остановлено")

@router.callback_query(F.data == "pause_learning")
async def pause_learning(callback: CallbackQuery):
    """Пауза в обучении"""
    user_id = callback.from_user.id
    
    if user_id in active_sessions:
        session = active_sessions[user_id]
        session.is_paused = not session.is_paused
        
        if session.is_paused:
            text = "⏸️ <b>Обучение приостановлено</b>\n\nНажми кнопку снова, чтобы продолжить"
        else:
            text = "▶️ <b>Обучение продолжено</b>\n\nРеши текущую задачу!"
        
        await callback.answer(
            "⏸️ Пауза" if session.is_paused else "▶️ Продолжение"
        )
    else:
        await callback.answer("❌ Сессия не найдена")

@router.callback_query(F.data == "repeat_level")
async def repeat_level(callback: CallbackQuery, state: FSMContext):
    """Повторить текущий уровень"""
    data = await state.get_data()
    level = data.get("last_completed_level", 1)
    
    await start_learning_session(callback, state, level)

@router.callback_query(F.data == "next_level")
async def next_level(callback: CallbackQuery, state: FSMContext):
    """Перейти на следующий уровень"""
    user_id = callback.from_user.id
    
    # Получаем информацию о последнем пройденном уровне из состояния
    data = await state.get_data()
    last_completed_level = data.get("last_completed_level", 1)
    
    # Получаем текущий доступный уровень пользователя из базы данных
    user_stats = await db.get_user_stats(user_id)
    current_available_level = user_stats.get("level", 1) if user_stats else 1
    
    # Проверяем, можем ли мы перейти на следующий уровень
    # Следующий уровень доступен только если он не превышает текущий доступный уровень
    next_level_num = last_completed_level + 1
    
    if next_level_num > current_available_level:
        # Уровень еще не разблокирован
        await callback.answer(
            "🔒 Следующий уровень еще не разблокирован!\n"
            f"Для доступа к уровню {next_level_num} нужно набрать 80%+ точности на уровне {current_available_level}.",
            show_alert=True
        )
        logger.info(f"Пользователь {user_id} пытался перейти на недоступный уровень {next_level_num}")
        return
    
    # Ограничиваем максимальным уровнем
    next_level_num = min(next_level_num, Config.MAX_LEVEL)
    
    logger.info(f"Пользователь {user_id} переходит с уровня {last_completed_level} на уровень {next_level_num}")
    
    await start_learning_session(callback, state, next_level_num)

@router.callback_query(F.data == "detailed_stats")
async def show_detailed_stats(callback: CallbackQuery):
    """Показать подробную статистику"""
    stats = await db.get_user_stats(callback.from_user.id)
    from utils.formatters import format_user_stats
    
    await callback.message.answer(
        format_user_stats(stats),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "show_leaderboard")
async def show_leaderboard(callback: CallbackQuery):
    """Показать рейтинг из результатов сессии"""
    user_id = callback.from_user.id
    
    # Получаем рейтинг и позицию пользователя
    leaderboard = await db.get_leaderboard(limit=10)
    user_rank = await db.get_user_rank(user_id)
    
    from utils.formatters import format_leaderboard
    leaderboard_text = format_leaderboard(leaderboard, user_rank)
    
    await callback.message.answer(leaderboard_text, parse_mode="HTML")
    await callback.answer()

 