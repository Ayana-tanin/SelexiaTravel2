#!/usr/bin/env python
"""
Скрипт для импорта данных в PostgreSQL на Railway
Запускайте: python import_data.py
"""

import os
import sys
import django
import json
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настраиваем Django для Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
os.environ.setdefault('RAILWAY_ENVIRONMENT', 'True')
django.setup()

from django.contrib.auth import get_user_model
from selexia_travel.models import Country, City, Excursion, Review, Booking, UserSettings
from django.core.management import call_command
from django.db import transaction

def import_model_data(model_class, filename):
    """Импортирует данные модели из JSON файла"""
    try:
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print(f"⚠️ {model_class.__name__}: Файл пуст")
            return False
        
        # Импортируем данные
        imported_count = 0
        for item in data:
            try:
                # Создаем объект
                fields = item['fields']
                obj = model_class(**fields)
                obj.save()
                imported_count += 1
            except Exception as e:
                print(f"   ⚠️ Ошибка импорта записи: {e}")
                continue
        
        print(f"✅ {model_class.__name__}: {imported_count} записей импортировано")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта {model_class.__name__}: {e}")
        return False

def import_users():
    """Импортирует пользователей"""
    try:
        filename = 'data/users.json'
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print(f"⚠️ Users: Файл пуст")
            return False
        
        User = get_user_model()
        imported_count = 0
        
        for item in data:
            try:
                fields = item['fields']
                
                # Создаем пользователя
                user = User(
                    username=fields.get('username', f"user_{imported_count}"),
                    email=fields.get('email', f"user{imported_count}@example.com"),
                    first_name=fields.get('first_name', ''),
                    last_name=fields.get('last_name', ''),
                    is_active=fields.get('is_active', True),
                    is_staff=fields.get('is_staff', False),
                    is_superuser=fields.get('is_superuser', False),
                )
                
                # Устанавливаем пароль по умолчанию
                user.set_password('password123')
                user.save()
                
                imported_count += 1
                
            except Exception as e:
                print(f"   ⚠️ Ошибка импорта пользователя: {e}")
                continue
        
        print(f"✅ Users: {imported_count} пользователей импортировано")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта Users: {e}")
        return False

def create_sample_data():
    """Создает образцы данных если нет файлов для импорта"""
    print("📝 Создание образцов данных...")
    
    try:
        # Создаем страны
        countries_data = [
            {'name_ru': 'Греция', 'name_en': 'Greece', 'description_ru': 'Древняя страна с богатой историей', 'is_popular': True},
            {'name_ru': 'Италия', 'name_en': 'Italy', 'description_ru': 'Страна искусства и культуры', 'is_popular': True},
            {'name_ru': 'Испания', 'name_en': 'Spain', 'description_ru': 'Страна фламенко и корриды', 'is_popular': True},
            {'name_ru': 'Турция', 'name_en': 'Turkey', 'description_ru': 'Мост между Европой и Азией', 'is_popular': True},
            {'name_ru': 'Египет', 'name_en': 'Egypt', 'description_ru': 'Страна пирамид и фараонов', 'is_popular': True},
        ]
        
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                name_ru=country_data['name_ru'],
                defaults=country_data
            )
            if created:
                print(f"   ✅ Создана страна: {country.name_ru}")
        
        # Создаем города
        cities_data = [
            {'name_ru': 'Афины', 'name_en': 'Athens', 'country': Country.objects.get(name_ru='Греция'), 'is_popular': True},
            {'name_ru': 'Рим', 'name_en': 'Rome', 'country': Country.objects.get(name_ru='Италия'), 'is_popular': True},
            {'name_ru': 'Барселона', 'name_en': 'Barcelona', 'country': Country.objects.get(name_ru='Испания'), 'is_popular': True},
            {'name_ru': 'Стамбул', 'name_en': 'Istanbul', 'country': Country.objects.get(name_ru='Турция'), 'is_popular': True},
            {'name_ru': 'Каир', 'name_en': 'Cairo', 'country': Country.objects.get(name_ru='Египет'), 'is_popular': True},
        ]
        
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name_ru=city_data['name_ru'],
                defaults=city_data
            )
            if created:
                print(f"   ✅ Создан город: {city.name_ru}")
        
        print("✅ Образцы данных созданы")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания образцов данных: {e}")
        return False

def main():
    """Основная функция импорта"""
    print("🚂 Импорт данных в Railway PostgreSQL...")
    print("=" * 60)
    
    # Проверяем подключение к БД
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Подключение к PostgreSQL: {version[0] if version else 'Неизвестно'}")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False
    
    # Применяем миграции
    print("\n🔄 Применение миграций...")
    try:
        call_command('migrate', verbosity=1)
        print("✅ Миграции применены")
    except Exception as e:
        print(f"❌ Ошибка миграций: {e}")
        return False
    
    # Проверяем наличие файлов данных
    data_folder = 'data'
    if os.path.exists(data_folder) and os.listdir(data_folder):
        print(f"\n📁 Найдены файлы данных в папке '{data_folder}'")
        
        # Импортируем данные
        models_to_import = [
            (Country, 'data/countries.json'),
            (City, 'data/cities.json'),
            (Excursion, 'data/excursions.json'),
            (Review, 'data/reviews.json'),
            (Booking, 'data/bookings.json'),
            (UserSettings, 'data/user_settings.json'),
        ]
        
        imported_count = 0
        for model_class, filename in models_to_import:
            if import_model_data(model_class, filename):
                imported_count += 1
        
        # Импортируем пользователей
        if import_users():
            imported_count += 1
        
        print(f"\n🎉 Импорт завершен! Импортировано {imported_count} типов данных.")
        
    else:
        print(f"\n📝 Файлы данных не найдены, создаем образцы...")
        create_sample_data()
    
    # Создаем суперпользователя
    print("\n👤 Создание суперпользователя...")
    try:
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@railway.app',
                password='admin123'
            )
            print(f"✅ Суперпользователь создан: {user.username}")
        else:
            print("✅ Суперпользователь уже существует")
    except Exception as e:
        print(f"❌ Ошибка создания суперпользователя: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Импорт данных завершен!")
    print("\n📋 Доступные данные:")
    print(f"   🌍 Страны: {Country.objects.count()}")
    print(f"   🏙️ Города: {City.objects.count()}")
    print(f"   🎯 Экскурсии: {Excursion.objects.count()}")
    print(f"   👥 Пользователи: {User.objects.count()}")
    print(f"   ⭐ Отзывы: {Review.objects.count()}")
    print(f"   📅 Бронирования: {Booking.objects.count()}")
    
    return True

if __name__ == '__main__':
    main()
