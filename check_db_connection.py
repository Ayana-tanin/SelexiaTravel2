#!/usr/bin/env python
"""
Скрипт для создания всех таблиц в базе данных PostgreSQL для SelexiaTravel
Использует Django ORM для создания таблиц на основе моделей
"""

import os
import sys
import django
from pathlib import Path
from django.core.management import execute_from_command_line
from django.db import connection, transaction
from django.conf import settings

# Добавляем корневую директорию проекта в Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
django.setup()

def check_database_connection():
    """Проверяет подключение к базе данных"""
    print("🔍 Проверка подключения к базе данных...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Подключение к PostgreSQL успешно!")
            print(f"   🗄️ Версия: {version[0]}")
            
            # Проверяем текущую базу данных
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"   📊 База данных: {db_name[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        print("\n🔧 Возможные решения:")
        print("   1. Проверьте правильность DATABASE_URL в .env файле")
        print("   2. Убедитесь, что PostgreSQL запущен и доступен")
        print("   3. Проверьте сетевое подключение к Railway")
        return False

def check_existing_tables():
    """Проверяет существующие таблицы в базе данных"""
    print("\n🔍 Проверка существующих таблиц...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"📋 Найдено существующих таблиц: {len(tables)}")
                for table in tables:
                    print(f"   • {table[0]}")
                return [table[0] for table in tables]
            else:
                print("📋 Таблицы не найдены - база данных пустая")
                return []
                
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {e}")
        return []

def create_migrations():
    """Создает миграции для всех приложений"""
    print("\n📝 Создание миграций...")
    
    try:
        # Создаем миграции для основного приложения
        print("   🔄 Создание миграций для selexia_travel...")
        execute_from_command_line(['manage.py', 'makemigrations', 'selexia_travel', '--verbosity=2'])
        
        # Создаем миграции для встроенных приложений Django
        print("   🔄 Создание миграций для Django приложений...")
        execute_from_command_line(['manage.py', 'makemigrations', '--verbosity=1'])
        
        print("✅ Миграции созданы успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании миграций: {e}")
        return False

def apply_migrations():
    """Применяет миграции к базе данных"""
    print("\n🗄️ Применение миграций к базе данных...")
    
    try:
        # Сначала применяем миграции Django (contenttypes, auth, etc.)
        print("   🔄 Применение базовых миграций Django...")
        execute_from_command_line(['manage.py', 'migrate', 'contenttypes', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'auth', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'sessions', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'messages', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'staticfiles', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'admin', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'sites', '--verbosity=2'])
        
        # Применяем миграции для allauth
        print("   🔄 Применение миграций django-allauth...")
        execute_from_command_line(['manage.py', 'migrate', 'account', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'socialaccount', '--verbosity=2'])
        
        # Применяем миграции нашего приложения
        print("   🔄 Применение миграций selexia_travel...")
        execute_from_command_line(['manage.py', 'migrate', 'selexia_travel', '--verbosity=2'])
        
        # Применяем остальные миграции
        print("   🔄 Применение всех оставшихся миграций...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        
        print("✅ Все миграции применены успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении миграций: {e}")
        return False

def verify_tables_created():
    """Проверяет созданные таблицы"""
    print("\n🔍 Проверка созданных таблиц...")
    
    try:
        with connection.cursor() as cursor:
            # Получаем все таблицы
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"📊 Всего таблиц создано: {len(tables)}")
            
            # Группируем таблицы по категориям
            django_tables = []
            allauth_tables = []
            selexia_tables = []
            other_tables = []
            
            for table in tables:
                table_name = table[0]
                if table_name.startswith('django_'):
                    django_tables.append(table_name)
                elif table_name.startswith(('account_', 'socialaccount_')):
                    allauth_tables.append(table_name)
                elif table_name.startswith('selexia_travel_'):
                    selexia_tables.append(table_name)
                else:
                    other_tables.append(table_name)
            
            print(f"\n📋 Django системные таблицы ({len(django_tables)}):")
            for table in django_tables:
                print(f"   • {table}")
            
            print(f"\n👤 Django Allauth таблицы ({len(allauth_tables)}):")
            for table in allauth_tables:
                print(f"   • {table}")
            
            print(f"\n🏢 SelexiaTravel таблицы ({len(selexia_tables)}):")
            for table in selexia_tables:
                print(f"   • {table}")
            
            if other_tables:
                print(f"\n📦 Другие таблицы ({len(other_tables)}):")
                for table in other_tables:
                    print(f"   • {table}")
            
            # Проверяем ключевые таблицы нашего приложения
            expected_selexia_tables = [
                'selexia_travel_user',
                'selexia_travel_country',
                'selexia_travel_city', 
                'selexia_travel_category',
                'selexia_travel_excursion',
                'selexia_travel_excursionimage',
                'selexia_travel_booking',
                'selexia_travel_review',
                'selexia_travel_reviewimage',
                'selexia_travel_favorite',
                'selexia_travel_application',
                'selexia_travel_usersettings'
            ]
            
            missing_tables = []
            for expected_table in expected_selexia_tables:
                if expected_table not in selexia_tables:
                    missing_tables.append(expected_table)
            
            if missing_tables:
                print(f"\n⚠️ Отсутствующие таблицы ({len(missing_tables)}):")
                for table in missing_tables:
                    print(f"   • {table}")
                return False
            else:
                print(f"\n✅ Все ключевые таблицы SelexiaTravel созданы!")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {e}")
        return False

def create_superuser():
    """Создает суперпользователя если его нет"""
    print("\n👑 Проверка суперпользователя...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Проверяем, есть ли уже суперпользователи
        if User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.filter(is_superuser=True).first()
            print(f"✅ Суперпользователь уже существует: {superuser.email}")
            return True
        
        # Создаем суперпользователя с данными по умолчанию
        print("🔄 Создание суперпользователя...")
        
        superuser = User.objects.create_superuser(
            email='admin@selexiatravel.com',
            password='admin123',
            username='admin',
            first_name='Admin',
            last_name='User'
        )
        
        print("✅ Суперпользователь создан успешно!")
        print("   📧 Email: admin@selexiatravel.com")
        print("   🔑 Пароль: admin123")
        print("   ⚠️ ОБЯЗАТЕЛЬНО смените пароль после первого входа!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании суперпользователя: {e}")
        return False

def create_sample_data():
    """Создает базовые тестовые данные"""
    print("\n📊 Создание базовых данных...")
    
    try:
        from selexia_travel.models import Country, City, Category
        
        # Создаем страны
        countries_data = [
            {'name_ru': 'Россия', 'name_en': 'Russia', 'iso_code': 'RU', 'is_popular': True},
            {'name_ru': 'Турция', 'name_en': 'Turkey', 'iso_code': 'TR', 'is_popular': True},
            {'name_ru': 'Египет', 'name_en': 'Egypt', 'iso_code': 'EG', 'is_popular': True},
            {'name_ru': 'Таиланд', 'name_en': 'Thailand', 'iso_code': 'TH', 'is_popular': True},
            {'name_ru': 'Греция', 'name_en': 'Greece', 'iso_code': 'GR', 'is_popular': False},
        ]
        
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                iso_code=country_data['iso_code'],
                defaults=country_data
            )
            if created:
                print(f"   ✅ Создана страна: {country.name_ru}")
        
        # Создаем города
        cities_data = [
            {'name_ru': 'Москва', 'name_en': 'Moscow', 'country_code': 'RU', 'is_popular': True},
            {'name_ru': 'Санкт-Петербург', 'name_en': 'Saint Petersburg', 'country_code': 'RU', 'is_popular': True},
            {'name_ru': 'Стамбул', 'name_en': 'Istanbul', 'country_code': 'TR', 'is_popular': True},
            {'name_ru': 'Анталья', 'name_en': 'Antalya', 'country_code': 'TR', 'is_popular': True},
            {'name_ru': 'Каир', 'name_en': 'Cairo', 'country_code': 'EG', 'is_popular': True},
            {'name_ru': 'Бангкок', 'name_en': 'Bangkok', 'country_code': 'TH', 'is_popular': True},
            {'name_ru': 'Афины', 'name_en': 'Athens', 'country_code': 'GR', 'is_popular': True},
        ]
        
        for city_data in cities_data:
            try:
                country = Country.objects.get(iso_code=city_data['country_code'])
                city, created = City.objects.get_or_create(
                    name_ru=city_data['name_ru'],
                    country=country,
                    defaults={
                        'name_en': city_data['name_en'],
                        'is_popular': city_data['is_popular']
                    }
                )
                if created:
                    print(f"   ✅ Создан город: {city.name_ru}")
            except Country.DoesNotExist:
                print(f"   ⚠️ Страна с кодом {city_data['country_code']} не найдена")
        
        # Создаем категории
        categories_data = [
            {'name_ru': 'Обзорные экскурсии', 'name_en': 'City Tours', 'icon': 'fas fa-city', 'color': '#007bff', 'is_featured': True},
            {'name_ru': 'Музеи и галереи', 'name_en': 'Museums & Galleries', 'icon': 'fas fa-university', 'color': '#28a745', 'is_featured': True},
            {'name_ru': 'Природа и парки', 'name_en': 'Nature & Parks', 'icon': 'fas fa-tree', 'color': '#20c997', 'is_featured': True},
            {'name_ru': 'Гастрономические туры', 'name_en': 'Food Tours', 'icon': 'fas fa-utensils', 'color': '#fd7e14', 'is_featured': True},
            {'name_ru': 'Приключения', 'name_en': 'Adventures', 'icon': 'fas fa-mountain', 'color': '#dc3545', 'is_featured': False},
            {'name_ru': 'Культура и история', 'name_en': 'Culture & History', 'icon': 'fas fa-landmark', 'color': '#6f42c1', 'is_featured': False},
        ]
        
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name_ru=category_data['name_ru'],
                defaults=category_data
            )
            if created:
                print(f"   ✅ Создана категория: {category.name_ru}")
        
        print("✅ Базовые данные созданы успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании базовых данных: {e}")
        return False

def show_summary():
    """Показывает итоговую информацию"""
    print("\n" + "=" * 60)
    print("🎉 СОЗДАНИЕ ТАБЛИЦ ЗАВЕРШЕНО УСПЕШНО!")
    print("=" * 60)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """)
            total_tables = cursor.fetchone()[0]
        
        print(f"📊 Общее количество таблиц: {total_tables}")
        
        # Показываем информацию о пользователях
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        print(f"👥 Пользователей в системе: {total_users}")
        print(f"👑 Суперпользователей: {superusers}")
        
        # Показываем информацию о данных
        from selexia_travel.models import Country, City, Category
        
        countries_count = Country.objects.count()
        cities_count = City.objects.count()
        categories_count = Category.objects.count()
        
        print(f"🌍 Стран: {countries_count}")
        print(f"🏙️ Городов: {cities_count}")
        print(f"📂 Категорий: {categories_count}")
        
    except Exception as e:
        print(f"⚠️ Не удалось получить статистику: {e}")
    
    print("\n📋 Следующие шаги:")
    print("1. 🚀 Запустите сервер: python manage.py runserver")
    print("2. 🔐 Войдите в админку: http://127.0.0.1:8000/admin/")
    print("3. 📊 Добавьте контент через админку или API")
    print("4. 🎨 Настройте фронтенд (Vue.js)")
    print("\n🔒 Данные для входа в админку:")
    print("   Email: admin@selexiatravel.com")
    print("   Пароль: admin123")
    print("   ⚠️ ОБЯЗАТЕЛЬНО смените пароль!")

def main():
    """Основная функция"""
    print("🚀 СОЗДАНИЕ ТАБЛИЦ БАЗЫ ДАННЫХ SELEXIATRAVEL")
    print("=" * 60)
    
    # 1. Проверяем подключение к БД
    if not check_database_connection():
        print("\n❌ Не удалось подключиться к базе данных")
        print("Проверьте настройки DATABASE_URL в .env файле")
        return False
    
    # 2. Проверяем существующие таблицы
    existing_tables = check_existing_tables()
    
    # 3. Создаем миграции
    if not create_migrations():
        print("\n❌ Не удалось создать миграции")
        return False
    
    # 4. Применяем миграции
    if not apply_migrations():
        print("\n❌ Не удалось применить миграции")
        return False
    
    # 5. Проверяем созданные таблицы
    if not verify_tables_created():
        print("\n⚠️ Не все таблицы созданы корректно")
    
    # 6. Создаем суперпользователя
    create_superuser()
    
    # 7. Создаем базовые данные
    create_sample_data()
    
    # 8. Показываем итоги
    show_summary()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Операция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)