#!/usr/bin/env python
"""
Скрипт для создания суперпользователя Django и проверки переменных окружения
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту в sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line
from django.conf import settings

User = get_user_model()

def check_env_variables():
    """Проверяет все переменные окружения из .env файла"""
    print("🔍 Проверка переменных окружения...")
    print("=" * 50)
    
    # Основные настройки Django
    env_vars = {
        'DEBUG': settings.DEBUG,
        'SECRET_KEY': settings.SECRET_KEY[:20] + '...' if len(settings.SECRET_KEY) > 20 else settings.SECRET_KEY,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'DATABASE_NAME': getattr(settings.DATABASES.get('default', {}), 'NAME', 'Не настроено'),
        'DATABASE_USER': getattr(settings.DATABASES.get('default', {}), 'USER', 'Не настроено'),
        'DATABASE_HOST': getattr(settings.DATABASES.get('default', {}), 'HOST', 'Не настроено'),
        'DATABASE_PORT': getattr(settings.DATABASES.get('default', {}), 'PORT', 'Не настроено'),
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_ROOT': settings.STATIC_ROOT,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    
    # Проверяем настройки почты
    if hasattr(settings, 'EMAIL_HOST'):
        env_vars.update({
            'EMAIL_HOST': settings.EMAIL_HOST,
            'EMAIL_PORT': settings.EMAIL_PORT,
            'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
            'EMAIL_USE_TLS': settings.EMAIL_USE_TLS,
            'EMAIL_USE_SSL': getattr(settings, 'EMAIL_USE_SSL', False),
        })
    
    # Проверяем настройки Gmail
    if hasattr(settings, 'GMAIL_CLIENT_ID'):
        env_vars.update({
            'GMAIL_CLIENT_ID': settings.GMAIL_CLIENT_ID[:20] + '...' if len(settings.GMAIL_CLIENT_ID) > 20 else settings.GMAIL_CLIENT_ID,
            'GMAIL_CLIENT_SECRET': '***' if settings.GMAIL_CLIENT_SECRET else 'Не настроено',
            'GMAIL_REFRESH_TOKEN': '***' if getattr(settings, 'GMAIL_REFRESH_TOKEN', None) else 'Не настроено',
        })
    
    # Проверяем настройки Yandex
    if hasattr(settings, 'YANDEX_CLIENT_ID'):
        env_vars.update({
            'YANDEX_CLIENT_ID': settings.YANDEX_CLIENT_ID[:20] + '...' if len(settings.YANDEX_CLIENT_ID) > 20 else settings.YANDEX_CLIENT_ID,
            'YANDEX_CLIENT_SECRET': '***' if settings.YANDEX_CLIENT_SECRET else 'Не настроено',
        })
    
    # Проверяем настройки Redis/Celery
    if hasattr(settings, 'REDIS_URL'):
        env_vars.update({
            'REDIS_URL': settings.REDIS_URL,
        })
    
    if hasattr(settings, 'CELERY_BROKER_URL'):
        env_vars.update({
            'CELERY_BROKER_URL': settings.CELERY_BROKER_URL,
        })
    
    # Выводим результаты
    for key, value in env_vars.items():
        status = "✅" if value and value != 'Не настроено' else "❌"
        print(f"{status} {key}: {value}")
    
    print("=" * 50)
    
    # Проверяем .env файл
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        print(f"📁 Файл .env найден: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
            print(f"📊 Количество переменных в .env: {len(env_lines)}")
            
            # Показываем первые несколько переменных (без значений)
            print("🔐 Примеры переменных из .env:")
            for i, line in enumerate(env_lines[:5]):
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0] if '=' in line else line.strip()
                    print(f"   {key}")
            if len(env_lines) > 5:
                print(f"   ... и еще {len(env_lines) - 5} переменных")
    else:
        print(f"❌ Файл .env не найден: {env_file}")
    
    print()

def create_superuser():
    """Создает суперпользователя если его нет"""
    print("👤 Проверка суперпользователя...")
    
    # Проверяем, есть ли уже суперпользователь
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Суперпользователь уже существует!")
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            print(f"   👑 {user.username} ({user.email}) - Суперпользователь")
        return
    
    print("❌ Суперпользователь не найден. Создаю нового...")
    
    try:
        # Создаем суперпользователя
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='1234',
            first_name='Администратор',
            last_name='Системы'
        )
        
        print(f"✅ Суперпользователь успешно создан!")
        print(f"   👑 Имя пользователя: {superuser.username}")
        print(f"   📧 Email: {superuser.email}")
        print(f"   🔑 Пароль: 1234")
        print(f"   🆔 ID: {superuser.id}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании суперпользователя: {e}")
        
        # Пробуем создать через management команду
        print("🔄 Пробую создать через management команду...")
        try:
            execute_from_command_line([
                'manage.py', 'createsuperuser',
                '--username', 'admin',
                '--email', 'admin@gmail.com',
                '--noinput'
            ])
            
            # Устанавливаем пароль
            user = User.objects.get(username='admin')
            user.set_password('1234')
            user.save()
            
            print("✅ Суперпользователь создан через management команду!")
            print(f"   👑 Имя пользователя: {user.username}")
            print(f"   📧 Email: {user.email}")
            print(f"   🔑 Пароль: 1234")
            
        except Exception as e2:
            print(f"❌ Ошибка при создании через management команду: {e2}")

def check_database():
    """Проверяет подключение к базе данных"""
    print("🗄️ Проверка базы данных...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Подключение к БД успешно!")
        print(f"   🗄️ Версия БД: {version[0] if version else 'Неизвестно'}")
        
        # Проверяем количество пользователей
        user_count = User.objects.count()
        print(f"   👥 Количество пользователей: {user_count}")
        
        # Проверяем количество суперпользователей
        superuser_count = User.objects.filter(is_superuser=True).count()
        print(f"   👑 Количество суперпользователей: {superuser_count}")
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")

def main():
    """Основная функция"""
    print("🚀 Запуск скрипта создания суперпользователя...")
    print("=" * 60)
    
    try:
        # Проверяем переменные окружения
        check_env_variables()
        
        # Проверяем базу данных
        check_database()
        
        # Создаем суперпользователя
        create_superuser()
        
        print("=" * 60)
        print("🎉 Скрипт завершен успешно!")
        
        # Показываем итоговую информацию
        print("\n📋 Итоговая информация:")
        print(f"   🌐 Проект: {BASE_DIR.name}")
        print(f"   🐍 Python: {sys.version}")
        print(f"   🎯 Django: {django.get_version()}")
        print(f"   👥 Всего пользователей: {User.objects.count()}")
        print(f"   👑 Суперпользователей: {User.objects.filter(is_superuser=True).count()}")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
