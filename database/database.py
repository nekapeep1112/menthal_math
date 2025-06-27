from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from database.models import Base, User, LearningSession, Problem, Achievement, UserAchievement, UserSettings
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        self.engine = create_async_engine(
            Config.DATABASE_URL,
            echo=Config.DEBUG,
            future=True
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Создаем стандартные достижения
        await self.create_default_achievements()
        logger.info("База данных инициализирована")
    
    async def create_default_achievements(self):
        """Создание стандартных достижений"""
        achievements = [
            ("Новичок", "Решите первую задачу", "🎯", "level", 1),
            ("Ученик", "Достигните 3 уровня", "📚", "level", 3),
            ("Эксперт", "Достигните 5 уровня", "🧠", "level", 5),
            ("Мастер", "Достигните 7 уровня", "🏆", "level", 7),
            ("Гений", "Достигните 10 уровня", "👑", "level", 10),
            ("Скорость", "Решите задачу за 5 секунд", "⚡", "speed", 5),
            ("Точность", "Решите 10 задач подряд правильно", "🎯", "streak", 10),
            ("Выносливость", "Решите 50 задач", "💪", "total", 50),
        ]
        
        async with self.async_session() as session:
            for name, desc, icon, cond_type, cond_value in achievements:
                # Проверяем, существует ли уже такое достижение
                result = await session.execute(
                    select(Achievement).where(Achievement.name == name)
                )
                if not result.scalar_one_or_none():
                    achievement = Achievement(
                        name=name,
                        description=desc,
                        icon=icon,
                        condition_type=cond_type,
                        condition_value=cond_value
                    )
                    session.add(achievement)
            await session.commit()
    
    async def get_or_create_user(self, telegram_id: int, username: str = None, 
                                first_name: str = None, last_name: str = None) -> User:
        """Получить или создать пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Создан новый пользователь: {telegram_id}")
            
            return user
    
    async def get_user_stats(self, telegram_id: int) -> dict:
        """Получить статистику пользователя"""
        async with self.async_session() as session:
            user = await session.execute(
                select(User).options(
                    selectinload(User.sessions),
                    selectinload(User.achievements)
                ).where(User.telegram_id == telegram_id)
            )
            user = user.scalar_one_or_none()
            
            if not user:
                return {}
            
            total_sessions = len(user.sessions)
            completed_sessions = len([s for s in user.sessions if s.completed])
            total_problems = sum(s.problems_solved for s in user.sessions)
            correct_answers = sum(s.correct_answers for s in user.sessions)
            accuracy = (correct_answers / total_problems * 100) if total_problems > 0 else 0
            
            return {
                "level": user.current_level,
                "total_score": user.total_score,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "total_problems": total_problems,
                "correct_answers": correct_answers,
                "accuracy": round(accuracy, 1),
                "achievements_count": len(user.achievements)
            }
    
    async def save_learning_session(self, telegram_id: int, level: int, 
                                  problems_data: list, total_time: float) -> bool:
        """Сохранить результаты сессии обучения"""
        async with self.async_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                logger.error(f"Пользователь {telegram_id} не найден")
                return False
            
            # Подсчитываем результаты
            problems_solved = len(problems_data)
            correct_answers = len([p for p in problems_data if p['is_correct']])
            accuracy = (correct_answers / problems_solved * 100) if problems_solved > 0 else 0
            
            # Создаем сессию обучения
            from datetime import datetime
            learning_session = LearningSession(
                user_id=user.id,
                level=level,
                problems_solved=problems_solved,
                correct_answers=correct_answers,
                total_time=total_time,
                completed=True,
                finished_at=datetime.utcnow()
            )
            session.add(learning_session)
            await session.flush()  # Получаем ID сессии
            
            # Сохраняем каждую задачу
            for i, problem_data in enumerate(problems_data):
                problem_text = problem_data.get('problem_text', f"Задача {i+1}")
                problem = Problem(
                    session_id=learning_session.id,
                    level=level,
                    problem_text=problem_text,
                    correct_answer=problem_data['correct_answer'],
                    user_answer=problem_data['user_answer'],
                    is_correct=problem_data['is_correct'],
                    time_taken=problem_data['time_taken'],
                    answered_at=datetime.utcnow()
                )
                session.add(problem)
            
            # Обновляем статистику пользователя
            score_gained = correct_answers * 10  # 10 очков за правильный ответ
            if accuracy >= 80:  # Бонус за хорошую точность
                score_gained += problems_solved * 5
            
            user.total_score += score_gained
            
            # Проверяем повышение уровня (80%+ точность для перехода)
            if accuracy >= 80 and level == user.current_level:
                new_level = min(level + 1, Config.MAX_LEVEL)
                if new_level > user.current_level:
                    user.current_level = new_level
                    logger.info(f"Пользователь {telegram_id} повысился до уровня {user.current_level}")
            
            # Обновляем время последней активности
            user.last_activity = datetime.utcnow()
            
            await session.commit()
            
            # Проверяем достижения
            await self.check_achievements(telegram_id)
            
            logger.info(f"Сессия сохранена: пользователь {telegram_id}, уровень {level}, "
                       f"точность {accuracy:.1f}%, очков +{score_gained}")
            return True
    
    async def check_achievements(self, telegram_id: int):
        """Проверить и выдать достижения пользователю"""
        async with self.async_session() as session:
            # Получаем пользователя с сессиями и связанными задачами
            user_result = await session.execute(
                select(User).options(
                    selectinload(User.sessions).selectinload(LearningSession.problems),
                    selectinload(User.achievements)
                ).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return []
            
            # Получаем все достижения
            achievements_result = await session.execute(select(Achievement))
            all_achievements = achievements_result.scalars().all()
            
            # Список уже полученных достижений
            earned_achievement_ids = [ua.achievement_id for ua in user.achievements]
            
            new_achievements = []
            
            for achievement in all_achievements:
                if achievement.id in earned_achievement_ids:
                    continue  # Уже получено
                
                earned = False
                
                if achievement.condition_type == "level":
                    earned = user.current_level >= achievement.condition_value
                
                elif achievement.condition_type == "total":
                    total_problems = sum(s.problems_solved for s in user.sessions)
                    earned = total_problems >= achievement.condition_value
                
                elif achievement.condition_type == "speed":
                    # Проверяем есть ли задачи решенные быстрее чем condition_value секунд
                    earned = False
                    for sess in user.sessions:
                        if sess.problems:  # Проверяем что problems загружены
                            for problem in sess.problems:
                                if problem.time_taken <= achievement.condition_value and problem.is_correct:
                                    earned = True
                                    break
                        if earned:
                            break
                
                elif achievement.condition_type == "streak":
                    # Проверяем streak правильных ответов
                    max_streak = 0
                    current_streak = 0
                    for sess in user.sessions:
                        if sess.problems:  # Проверяем что problems загружены
                            for problem in sess.problems:
                                if problem.is_correct:
                                    current_streak += 1
                                    max_streak = max(max_streak, current_streak)
                                else:
                                    current_streak = 0
                    earned = max_streak >= achievement.condition_value
                
                if earned:
                    # Выдаем достижение
                    user_achievement = UserAchievement(
                        user_id=user.id,
                        achievement_id=achievement.id
                    )
                    session.add(user_achievement)
                    new_achievements.append(achievement)
            
            if new_achievements:
                await session.commit()
                logger.info(f"Пользователь {telegram_id} получил {len(new_achievements)} новых достижений")
            
            return new_achievements
    
    async def get_user_settings(self, telegram_id: int) -> dict:
        """Получить настройки пользователя"""
        async with self.async_session() as session:
            user_result = await session.execute(
                select(User).options(selectinload(User.settings)).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {
                    "time_per_problem": Config.DEFAULT_TIME_PER_PROBLEM,
                    "problems_per_session": Config.DEFAULT_PROBLEMS_PER_SESSION,
                    "sound_enabled": True,
                    "dark_theme": False
                }
            
            if not user.settings:
                # Создаем настройки по умолчанию
                settings = UserSettings(
                    user_id=user.id,
                    time_per_problem=Config.DEFAULT_TIME_PER_PROBLEM,
                    problems_per_session=Config.DEFAULT_PROBLEMS_PER_SESSION
                )
                session.add(settings)
                await session.commit()
                await session.refresh(settings)
                
                return {
                    "time_per_problem": settings.time_per_problem,
                    "problems_per_session": settings.problems_per_session,
                    "sound_enabled": settings.sound_enabled,
                    "dark_theme": settings.dark_theme
                }
            
            return {
                "time_per_problem": user.settings.time_per_problem,
                "problems_per_session": user.settings.problems_per_session,
                "sound_enabled": user.settings.sound_enabled,
                "dark_theme": user.settings.dark_theme
            }

    async def update_user_setting(self, telegram_id: int, setting_name: str, value) -> bool:
        """Обновить настройку пользователя"""
        async with self.async_session() as session:
            user_result = await session.execute(
                select(User).options(selectinload(User.settings)).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Создаем настройки если их нет
            if not user.settings:
                settings = UserSettings(
                    user_id=user.id,
                    time_per_problem=Config.DEFAULT_TIME_PER_PROBLEM,
                    problems_per_session=Config.DEFAULT_PROBLEMS_PER_SESSION
                )
                session.add(settings)
                await session.flush()  # Получаем ID
                user.settings = settings
            
            # Обновляем настройку
            if hasattr(user.settings, setting_name):
                setattr(user.settings, setting_name, value)
                user.settings.updated_at = datetime.utcnow()
                await session.commit()
                logger.info(f"Настройка {setting_name} пользователя {telegram_id} обновлена на {value}")
                return True
            
            return False

    async def get_leaderboard(self, limit: int = 10) -> list:
        """Получить рейтинг пользователей по очкам"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User)
                .where(User.total_score > 0)
                .order_by(User.total_score.desc(), User.current_level.desc())
                .limit(limit)
            )
            users = result.scalars().all()
            
            leaderboard = []
            for i, user in enumerate(users, 1):
                leaderboard.append({
                    'position': i,
                    'name': user.first_name or user.username or f"Пользователь {user.telegram_id}",
                    'score': user.total_score,
                    'level': user.current_level,
                    'telegram_id': user.telegram_id
                })
            
            return leaderboard

    async def get_user_rank(self, telegram_id: int) -> dict:
        """Получить позицию пользователя в рейтинге"""
        async with self.async_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {'position': None, 'total_users': 0}
            
            # Считаем количество пользователей с большим счетом
            higher_score_result = await session.execute(
                select(User.id).where(
                    (User.total_score > user.total_score) | 
                    ((User.total_score == user.total_score) & (User.current_level > user.current_level))
                )
            )
            higher_count = len(higher_score_result.scalars().all())
            
            # Считаем общее количество пользователей с очками
            total_result = await session.execute(
                select(User.id).where(User.total_score > 0)
            )
            total_users = len(total_result.scalars().all())
            
            return {
                'position': higher_count + 1,
                'total_users': total_users,
                'score': user.total_score,
                'level': user.current_level
            }

    async def close(self):
        """Закрыть соединение с базой данных"""
        await self.engine.dispose()

# Глобальный экземпляр базы данных
db = Database() 