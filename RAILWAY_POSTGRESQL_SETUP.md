# 🚀 Настройка PostgreSQL на Railway для SelexiaTravel

Этот документ содержит пошаговые инструкции по подключению проекта SelexiaTravel к PostgreSQL базе данных на платформе Railway.

## 📋 Предварительные требования

1. **Аккаунт на Railway** - [railway.app](https://railway.app)
2. **Установленный Python 3.8+** и Django
3. **Установленные зависимости** из `requirements.txt`

## 🔧 Шаг 1: Создание PostgreSQL базы данных на Railway

### 1.1 Войдите в Railway Dashboard
- Откройте [railway.app](https://railway.app)
- Войдите в свой аккаунт

### 1.2 Создайте новый проект
- Нажмите "New Project"
- Выберите "Deploy from GitHub repo" или "Start from scratch"

### 1.3 Добавьте PostgreSQL базу данных
- В проекте нажмите "New"
- Выберите "Database" → "PostgreSQL"
- Дождитесь создания базы данных

### 1.4 Получите DATABASE_URL
- В созданной базе данных нажмите "Connect"
- Скопируйте `DATABASE_URL` (формат: `postgresql://username:password@host:port/database`)

## 🔧 Шаг 2: Настройка переменных окружения

### 2.1 Автоматическая настройка (рекомендуется)
```bash
python setup_railway_env.py
```
Следуйте инструкциям и введите ваш `DATABASE_URL`.

### 2.2 Ручная настройка
Создайте файл `.env.railway` с содержимым:
```bash
# Railway PostgreSQL Environment Variables
DATABASE_URL=postgresql://username:password@host:port/database

# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,*.railway.app

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=selexiatravelauth@gmail.com
EMAIL_HOST_PASSWORD=afjs pirk rdtg tqyw
DEFAULT_FROM_EMAIL=selexiatravelauth@gmail.com

BOOKING_NOTIFICATION_EMAIL=selexiatravelauth@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Social Auth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

VK_CLIENT_ID=your-vk-client-id
VK_CLIENT_SECRET=your-vk-client-secret

YANDEX_CLIENT_ID=your-yandex-client-id
YANDEX_CLIENT_SECRET=your-yandex-client-secret

APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret
APPLE_KEY=your-apple-key

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

# Site Settings
SITE_ID=1
```

## 🔧 Шаг 3: Загрузка переменных в Railway

### 3.1 Через Railway CLI
```bash
# Установите Railway CLI
npm install -g @railway/cli

# Войдите в Railway
railway login

# Загрузите переменные окружения
cat .env.railway | railway variables
```

### 3.2 Через веб-интерфейс
- В Railway Dashboard перейдите в ваш проект
- Нажмите "Variables"
- Добавьте каждую переменную из `.env.railway`

## 🔧 Шаг 4: Создание таблиц и настройка базы данных

### 4.1 Автоматическая настройка
```bash
python setup_railway_postgresql.py
```

Этот скрипт:
- ✅ Проверит подключение к PostgreSQL
- ✅ Создаст все таблицы через миграции Django
- ✅ Создаст суперпользователя
- ✅ Соберет статические файлы

### 4.2 Ручная настройка
```bash
# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic --noinput
```

## 🔧 Шаг 5: Проверка работы

### 5.1 Тест подключения
```bash
python manage.py dbshell
```
В PostgreSQL shell выполните:
```sql
SELECT version();
\dt
\q
```

### 5.2 Запуск сервера
```bash
python manage.py runserver
```

### 5.3 Проверка админ-панели
- Откройте `http://localhost:8000/admin/`
- Войдите с учетными данными суперпользователя

## 🔧 Шаг 6: Импорт данных (опционально)

Если у вас есть данные для импорта:
```bash
# Импорт всех данных
python manage.py loaddata data/*.json

# Или отдельных файлов
python manage.py loaddata data/countries.json
python manage.py loaddata data/cities.json
python manage.py loaddata data/excursions.json
```

## 🚨 Устранение неполадок

### Ошибка подключения к базе данных
```
django.db.utils.OperationalError: could not connect to server
```
**Решение:**
1. Проверьте правильность `DATABASE_URL`
2. Убедитесь, что база данных запущена на Railway
3. Проверьте настройки брандмауэра

### Ошибка аутентификации
```
django.db.utils.OperationalError: FATAL: password authentication failed
```
**Решение:**
1. Проверьте правильность пароля в `DATABASE_URL`
2. Убедитесь, что пользователь имеет права доступа

### Ошибка миграций
```
django.db.utils.ProgrammingError: relation "table_name" already exists
```
**Решение:**
1. Сбросьте миграции: `python manage.py migrate --fake-initial`
2. Или удалите таблицы и пересоздайте их

## 📊 Структура созданных таблиц

После успешной настройки в базе данных будут созданы следующие таблицы:

### Основные таблицы
- `auth_user` - Пользователи системы
- `auth_group` - Группы пользователей
- `auth_permission` - Права доступа
- `django_content_type` - Типы контента
- `django_migrations` - История миграций
- `django_session` - Сессии пользователей
- `django_site` - Настройки сайта

### Таблицы приложения
- `selexia_travel_user` - Расширенная модель пользователя
- `selexia_travel_country` - Страны
- `selexia_travel_city` - Города
- `selexia_travel_category` - Категории экскурсий
- `selexia_travel_excursion` - Экскурсии
- `selexia_travel_booking` - Бронирования
- `selexia_travel_review` - Отзывы
- `selexia_travel_favorite` - Избранное
- `selexia_travel_usersettings` - Настройки пользователей

## 🔐 Безопасность

### Рекомендации по безопасности
1. **Измените SECRET_KEY** на уникальное значение
2. **Используйте HTTPS** в продакшене
3. **Ограничьте доступ** к базе данных
4. **Регулярно обновляйте** зависимости

### Переменные для продакшена
```bash
DEBUG=False
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. **Проверьте логи** Django и Railway
2. **Обратитесь к документации** Django и Railway
3. **Создайте issue** в репозитории проекта

## 🎯 Следующие шаги

После успешной настройки PostgreSQL:

1. **Настройте Gmail интеграцию** - см. `GMAIL_INTEGRATION_README.md`
2. **Настройте социальную аутентификацию** - см. `GOOGLE_OAUTH_SETUP.md`
3. **Разверните на Railway** - см. `RAILWAY_DEPLOYMENT.md`
4. **Оптимизируйте производительность** - см. `OPTIMIZATION_README.md`

---

**Удачи в настройке! 🚀**
