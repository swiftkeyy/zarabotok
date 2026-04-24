# 💼 Бот "Календарь Заработка" — SQLite версия для bothost.ru

## ✅ Как данные сохраняются без PostgreSQL

База данных сохраняется в папке **`/app/data/bot_data.db`**

Эта папка на bothost.ru **не удаляется** после перезапуска (в отличие от обычных файлов).

---

## 🗄️ Миграции базы данных

Проект использует **Alembic** для управления схемой базы данных.

### Быстрый старт с миграциями

```bash
# Применить все миграции
python migrate.py upgrade

# Откатить последнюю миграцию
python migrate.py downgrade

# Посмотреть текущую версию БД
python migrate.py current

# Создать новую миграцию
python migrate.py create add_new_table
```

Подробнее см. [MIGRATIONS.md](MIGRATIONS.md)

---

## 🚀 Пошаговый деплой на bothost.ru

### 1. Создай проект
- Зайди на [bothost.ru](https://bothost.ru)
- Создай новый проект (Python + aiogram)

### 2. Загрузи файлы
Загрузи в корень проекта:
- `main.py`
- `requirements.txt`
- `migrate.py` (опционально, для миграций)
- `alembic/` (папка с миграциями)
- `alembic.ini` (конфигурация Alembic)
- `work-earn-miniapp.html` → в папку `miniapp/`

### 3. Настрой переменные окружения

В панели проекта → **Переменные окружения** добавь:

```env
BOT_TOKEN=твой_токен
ADMIN_IDS=123456789,987654321
WEBAPP_URL=https://твой-бот.bothost.ru/miniapp/work-earn-miniapp.html
```

### 4. Установи зависимости

В терминале проекта выполни:

```bash
pip install -r requirements.txt
```

### 5. Примени миграции (опционально)

Если у тебя уже есть база данных с таблицами, пропусти этот шаг.

Для новой базы данных:
```bash
python migrate.py upgrade
```

Для существующей базы данных:
```bash
python migrate.py stamp
```

### 6. Запусти бота

```bash
python main.py
```

Готово!

---

## Важные моменты

- База автоматически создаётся в `/app/data/`
- Все данные (пользователи, статистика, каналы) сохраняются после перезапуска
- Не нужно подключать PostgreSQL
- Миграции работают как с PostgreSQL (Railway), так и с SQLite (bothost.ru)

---

**Теперь бот полностью готов к работе на bothost.ru без внешней базы!** 🎉

Если что-то не работает — пиши, помогу.