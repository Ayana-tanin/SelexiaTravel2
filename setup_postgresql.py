#!/usr/bin/env python
"""
Скрипт для настройки PostgreSQL базы данных для проекта SelexiaTravel
"""

import os
import sys
import subprocess
from pathlib import Path

def check_postgresql_installed():
    """Проверяет, установлен ли PostgreSQL"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL установлен: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL не найден в PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL не установлен")
        return False

def create_database_and_user():
    """Создает базу данных и пользователя"""
    print("\n🗄️ Создание базы данных и пользователя...")
    
    # Параметры подключения
    DB_NAME = "selexia_travel_db"
    DB_USER = "selexia_user"
    DB_PASSWORD = "selexia_password"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    try:
        # Создаем пользователя
        print(f"👤 Создание пользователя {DB_USER}...")
        create_user_cmd = [
            'psql', '-U', 'postgres', '-h', DB_HOST, '-p', DB_PORT,
            '-c', f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';"
        ]
        
        result = subprocess.run(create_user_cmd, capture_output=True, text=True)
        if result.returncode == 0 or "already exists" in result.stderr:
            print(f"✅ Пользователь {DB_USER} создан или уже существует")
        else:
            print(f"⚠️ Предупреждение при создании пользователя: {result.stderr}")
        
        # Создаем базу данных
        print(f"🗄️ Создание базы данных {DB_NAME}...")
        create_db_cmd = [
            'psql', '-U', 'postgres', '-h', DB_HOST, '-p', DB_PORT,
            '-c', f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};"
        ]
        
        result = subprocess.run(create_db_cmd, capture_output=True, text=True)
        if result.returncode == 0 or "already exists" in result.stderr:
            print(f"✅ База данных {DB_NAME} создана или уже существует")
        else:
            print(f"⚠️ Предупреждение при создании БД: {result.stderr}")
        
        # Предоставляем права
        print(f"🔐 Настройка прав доступа...")
        grant_cmd = [
            'psql', '-U', 'postgres', '-h', DB_HOST, '-p', DB_PORT,
            '-d', DB_NAME, '-c', f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};"
        ]
        
        result = subprocess.run(grant_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Права доступа настроены")
        else:
            print(f"⚠️ Предупреждение при настройке прав: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании БД: {e}")
        return False

def test_connection():
    """Тестирует подключение к базе данных"""
    print("\n🔍 Тестирование подключения к PostgreSQL...")
    
    try:
        # Тестируем подключение
        test_cmd = [
            'psql', '-U', 'selexia_user', '-h', 'localhost', '-p', '5432',
            '-d', 'selexia_travel_db', '-c', 'SELECT version();'
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Подключение к PostgreSQL успешно!")
            print(f"   🗄️ Версия: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Ошибка подключения: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def create_env_file():
    """Создает .env файл с настройками PostgreSQL"""
    print("\n📝 Создание .env файла...")
    
    env_content = """# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,selexiatravel.com,www.selexiatravel.com

# Database - PostgreSQL
DATABASE_URL=postgresql://selexia_user:selexia_password@localhost:5432/selexia_travel_db
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=selexia_travel_db
DATABASE_USER=selexia_user
DATABASE_PASSWORD=selexia_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=selexiatravelauth@gmail.com
EMAIL_HOST_PASSWORD=afjs pirk rdtg tqyw
DEFAULT_FROM_EMAIL=selexiatravelauth@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

BOOKING_NOTIFICATION_EMAIL=selexiatravelauth@gmail.com

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

# Gmail API настройки
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Site Settings
SITE_ID=1

# Redis/Celery (раскомментировать при необходимости)
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0

# AWS S3 (раскомментировать при необходимости)
# AWS_ACCESS_KEY_ID=your-aws-access-key
# AWS_SECRET_ACCESS_KEY=your-aws-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=your-region
# AWS_S3_CUSTOM_DOMAIN=your-domain
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Файл .env создан с настройками PostgreSQL")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания .env файла: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Настройка PostgreSQL для проекта SelexiaTravel...")
    print("=" * 60)
    
    # Проверяем PostgreSQL
    if not check_postgresql_installed():
        print("\n❌ PostgreSQL не установлен!")
        print("📋 Инструкции по установке:")
        print("   Windows: https://www.postgresql.org/download/windows/")
        print("   Linux: sudo apt-get install postgresql postgresql-contrib")
        print("   macOS: brew install postgresql")
        return False
    
    # Создаем БД и пользователя
    if not create_database_and_user():
        print("\n❌ Не удалось создать базу данных!")
        return False
    
    # Тестируем подключение
    if not test_connection():
        print("\n❌ Не удалось подключиться к базе данных!")
        return False
    
    # Создаем .env файл
    if not create_env_file():
        print("\n❌ Не удалось создать .env файл!")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 PostgreSQL успешно настроен!")
    print("\n📋 Следующие шаги:")
    print("1. 🔄 Перезапустите Django сервер")
    print("2. 🗄️ Выполните миграции: python manage.py migrate")
    print("3. 👤 Создайте суперпользователя: python create_admin.py")
    print("4. 🌐 Откройте админ-панель: http://127.0.0.1:8000/admin/")
    
    print("\n🔐 Данные для подключения:")
    print("   🗄️ База данных: selexia_travel_db")
    print("   👤 Пользователь: selexia_user")
    print("   🔑 Пароль: selexia_password")
    print("   🌐 Хост: localhost")
    print("   🔌 Порт: 5432")
    
    return True

if __name__ == '__main__':
    main()
