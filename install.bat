@echo off
chcp 65001 >nul
echo 🚀 Установка зависимостей SELEXIA Travel
echo ================================================

echo.
echo 📋 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python найден

echo.
echo 📋 Проверка Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js не найден! Установите Node.js 18+
    pause
    exit /b 1
)

echo ✅ Node.js найден

echo.
echo 🔧 Установка Python зависимостей...
python install_dependencies.py
if errorlevel 1 (
    echo ❌ Ошибка при установке Python зависимостей
    pause
    exit /b 1
)

echo.
echo 🔧 Установка Node.js зависимостей...
node install_node_deps.js
if errorlevel 1 (
    echo ❌ Ошибка при установке Node.js зависимостей
    pause
    exit /b 1
)

echo.
echo 🎉 Все зависимости установлены успешно!
echo.
echo 📋 Следующие шаги:
echo 1. Активируйте виртуальное окружение: selexia_env\Scripts\activate
echo 2. Выполните миграции: python manage.py migrate
echo 3. Создайте суперпользователя: python manage.py createsuperuser
echo 4. Соберите Vue.js: npm run build
echo 5. Запустите сервер: python manage.py runserver
echo.
pause
