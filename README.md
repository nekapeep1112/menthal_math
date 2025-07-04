# 🧮 Telegram Бот для Ментальной Арифметики

Красивый и функциональный Telegram бот для обучения ментальной арифметике с прогрессивной системой уровней, достижениями и подробной статистикой.

## ✨ Особенности

- 🎯 **10 уровней сложности** - от простых задач до экспертного уровня
- ⚡ **Интерактивные задачи** - быстрые вычисления с ограничением времени
- 🏆 **Система достижений** - мотивация через награды
- 📊 **Подробная статистика** - отслеживание прогресса
- 🎨 **Красивый интерфейс** - современные клавиатуры и эмодзи
- 💾 **База данных** - сохранение прогресса пользователей
- 🔄 **Адаптивная сложность** - задачи подстраиваются под уровень

## 🎮 Уровни обучения

| Уровень | Сложность | Описание |
|---------|-----------|----------|
| 🟢 1-2 | Легкий | Простое сложение/вычитание (1-10) |
| 🟡 3-5 | Средний | Большие числа и тройные суммы |
| 🟠 6-8 | Сложный | Смешанные операции и умножение |
| 🔴 9-10 | Эксперт | Сложные выражения и мастер-уровень |

## 🚀 Быстрый запуск

### 1. Клонирование репозитория
\`\`\`bash
git clone https://github.com/nekapeep1112/menthal_math.git
\`\`\`

### 2. Установка зависимостей
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Настройка окружения
Создайте файл `.env` на основе `.env.example`:
\`\`\`bash
cp .env.example .env
\`\`\`

Заполните переменные окружения:
\`\`\`env
BOT_TOKEN=ваш_токен_бота_от_BotFather
ADMIN_ID=ваш_telegram_id
DATABASE_URL=sqlite+aiosqlite:///mental_math_bot.db
DEBUG=True
\`\`\`

### 4. Запуск бота
\`\`\`bash
python main.py
\`\`\`

## 🔧 Получение токена бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Получите токен и добавьте в `.env`

## 📁 Структура проекта

\`\`\`
📦 parserbotkege/
├── 📁 database/
│   ├── __init__.py
│   ├── models.py          # Модели SQLAlchemy
│   └── database.py        # Работа с БД
├── 📁 handlers/
│   ├── __init__.py
│   ├── basic_handlers.py  # Основные команды
│   └── learning_handlers.py # Обучение и задачи
├── 📁 keyboards/
│   ├── __init__.py
│   └── main_keyboard.py   # Клавиатуры бота
├── 📁 utils/
│   ├── __init__.py
│   ├── math_generator.py  # Генератор задач
│   └── formatters.py      # Форматирование сообщений
├── config.py              # Конфигурация
├── main.py               # Точка входа
├── requirements.txt      # Зависимости
└── README.md            # Документация
\`\`\`

## 🎯 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота и регистрация |
| `/help` | Справка по использованию |
| `🧮 Начать обучение` | Выбор уровня и начало тренировки |
| `📊 Моя статистика` | Просмотр прогресса |
| `🏆 Достижения` | Список полученных наград |
| `⚙️ Настройки` | Персонализация бота |

## 🏗️ Архитектура

### База данных
- **SQLAlchemy ORM** с поддержкой async/await
- **SQLite** для локального хранения
- Модели: User, LearningSession, Problem, Achievement

### Состояния FSM
- `solving_problem` - Решение задачи
- `waiting_custom_answer` - Ожидание ввода ответа

### Клавиатуры
- **ReplyKeyboard** для главного меню
- **InlineKeyboard** для интерактивных действий
- Адаптивные кнопки в зависимости от контекста

## 🎨 Дизайн и UX

- **Современные эмодзи** для визуальной привлекательности
- **Прогресс-бары** для отслеживания выполнения
- **Цветовая индикация** сложности уровней
- **Мотивационные сообщения** по результатам
- **Быстрые ответы** через inline-кнопки

## 📊 Система достижений

| Достижение | Условие | Награда |
|------------|---------|---------|
| 🎯 Новичок | Первая решенная задача | Мотивация |
| 📚 Ученик | Достижение 3 уровня | Прогресс |
| 🧠 Эксперт | Достижение 5 уровня | Признание |
| 🏆 Мастер | Достижение 7 уровня | Уважение |
| 👑 Гений | Достижение 10 уровня | Слава |
| ⚡ Скорость | Решение за 5 секунд | Быстрота |
| 🎯 Точность | 10 правильных подряд | Аккуратность |

## ⚙️ Конфигурация

### Настройки обучения
- `MAX_LEVEL = 10` - Максимальный уровень
- `PROBLEMS_PER_LEVEL = 5` - Задач на уровень
- `TIME_LIMIT_SECONDS = 30` - Время на задачу

### Параметры базы данных
- Автоматическое создание таблиц
- Миграции при изменении моделей
- Backup и восстановление

## 🔧 Разработка

### Добавление нового уровня
1. Обновите `level_configs` в `math_generator.py`
2. Добавьте описание в `get_level_description`
3. Протестируйте генерацию задач

### Создание нового достижения
1. Добавьте в `create_default_achievements`
2. Реализуйте логику проверки
3. Добавьте уведомление пользователю

## 🐛 Отладка

### Логирование
- Файл `mental_math_bot.log` содержит подробные логи
- Уровень `INFO` для основных событий
- Уровень `ERROR` для ошибок

### Частые проблемы
1. **Неверный токен** - проверьте `.env`
2. **База данных заблокирована** - перезапустите бота
3. **Ошибки импорта** - установите зависимости

## 📈 Статистика и аналитика

- Общее количество пользователей
- Средняя точность по уровням
- Время решения задач
- Популярные уровни

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - используйте свободно для личных и коммерческих проектов.

## 🆘 Поддержка

Если у вас возникли вопросы или проблемы:
1. Проверьте этот README
2. Посмотрите логи бота
3. Создайте Issue в репозитории

---

<div align="center">
Made with ❤️ and 🧮 for mental math enthusiasts!
</div> 