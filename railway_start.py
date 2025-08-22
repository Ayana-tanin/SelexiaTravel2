#!/usr/bin/env python3
"""
Скрипт для запуска Django приложения на Railway
Включает проверки окружения и обработку ошибок
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Проверяет критические переменные окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют критические переменные: {', '.join(missing_vars)}")
        return False
    
    print("✅ Все критические переменные установлены")
    return True

def check_database():
    """Проверяет подключение к базе данных"""
    print("🔍 Проверка подключения к базе данных...")
    
    try:
        result = subprocess.run([
            sys.executable, 'check_db_connection.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ База данных доступна")
            return True
        else:
            print(f"❌ Ошибка подключения к БД: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут проверки базы данных")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        return False

def run_migrations():
    """Запускает миграции базы данных"""
    print("🔄 Применение миграций...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--noinput'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Миграции применены успешно")
            return True
        else:
            print(f"❌ Ошибка миграций: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут миграций")
        return False
    except Exception as e:
        print(f"❌ Ошибка миграций: {e}")
        return False

def collect_static():
    """Собирает статические файлы"""
    print("📦 Сбор статических файлов...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Статические файлы собраны")
            return True
        else:
            print(f"⚠️ Предупреждение при сборе статики: {result.stderr}")
            return True  # Не критично
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут сбора статики")
        return True
    except Exception as e:
        print(f"⚠️ Ошибка сбора статики: {e}")
        return True

def start_gunicorn():
    """Запускает Gunicorn сервер"""
    print("🚀 Запуск Gunicorn сервера...")
    
    # Получаем порт из переменной окружения
    port = os.environ.get('PORT', '8000')
    
    # Команда для запуска Gunicorn
    cmd = [
        'gunicorn',
        'selexia_travel.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '120',
        '--keep-alive', '5',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info'
    ]
    
    print(f"🌐 Сервер будет доступен на порту {port}")
    print(f"🔧 Команда запуска: {' '.join(cmd)}")
    
    try:
        # Запускаем Gunicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn завершился с ошибкой: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️ Сервер остановлен пользователем")
        return True
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🚂 ЗАПУСК SELEXIATRAVEL НА RAILWAY")
    print("=" * 50)
    
    # 1. Проверяем окружение
    if not check_environment():
        print("❌ Критические проблемы с окружением")
        sys.exit(1)
    
    # 2. Проверяем базу данных
    if not check_database():
        print("❌ Проблемы с базой данных")
        sys.exit(1)
    
    # 3. Применяем миграции
    if not run_migrations():
        print("❌ Ошибка миграций")
        sys.exit(1)
    
    # 4. Собираем статические файлы
    collect_static()
    
    # 5. Запускаем сервер
    print("\n🎉 Все проверки пройдены! Запускаем сервер...")
    print("=" * 50)
    
    if not start_gunicorn():
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
