# 🚂 Деплой на Railway

## ✅ Что готово

- ✅ HTML Mini App с Telegram WebApp SDK
- ✅ Функция `sendStatsToBot()` для отправки данных в бот
- ✅ Поддержка PostgreSQL для Railway
- ✅ Fallback на SQLite для bothost.ru

---

## 🚀 Пошаговый деплой

### 1. Создай проект на Railway

1. Откройте https://railway.app
2. Войдите через GitHub
3. Нажмите **"New Project"**
4. Выберите **"Deploy from GitHub repo"**
5. Выберите ваш репозиторий

### 2. Добавьте PostgreSQL

1. В проекте нажмите **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway создаст базу данных
3. Переменная `DATABASE_URL` добавится автоматически

### 3. Настройте переменные окружения

В настройках сервиса добавьте:

```env
BOT_TOKEN=ваш-токен-от-botfather
ADMIN_IDS=ваш_telegram_id,другой_admin_id
WEBAPP_URL=https://ваш-проект.up.railway.app/miniapp/work-earn-miniapp.html
```

**ВАЖНО**: 
- `BOT_TOKEN` - получите у @BotFather
- `ADMIN_IDS` - ваши Telegram ID через запятую (узнать можно у @userinfobot)
- `WEBAPP_URL` - URL вашего Mini App (см. шаг 5)

### 4. Настройте Start Command

В Railway Dashboard:
- Settings → Deploy → Start Command:
  ```bash
  python main.py
  ```

### 5. Получите URL проекта

1. Settings → Networking → Generate Domain
2. Скопируйте URL (например: `https://calendar-bot-production.up.railway.app`)
3. Обновите `WEBAPP_URL`:
   ```
   WEBAPP_URL=https://calendar-bot-production.up.railway.app/miniapp/work-earn-miniapp.html
   ```

### 6. Настройте Telegram Mini App

1. Откройте @BotFather в Telegram
2. Отправьте `/newapp`
3. Выберите вашего бота
4. Введите название: **Календарь Заработка**
5. Введите описание: **Трекер рабочих дней и заработка**
6. Загрузите иконку (640x360 px)
7. Введите URL: `https://calendar-bot-production.up.railway.app/miniapp/work-earn-miniapp.html`

### 7. Настройте кнопку меню

1. Отправьте `/mybots` в @BotFather
2. Выберите вашего бота
3. Выберите **"Bot Settings"** → **"Menu Button"**
4. Введите URL: `https://calendar-bot-production.up.railway.app/miniapp/work-earn-miniapp.html`

---

## 🧪 Тестирование

### Проверьте бота
1. Откройте вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку "📅 Открыть календарь"
4. Должно открыться Mini App

### Проверьте отправку данных
1. В Mini App отметьте несколько рабочих дней
2. Нажмите "📤 Отправить статистику в бот"
3. Бот должен ответить "✅ Статистика сохранена!"

---

## 📊 Как работает

### База данных
- **Railway**: Автоматически использует PostgreSQL (через `DATABASE_URL`)
- **bothost.ru**: Использует SQLite (`/app/data/bot_data.db`)

### Mini App
- Данные хранятся локально в браузере (localStorage)
- Кнопка "📤 Отправить статистику в бот" отправляет данные через Telegram WebApp API
- Бот сохраняет статистику в базу данных

### Уведомления
- **Ежемесячное напоминание**: 1 числа в 10:00 (МСК)
- **Личные напоминания**: Каждое воскресенье в 18:00 (если не сохранял 30+ дней)
- **Еженедельный отчёт**: Каждый понедельник в 9:00 (только админам)

---

## 🔧 Troubleshooting

### Бот не запускается
1. Проверьте логи: Dashboard → Deployments → Logs
2. Убедитесь, что `BOT_TOKEN` правильный
3. Проверьте, что PostgreSQL подключен

### Mini App не открывается
1. Проверьте `WEBAPP_URL` в переменных
2. Убедитесь, что URL правильный (должен заканчиваться на `.html`)
3. Проверьте, что файл `miniapp/work-earn-miniapp.html` существует

### Статистика не отправляется
1. Откройте DevTools → Console в браузере
2. Проверьте ошибки JavaScript
3. Убедитесь, что Telegram WebApp SDK загружен

### База данных пустая
1. Проверьте, что PostgreSQL подключен
2. Проверьте логи на ошибки миграций
3. Убедитесь, что `DATABASE_URL` установлен

---

## 💰 Стоимость

**Railway Hobby Plan:**
- $5/месяц
- 500 часов выполнения
- PostgreSQL включен

---

## 🆘 Поддержка

Если что-то не работает:
1. Проверьте логи в Railway Dashboard
2. Убедитесь, что все переменные окружения установлены
3. Проверьте, что PostgreSQL подключен

---

Made with ❤️ by Kiro AI
