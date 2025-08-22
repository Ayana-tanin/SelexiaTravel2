#!/usr/bin/env python
"""
Упрощенный скрипт для создания суперпользователя Django
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
from django.core.management import call_command
from django.conf import settings

User = get_user_model()

def create_superuser():
    """Создает суперпользователя если его нет"""
    print("👤 Проверка суперпользователя...")
    
    # Проверяем, есть ли уже суперпользователь
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Суперпользователь уже существует!")
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            print(f"   👑 {user.username} ({user.email}) - Суперпользователь")
        return True
    
    print("❌ Суперпользователь не найден. Создаю нового...")
    
    try:
        # Создаем суперпользователя через management команду
        call_command('createsuperuser', 
                    username='admin',
                    email='admin@gmail.com',
                    interactive=False)
        
        # Устанавливаем пароль
        user = User.objects.get(username='admin')
        user.set_password('1234')
        user.save()
        
        print("✅ Суперпользователь успешно создан!")
        print(f"   👑 Имя пользователя: {user.username}")
        print(f"   📧 Email: {user.email}")
        print(f"   🔑 Пароль: 1234")
        print(f"   🆔 ID: {user.id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании суперпользователя: {e}")
        return False

def check_env_file():
    """Проверяет наличие и содержимое .env файла"""
    print("🔍 Проверка .env файла...")
    
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        print(f"✅ Файл .env найден: {env_file}")
        
        with open(env_file, 'r', encoding='utf-8') as f:
            env_lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            
        print(f"📊 Количество переменных: {len(env_lines)}")
        
        # Показываем ключи переменных
        print("🔐 Переменные окружения:")
        for line in env_lines[:10]:  # Показываем первые 10
            if '=' in line:
                key = line.split('=')[0]
                print(f"   • {key}")
        
        if len(env_lines) > 10:
            print(f"   ... и еще {len(env_lines) - 10} переменных")
            
        return True
    else:
        print(f"❌ Файл .env не найден: {env_file}")
        return False

def main():
    """Основная функция"""
    print("🚀 Создание суперпользователя Django...")
    print("=" * 50)
    
    # Проверяем .env файл
    check_env_file()
    print()
    
    # Создаем суперпользователя
    success = create_superuser()
    
    print("=" * 50)
    if success:
        print("🎉 Суперпользователь создан успешно!")
        print("\n📋 Данные для входа:")
        print("   🌐 URL: http://127.0.0.1:8000/admin/")
        print("   👤 Логин: admin")
        print("   🔑 Пароль: 1234")
        print("   📧 Email: admin@gmail.com")
    else:
        print("❌ Не удалось создать суперпользователя")
        sys.exit(1)

if __name__ == '__main__':
    main()
