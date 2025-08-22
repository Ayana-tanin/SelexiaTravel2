# PowerShell скрипт для настройки PostgreSQL на Windows
# Запускать от имени администратора

Write-Host "🚀 Настройка PostgreSQL для Selexia Travel" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Проверяем, установлен ли PostgreSQL
Write-Host "🔍 Проверка установки PostgreSQL..." -ForegroundColor Yellow

try {
    $psqlVersion = & psql --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL уже установлен: $psqlVersion" -ForegroundColor Green
    } else {
        throw "PostgreSQL не найден"
    }
} catch {
    Write-Host "❌ PostgreSQL не установлен" -ForegroundColor Red
    Write-Host "📥 Скачайте и установите PostgreSQL с официального сайта:" -ForegroundColor Yellow
    Write-Host "   https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host "   Или используйте Chocolatey: choco install postgresql" -ForegroundColor Cyan
    exit 1
}

# Проверяем, запущен ли сервис PostgreSQL
Write-Host "🔍 Проверка статуса сервиса PostgreSQL..." -ForegroundColor Yellow

$service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($service) {
    if ($service.Status -eq "Running") {
        Write-Host "✅ Сервис PostgreSQL запущен" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Сервис PostgreSQL остановлен. Запускаем..." -ForegroundColor Yellow
        Start-Service $service.Name
        Start-Sleep -Seconds 3
        if ((Get-Service $service.Name).Status -eq "Running") {
            Write-Host "✅ Сервис PostgreSQL запущен" -ForegroundColor Green
        } else {
            Write-Host "❌ Не удалось запустить сервис PostgreSQL" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "❌ Сервис PostgreSQL не найден" -ForegroundColor Red
    exit 1
}

# Создаем .env файл если его нет
Write-Host "🔍 Проверка .env файла..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "📝 Создаем .env файл..." -ForegroundColor Yellow
    
    $envContent = @"
# Django Settings
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=postgresql
DB_NAME=selexia_travel
DB_USER=selexia_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_SSL_MODE=prefer

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@selexiatravel.com

# Social Authentication
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
YANDEX_CLIENT_ID=your-yandex-client-id
YANDEX_CLIENT_SECRET=your-yandex-client-secret
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env файл создан" -ForegroundColor Green
    Write-Host "⚠️  Не забудьте изменить пароли и настройки!" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env файл уже существует" -ForegroundColor Green
}

# Инструкции по созданию базы данных
Write-Host "📋 Инструкции по созданию базы данных:" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "1. Откройте pgAdmin или используйте командную строку" -ForegroundColor White
Write-Host "2. Подключитесь к PostgreSQL как postgres пользователь" -ForegroundColor White
Write-Host "3. Выполните следующие SQL команды:" -ForegroundColor White
Write-Host "" -ForegroundColor White

$sqlCommands = @"
-- Создание пользователя
CREATE USER selexia_user WITH PASSWORD 'your_secure_password';

-- Создание базы данных
CREATE DATABASE selexia_travel OWNER selexia_user;

-- Предоставление прав
GRANT ALL PRIVILEGES ON DATABASE selexia_travel TO selexia_user;
"@

Write-Host $sqlCommands -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "4. Обновите .env файл с правильными данными" -ForegroundColor White
Write-Host "5. Запустите миграции: python manage.py migrate" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "🔧 Для проверки подключения запустите:" -ForegroundColor Yellow
Write-Host "   python check_db_connection.py" -ForegroundColor Cyan

Write-Host "" -ForegroundColor White
Write-Host "🎉 Настройка завершена!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
