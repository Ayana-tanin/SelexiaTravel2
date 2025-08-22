# PowerShell скрипт для настройки Railway PostgreSQL
# Запустите: .\setup_railway.ps1

Write-Host "🚀 Настройка PostgreSQL на Railway для SelexiaTravel" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Проверяем Python
Write-Host "🔍 Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не найден. Установите Python 3.8+" -ForegroundColor Red
    exit 1
}

# Проверяем pip
Write-Host "🔍 Проверка pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip найден: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip не найден. Установите pip" -ForegroundColor Red
    exit 1
}

# Устанавливаем зависимости
Write-Host "📦 Установка зависимостей..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Зависимости установлены" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка установки зависимостей" -ForegroundColor Red
    exit 1
}

# Создаем .env.railway файл
Write-Host "🔧 Создание файла .env.railway..." -ForegroundColor Yellow

$databaseUrl = Read-Host "Введите DATABASE_URL для Railway PostgreSQL (postgresql://username:password@host:port/database)"

if ($databaseUrl -eq "") {
    Write-Host "❌ DATABASE_URL не может быть пустым" -ForegroundColor Red
    exit 1
}

if (-not $databaseUrl.StartsWith("postgresql://")) {
    Write-Host "❌ DATABASE_URL должен начинаться с 'postgresql://'" -ForegroundColor Red
    exit 1
}

$envContent = @"
# Railway PostgreSQL Environment Variables
DATABASE_URL=$databaseUrl

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
"@

try {
    $envContent | Out-File -FilePath ".env.railway" -Encoding UTF8
    Write-Host "✅ Файл .env.railway создан" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка создания файла .env.railway" -ForegroundColor Red
    exit 1
}

# Устанавливаем переменные окружения
Write-Host "🔧 Установка переменных окружения..." -ForegroundColor Yellow
try {
    $env:DATABASE_URL = $databaseUrl
    Write-Host "✅ Переменная DATABASE_URL установлена" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка установки переменной окружения" -ForegroundColor Red
}

# Тестируем подключение
Write-Host "🔍 Тестирование подключения..." -ForegroundColor Yellow
try {
    python test_railway_connection.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Подключение к базе данных успешно!" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка подключения к базе данных" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ошибка тестирования подключения" -ForegroundColor Red
    exit 1
}

# Создаем таблицы
Write-Host "🗄️ Создание таблиц..." -ForegroundColor Yellow
try {
    python setup_railway_postgresql.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Таблицы созданы успешно!" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка создания таблиц" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ошибка создания таблиц" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Настройка PostgreSQL на Railway завершена успешно!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Проверьте работу приложения: python manage.py runserver" -ForegroundColor White
Write-Host "2. Создайте суперпользователя: python manage.py createsuperuser" -ForegroundColor White
Write-Host "3. Импортируйте данные: python manage.py loaddata data/*.json" -ForegroundColor White
Write-Host ""
Write-Host "📚 Подробные инструкции: RAILWAY_POSTGRESQL_SETUP.md" -ForegroundColor Cyan
