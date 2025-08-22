#!/usr/bin/env python3
"""
Скрипт для установки зависимостей SELEXIA Travel
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} завершено успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при {description.lower()}:")
        print(f"Команда: {command}")
        print(f"Ошибка: {e.stderr}")
        return False

def main():
    print("🚀 Установка зависимостей SELEXIA Travel")
    print("=" * 50)
    
    # Проверяем Python версию
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Требуется Python 3.8+")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Создаем виртуальное окружение если его нет
    venv_path = "selexia_env"
    if not os.path.exists(venv_path):
        print(f"\n🔧 Создание виртуального окружения {venv_path}...")
        if not run_command(f"python -m venv {venv_path}", "Создание виртуального окружения"):
            sys.exit(1)
    
    # Активируем виртуальное окружение
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_path, "Scripts", "activate")
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:  # Linux/Mac
        activate_script = os.path.join(venv_path, "bin", "activate")
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # Обновляем pip
    if not run_command(f"{pip_path} install --upgrade pip", "Обновление pip"):
        sys.exit(1)
    
    # Устанавливаем зависимости
    if not run_command(f"{pip_path} install -r requirements.txt", "Установка Python зависимостей"):
        sys.exit(1)
    
    print("\n🎉 Python зависимости установлены успешно!")
    print("\n📋 Следующие шаги:")
    print("1. Активируйте виртуальное окружение:")
    if os.name == 'nt':
        print(f"   {venv_path}\\Scripts\\activate")
    else:
        print(f"   source {venv_path}/bin/activate")
    print("2. Выполните миграции: python manage.py migrate")
    print("3. Создайте суперпользователя: python manage.py createsuperuser")
    print("4. Запустите сервер: python manage.py runserver")

if __name__ == "__main__":
    main()
