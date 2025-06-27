from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Модель пользователя бота"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    current_level = Column(Integer, default=1)
    total_score = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("LearningSession", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

class LearningSession(Base):
    """Модель сессии обучения"""
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    level = Column(Integer, nullable=False)
    problems_solved = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_time = Column(Float, default=0.0)  # в секундах
    completed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="sessions")
    problems = relationship("Problem", back_populates="session")

class Problem(Base):
    """Модель задачи"""
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    level = Column(Integer, nullable=False)
    problem_text = Column(String(500), nullable=False)
    correct_answer = Column(Integer, nullable=False)
    user_answer = Column(Integer, nullable=True)
    is_correct = Column(Boolean, default=False)
    time_taken = Column(Float, default=0.0)  # в секундах
    created_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)
    
    # Связи
    session = relationship("LearningSession", back_populates="problems")

class Achievement(Base):
    """Модель достижений"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(500), nullable=False)
    icon = Column(String(10), default="🏆")
    condition_type = Column(String(50), nullable=False)  # level, streak, speed, accuracy
    condition_value = Column(Integer, nullable=False)
    
    # Связи
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    """Модель достижений пользователя"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class UserSettings(Base):
    """Модель настроек пользователя"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    time_per_problem = Column(Integer, default=30)  # секунд на задачу
    problems_per_session = Column(Integer, default=5)  # количество задач в сессии
    sound_enabled = Column(Boolean, default=True)
    dark_theme = Column(Boolean, default=False)
    difficulty_modifier = Column(Float, default=1.0)  # модификатор сложности
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="settings") 