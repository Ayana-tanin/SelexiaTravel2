#!/bin/bash

echo "🚀 Настройка PostgreSQL на Railway для SelexiaTravel"
echo "============================================================"

# Проверяем Python
echo "🔍 Проверка Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3 найден: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python найден: $(python --version)"
else
    echo "❌ Python не найден. Установите Python 3.8+"
    exit 1
fi

# Проверяем pip
echo "🔍 Проверка pip..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    echo "✅ pip3 найден: $(pip3 --version)"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    echo "✅ pip найден: $(pip --version)"
else
    echo "❌ pip не найден. Установите pip"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
$PIP_CMD install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены"
else
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

# Создаем .env.railway файл
echo "🔧 Создание файла .env.railway..."

read -p "Введите DATABASE_URL для Railway PostgreSQL (postgresql://username:password@host:port/database): " database_url

if [ -z "$database_url" ]; then
    echo "❌ DATABASE_URL не может быть пустым"
    exit 1
fi

if [[ ! $database_url == postgresql://* ]]; then
    echo "❌ DATABASE_URL должен начинаться с 'postgresql://'"
    exit 1
fi

cat > .env.railway << EOF
# Railway PostgreSQL Environment Variables
DATABASE_URL=$database_url

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
EOF

if [ $? -eq 0 ]; then
    echo "✅ Файл .env.railway создан"
else
    echo "❌ Ошибка создания файла .env.railway"
    exit 1
fi

# Устанавливаем переменные окружения
echo "🔧 Установка переменных окружения..."
export DATABASE_URL="$database_url"
echo "✅ Переменная DATABASE_URL установлена"

# Тестируем подключение
echo "🔍 Тестирование подключения..."
$PYTHON_CMD test_railway_connection.py
if [ $? -eq 0 ]; then
    echo "✅ Подключение к базе данных успешно!"
else
    echo "❌ Ошибка подключения к базе данных"
    exit 1
fi

# Создаем таблицы
echo "🗄️ Создание таблиц..."
$PYTHON_CMD setup_railway_postgresql.py
if [ $? -eq 0 ]; then
    echo "✅ Таблицы созданы успешно!"
else
    echo "❌ Ошибка создания таблиц"
    exit 1
fi

echo "🎉 Настройка PostgreSQL на Railway завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Проверьте работу приложения: $PYTHON_CMD manage.py runserver"
echo "2. Создайте суперпользователя: $PYTHON_CMD manage.py createsuperuser"
echo "3. Импортируйте данные: $PYTHON_CMD manage.py loaddata data/*.json"
echo ""
echo "📚 Подробные инструкции: RAILWAY_POSTGRESQL_SETUP.md"

# Делаем скрипт исполняемым
chmod +x setup_railway.sh
