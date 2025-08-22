#!/usr/bin/env python
"""
Скрипт для автоматического развертывания SelexiaTravel на Railway
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту в sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настраиваем Django для Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
os.environ.setdefault('RAILWAY_ENVIRONMENT', 'True')
django.setup()

from django.core.management import call_command
from django.conf import settings

def check_railway_environment():
    """Проверяет настройки Railway"""
    print("🔍 Проверка Railway окружения...")
    
    # Проверяем переменные окружения
    env_vars = {
        'DATABASE_NAME': os.environ.get('DATABASE_NAME'),
        'DATABASE_USER': os.environ.get('DATABASE_USER'),
        'DATABASE_PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'DATABASE_HOST': os.environ.get('DATABASE_HOST'),
        'DATABASE_PORT': os.environ.get('DATABASE_PORT'),
        'DATABASE_ENGINE': os.environ.get('DATABASE_ENGINE'),
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
    }
    
    print("📊 Переменные окружения:")
    for key, value in env_vars.items():
        if value:
            if 'PASSWORD' in key or 'SECRET' in key:
                print(f"   ✅ {key}: {'*' * len(value)}")
            else:
                print(f"   ✅ {key}: {value}")
        else:
            print(f"   ❌ {key}: Не установлено")
    
    return all(env_vars.values())

def run_migrations():
    """Выполняет миграции базы данных"""
    print("\n🗄️ Выполнение миграций...")
    
    try:
        call_command('migrate', verbosity=2)
        print("✅ Миграции выполнены успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка миграций: {e}")
        return False

def collect_static():
    """Собирает статические файлы"""
    print("\n📦 Сбор статических файлов...")
    
    try:
        call_command('collectstatic', '--noinput', verbosity=2)
        print("✅ Статические файлы собраны успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка сбора статики: {e}")
        return False

def create_superuser():
    """Создает суперпользователя если его нет"""
    print("\n👤 Проверка суперпользователя...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Суперпользователь уже существует!")
            return True
        
        # Создаем суперпользователя
        call_command('createsuperuser', 
                    username='admin',
                    email='admin@railway.app',
                    interactive=False)
        
        # Устанавливаем пароль
        user = User.objects.get(username='admin')
        user.set_password('admin123')
        user.save()
        
        print("✅ Суперпользователь создан!")
        print("   👑 Логин: admin")
        print("   🔑 Пароль: admin123")
        print("   📧 Email: admin@railway.app")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания суперпользователя: {e}")
        return False

def check_database():
    """Проверяет подключение к базе данных"""
    print("\n🔍 Проверка базы данных...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Подключение к БД успешно!")
        print(f"   🗄️ Версия: {version[0] if version else 'Неизвестно'}")
        
        # Проверяем количество пользователей
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_count = User.objects.count()
        print(f"   👥 Пользователей: {user_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def main():
    """Основная функция"""
    print("🚂 Развертывание SelexiaTravel на Railway...")
    print("=" * 60)
    
    # Проверяем Railway окружение
    if not check_railway_environment():
        print("\n❌ Не все переменные Railway установлены!")
        print("📋 Убедитесь что в Railway установлены:")
        print("   - DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD")
        print("   - DATABASE_HOST, DATABASE_PORT")
        print("   - SECRET_KEY")
        print("   - DATABASE_ENGINE=railway")
        return False
    
    # Проверяем базу данных
    if not check_database():
        print("\n❌ Не удалось подключиться к базе данных!")
        return False
    
    # Выполняем миграции
    if not run_migrations():
        print("\n❌ Не удалось выполнить миграции!")
        return False
    
    # Собираем статические файлы
    if not collect_static():
        print("\n❌ Не удалось собрать статические файлы!")
        return False
    
    # Создаем суперпользователя
    if not create_superuser():
        print("\n❌ Не удалось создать суперпользователя!")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Развертывание на Railway завершено успешно!")
    print("\n📋 Доступные URL:")
    print("   🌐 Сайт: https://your-app.up.railway.app")
    print("   👤 Админ-панель: https://your-app.up.railway.app/admin/")
    print("   🔑 Логин: admin")
    print("   🔐 Пароль: admin123")
    
    return True

if __name__ == '__main__':
    main()
